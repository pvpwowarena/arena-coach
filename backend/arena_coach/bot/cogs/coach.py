"""Discord cog: /coach pause | resume.

Phase 2: заглушка под Phase 4 realtime-подсказки.
В Phase 4 эти команды будут управлять bridge-демоном и WebSocket-стримом.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, ClassVar

import discord
from discord import app_commands
from discord.ext import commands

from arena_coach.access.models import Role
from arena_coach.bot.checks import whitelist_required

if TYPE_CHECKING:
    from arena_coach.bot.client import ArenaCoachBot

logger = logging.getLogger(__name__)


class CoachCog(commands.Cog, name="coach"):
    """Управление realtime-коучем (Phase 4)."""

    def __init__(self, bot: ArenaCoachBot) -> None:
        self.bot = bot
        # Phase 4: будет True/False per-player через Dict[discord_id, bool]
        self._paused: dict[str, bool] = {}

    coach_group = app_commands.Group(
        name="coach",
        description="Управление realtime-коучем (Phase 4)",
    )

    @coach_group.command(name="pause", description="Приостановить realtime-подсказки")
    @whitelist_required(Role.PLAYER)
    async def coach_pause(self, interaction: discord.Interaction) -> None:
        user_id = str(interaction.user.id)
        self._paused[user_id] = True

        embed = discord.Embed(
            title="⏸️  Коуч на паузе",
            description=(
                "Realtime-подсказки приостановлены.\n"
                "*(Phase 4 — функция будет полноценной после деплоя bridge)*"
            ),
            color=discord.Color.orange(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @coach_group.command(name="resume", description="Возобновить realtime-подсказки")
    @whitelist_required(Role.PLAYER)
    async def coach_resume(self, interaction: discord.Interaction) -> None:
        user_id = str(interaction.user.id)
        self._paused[user_id] = False

        embed = discord.Embed(
            title="▶️  Коуч активен",
            description=(
                "Realtime-подсказки возобновлены.\n"
                "*(Phase 4 — функция будет полноценной после деплоя bridge)*"
            ),
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ── Phase 4.5: голосовые подсказки ───────────────────────────────────

    _VOICE_MODE_LABELS: ClassVar[dict[str, str]] = {
        "on": "🔊 текст + голос",
        "off": "🔇 только текст",
        "only": "🎧 только голос (без text-spam)",
    }

    @coach_group.command(
        name="voice",
        description="Голосовые подсказки: on = текст+голос, off = только текст, only = только голос",
    )
    @app_commands.describe(mode="Режим голосовых подсказок")
    @app_commands.choices(
        mode=[
            app_commands.Choice(name="on — текст + голос (default)", value="on"),
            app_commands.Choice(name="off — только текст", value="off"),
            app_commands.Choice(name="only — только голос", value="only"),
        ]
    )
    @whitelist_required(Role.PLAYER)
    async def coach_voice(self, interaction: discord.Interaction, mode: str) -> None:
        await self.bot.player_settings.set_voice_mode(str(interaction.user.id), mode)

        voice_configured = bool(self.bot.settings.discord_voice_channel_id)
        note = (
            ""
            if voice_configured
            else "\n⚠️ Voice-канал на сервере пока не настроен — режим сохранён и заработает после настройки."
        )
        embed = discord.Embed(
            title="🎙 Режим голосовых подсказок обновлён",
            description=f"Твой режим: **{self._VOICE_MODE_LABELS.get(mode, mode)}**{note}",
            color=discord.Color.blurple(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    def is_paused(self, discord_id: str) -> bool:
        """Phase 4 использует этот метод перед отправкой hint'а."""
        return self._paused.get(discord_id, False)


async def setup(bot: ArenaCoachBot) -> None:  # type: ignore[override]
    await bot.add_cog(CoachCog(bot))
