"""Discord cog: /glossary <term>, /list_comps, /source <slug>.

Данные для glossary берутся из kb/glossary/abilities.json и kb/glossary/terms.md.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from arena_coach.access.models import Role
from arena_coach.bot.checks import whitelist_required
from arena_coach.kb.render import render_glossary_embed

if TYPE_CHECKING:
    from arena_coach.bot.client import ArenaCoachBot

logger = logging.getLogger(__name__)

_MAX_COMPS_PER_FIELD = 20


def _load_glossary(kb_path: Path) -> dict[str, dict[str, object]]:
    """Загрузить abilities.json из kb/glossary/."""
    abilities_file = kb_path / "glossary" / "abilities.json"
    if not abilities_file.exists():
        return {}
    try:
        data: dict[str, dict[str, object]] = json.loads(abilities_file.read_text(encoding="utf-8"))
        return data
    except Exception as exc:
        logger.warning("Failed to load abilities.json: %s", exc)
        return {}


class GlossaryCog(commands.Cog, name="glossary"):
    """Команды /glossary, /list_comps, /source."""

    def __init__(self, bot: ArenaCoachBot) -> None:
        self.bot = bot
        self._glossary: dict[str, dict[str, object]] = {}
        self._glossary_loaded = False

    def _ensure_glossary(self) -> None:
        if not self._glossary_loaded:
            from arena_coach.shared.settings import settings

            self._glossary = _load_glossary(settings.kb_path)
            self._glossary_loaded = True

    # ── /glossary ────────────────────────────────────────────────────────

    @app_commands.command(
        name="glossary",
        description="Расшифровка термина или способности (DR, premed, shatter, и т.д.)",
    )
    @app_commands.describe(term="Термин или название способности")
    @whitelist_required(Role.VIEWER)
    async def glossary(
        self,
        interaction: discord.Interaction,
        term: str,
    ) -> None:
        self._ensure_glossary()

        # Ищем сначала точное совпадение, потом case-insensitive
        key = term.lower().strip()
        definition = self._glossary.get(key) or self._glossary.get(term)

        if definition is None:
            # Ищем частичное совпадение
            matches = [k for k in self._glossary if key in k.lower()]
            if matches:
                match_list = ", ".join(f"`{m}`" for m in matches[:10])
                await interaction.response.send_message(
                    f"❓ Термин `{term}` не найден. Похожие: {match_list}",
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    f"❓ Термин `{term}` не найден в глоссарии.",
                    ephemeral=True,
                )
            return

        embed = render_glossary_embed(key, definition)
        await interaction.response.send_message(embed=embed)

    # ── /list_comps ──────────────────────────────────────────────────────

    @app_commands.command(
        name="list_comps",
        description="Все составы и матчапы в базе знаний",
    )
    @whitelist_required(Role.VIEWER)
    async def list_comps(self, interaction: discord.Interaction) -> None:
        matchups = self.bot.kb_retriever.list_all_matchups()

        if not matchups:
            await interaction.response.send_message(
                "📭 KB пуста. Матчапы пока не добавлены.",
                ephemeral=True,
            )
            return

        # Группируем по нашему составу
        grouped: dict[str, list[str]] = {}
        for comp, vs in matchups:
            grouped.setdefault(comp, []).append(vs)

        embed = discord.Embed(
            title="📚  Матчапы в KB",
            description=f"Всего документов: **{len(matchups)}**",
            color=discord.Color.blurple(),
        )

        for comp in sorted(grouped):
            vs_list = sorted(grouped[comp])
            value = "\n".join(f"vs `{v}`" for v in vs_list[:_MAX_COMPS_PER_FIELD])
            if len(vs_list) > _MAX_COMPS_PER_FIELD:
                value += f"\n*...и ещё {len(vs_list) - _MAX_COMPS_PER_FIELD}*"
            embed.add_field(name=f"🗡 {comp}", value=value, inline=True)

        await interaction.response.send_message(embed=embed)

    # ── /source ──────────────────────────────────────────────────────────

    @app_commands.command(
        name="source",
        description="Источники для матчапа по slug",
    )
    @app_commands.describe(slug="Slug матчапа, например: rm-vs-warrior-rdruid")
    @whitelist_required(Role.VIEWER)
    async def source(
        self,
        interaction: discord.Interaction,
        slug: str,
    ) -> None:
        doc = self.bot.kb_retriever.find_by_slug(slug)

        if doc is None:
            await interaction.response.send_message(
                f"❓ Матчап со slug `{slug}` не найден в KB.\n"
                f"Используй `/list_comps` чтобы увидеть доступные slug'и.",
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title=f"📚  Источники: {doc.slug}",
            description=f"**{doc.composition}** vs **{doc.vs}**",
            color=discord.Color.blurple(),
        )

        for i, src in enumerate(doc.sources, 1):
            src_type = getattr(src, "type", "unknown")
            if src_type in ("web", "youtube"):
                url = getattr(src, "url", "?")
                title = getattr(src, "title", None) or url
                ts = getattr(src, "t", None)
                value = f"[{title}]({url})"
                if ts:
                    value += f" (t={ts})"
            elif src_type == "stream-paste":
                author = getattr(src, "author", "?")
                platform = getattr(src, "platform", "?") or "?"
                recorded = getattr(src, "recorded", None)
                value = f"{platform} — {author}"
                if recorded:
                    value += f" ({recorded})"
            elif src_type == "file":
                path = getattr(src, "path", "?")
                author = getattr(src, "author", None) or "?"
                value = f"`{path}` (by {author})"
            else:
                value = str(src)

            embed.add_field(name=f"Источник {i} [{src_type}]", value=value, inline=False)

        embed.set_footer(
            text=f"last_reviewed: {doc.last_reviewed} | confidence: {doc.confidence.value}"
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot: ArenaCoachBot) -> None:  # type: ignore[override]
    await bot.add_cog(GlossaryCog(bot))
