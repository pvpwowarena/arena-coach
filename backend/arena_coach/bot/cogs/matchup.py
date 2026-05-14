"""Discord cog: /matchup our:<comp> vs:<comp> и /opener <comp> <comp>.

Lookup идёт через KBRetriever. Если матчапа нет → ephemeral «нет в KB» + suggestions.
Бот никогда не выдумывает совет — только из KB.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from arena_coach.access.models import Role
from arena_coach.bot.checks import whitelist_required
from arena_coach.kb.render import render_matchup_embed, render_no_matchup_embed

if TYPE_CHECKING:
    from arena_coach.bot.client import ArenaCoachBot

logger = logging.getLogger(__name__)


class MatchupCog(commands.Cog, name="matchup"):
    """Команды /matchup и /opener."""

    def __init__(self, bot: ArenaCoachBot) -> None:
        self.bot = bot

    # ── /matchup ─────────────────────────────────────────────────────────

    @app_commands.command(
        name="matchup",
        description="Стратегия на матчап: опенер, ротация, cooldown'ы",
    )
    @app_commands.describe(
        our="Наш состав, например: rogue+mage",
        vs="Их состав, например: warrior+resto-druid",
    )
    @whitelist_required(Role.VIEWER)
    async def matchup(
        self,
        interaction: discord.Interaction,
        our: str,
        vs: str,
    ) -> None:
        doc = self.bot.kb_retriever.find_matchup(our, vs)

        if doc is None:
            suggestions = self.bot.kb_retriever.suggest_similar(our, vs)
            embed = render_no_matchup_embed(our, vs, suggestions)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = render_matchup_embed(doc, mode="full")
        await interaction.response.send_message(embed=embed)

    # ── /opener ──────────────────────────────────────────────────────────

    @app_commands.command(
        name="opener",
        description="Только опенер для матчапа (коротко)",
    )
    @app_commands.describe(
        our="Наш состав, например: rogue+mage",
        vs="Их состав, например: warrior+resto-druid",
    )
    @whitelist_required(Role.VIEWER)
    async def opener(
        self,
        interaction: discord.Interaction,
        our: str,
        vs: str,
    ) -> None:
        doc = self.bot.kb_retriever.find_matchup(our, vs)

        if doc is None:
            suggestions = self.bot.kb_retriever.suggest_similar(our, vs)
            embed = render_no_matchup_embed(our, vs, suggestions)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = render_matchup_embed(doc, mode="opener")
        await interaction.response.send_message(embed=embed)


async def setup(bot: ArenaCoachBot) -> None:  # type: ignore[override]
    await bot.add_cog(MatchupCog(bot))
