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
    from arena_coach.access.usage import UsageSummary
    from arena_coach.bot.client import ArenaCoachBot

logger = logging.getLogger(__name__)


# Ориентировочная цена $/1M токенов (вход, выход). Тарифы Anthropic меняются —
# это ОЦЕНКА для админ-панели; точный счёт — в биллинге Anthropic.
_PRICE_PER_MTOK: dict[str, tuple[float, float]] = {
    "opus": (15.0, 75.0),
    "sonnet": (3.0, 15.0),
    "haiku": (1.0, 5.0),
}


def _fmt_tokens(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)


def _est_cost_usd(model: str, in_tok: int, out_tok: int) -> float | None:
    low = model.lower()
    for key, (pin, pout) in _PRICE_PER_MTOK.items():
        if key in low:
            return in_tok / 1_000_000 * pin + out_tok / 1_000_000 * pout
    return None


def _stats_embed(all_time: UsageSummary, week: UsageSummary) -> discord.Embed:
    """Собрать админ-embed расхода токенов: разбивка по назначению/модели + итоги."""
    embed = discord.Embed(title="📊 Расход токенов LLM", color=discord.Color.teal())
    if not all_time.buckets:
        embed.description = (
            "Пока ноль — модель ещё не вызывалась.\n"
            "LLM включается при заданном `ANTHROPIC_API_KEY` и работает на разборе "
            "незнакомых сетапов и постматче (в бою — детерминированно, без токенов)."
        )
        return embed

    lines: list[str] = []
    total_cost = 0.0
    cost_known = False
    for b in all_time.buckets[:10]:
        cost = _est_cost_usd(b.model, b.input_tokens, b.output_tokens)
        cost_str = ""
        if cost is not None:
            total_cost += cost
            cost_known = True
            cost_str = f" · ≈${cost:.2f}"
        lines.append(
            f"**{b.purpose}** · `{b.model}`\n"
            f"  {_fmt_tokens(b.input_tokens)} in + {_fmt_tokens(b.output_tokens)} out "
            f"= {_fmt_tokens(b.total_tokens)} · {b.calls} выз.{cost_str}"
        )
    embed.description = "\n".join(lines)

    total = (
        f"{_fmt_tokens(all_time.input_tokens)} in + {_fmt_tokens(all_time.output_tokens)} out "
        f"= {_fmt_tokens(all_time.total_tokens)} · {all_time.calls} вызовов"
    )
    if cost_known:
        total += f"\n≈ ${total_cost:.2f} (оценка, сверь актуальный тариф Anthropic)"
    embed.add_field(name="Итого (всё время)", value=total, inline=False)
    embed.add_field(
        name="За 7 дней",
        value=(
            f"{_fmt_tokens(week.total_tokens)} токенов · {week.calls} вызовов"
            if week.buckets
            else "нет вызовов"
        ),
        inline=False,
    )
    embed.set_footer(text="Модели задаются в api.env: ANTHROPIC_MODEL_SYNTH / _CLASSIFY")
    return embed


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

    # ── Phase 4.7: статистика расхода токенов (для админа) ────────────────

    @coach_group.command(
        name="stats",
        description="Расход токенов LLM: сколько и куда (только админ)",
    )
    @whitelist_required(Role.ADMIN)
    async def coach_stats(self, interaction: discord.Interaction) -> None:
        svc = getattr(self.bot, "usage_service", None)
        if svc is None:
            await interaction.response.send_message(
                "Учёт токенов недоступен (usage_service не инициализирован).", ephemeral=True
            )
            return
        all_time = await svc.summary()
        week = await svc.summary(days=7)
        await interaction.response.send_message(embed=_stats_embed(all_time, week), ephemeral=True)

    def is_paused(self, discord_id: str) -> bool:
        """Phase 4 использует этот метод перед отправкой hint'а."""
        return self._paused.get(discord_id, False)


async def setup(bot: ArenaCoachBot) -> None:  # type: ignore[override]
    await bot.add_cog(CoachCog(bot))
