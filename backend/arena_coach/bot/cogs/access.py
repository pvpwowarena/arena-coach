"""Discord cog: /access add | remove | list | audit.

Только admin-role. Команды изменяют whitelist через AccessService.
Все операции пишутся в audit log.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from arena_coach.access.audit import read_recent_entries
from arena_coach.access.models import Role
from arena_coach.bot.checks import whitelist_required

if TYPE_CHECKING:
    from arena_coach.bot.client import ArenaCoachBot

logger = logging.getLogger(__name__)

# Максимальное число записей в /access list embed
_MAX_LIST_ROWS = 15

# Максимальное число audit-строк в /access audit embed
_MAX_AUDIT_ROWS = 20


class AccessCog(commands.Cog, name="access"):
    """Управление доступом (whitelist). Только для admin."""

    def __init__(self, bot: ArenaCoachBot) -> None:
        self.bot = bot

    access_group = app_commands.Group(
        name="access",
        description="Управление whitelist'ом арена-коуча",
    )

    # ── /access add ──────────────────────────────────────────────────────

    @access_group.command(name="add", description="Добавить игрока в whitelist")
    @app_commands.describe(
        user="Discord-пользователь",
        role="Роль: viewer | player | admin",
        character="Имя персонажа (точно как в игре)",
        realm="Реалм (например: Gorefiend)",
    )
    @whitelist_required(Role.ADMIN)
    async def access_add(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        role: str,
        character: str,
        realm: str,
    ) -> None:
        # Валидация роли
        try:
            role_enum = Role(role.lower())
        except ValueError:
            await interaction.response.send_message(
                f"❌ Неизвестная роль `{role}`. Допустимые: `viewer`, `player`, `admin`.",
                ephemeral=True,
            )
            return

        await self.bot.access_service.add_entry(
            discord_id=str(user.id),
            character=character,
            realm=realm,
            role=role_enum,
            added_by=str(interaction.user.id),
        )

        embed = discord.Embed(
            title="✅  Доступ добавлен",
            description=f"{user.mention} добавлен в whitelist.",
            color=discord.Color.green(),
        )
        embed.add_field(name="Роль", value=f"`{role_enum.value}`", inline=True)
        embed.add_field(name="Персонаж", value=f"`{character}@{realm}`", inline=True)
        embed.set_footer(text=f"Добавил: {interaction.user}")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ── /access remove ───────────────────────────────────────────────────

    @access_group.command(name="remove", description="Убрать игрока из whitelist")
    @app_commands.describe(user="Discord-пользователь")
    @whitelist_required(Role.ADMIN)
    async def access_remove(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
    ) -> None:
        removed = await self.bot.access_service.remove_entry(
            discord_id=str(user.id),
            actor=str(interaction.user.id),
        )

        if removed:
            embed = discord.Embed(
                title="🗑️  Доступ отозван",
                description=f"{user.mention} удалён из whitelist.",
                color=discord.Color.orange(),
            )
        else:
            embed = discord.Embed(
                title="⚠️  Не найден",
                description=(
                    f"{user.mention} не найден в активном whitelist, "
                    "или является владельцем (нельзя удалить)."
                ),
                color=discord.Color.red(),
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ── /access list ─────────────────────────────────────────────────────

    @access_group.command(name="list", description="Список игроков в whitelist")
    @whitelist_required(Role.ADMIN)
    async def access_list(self, interaction: discord.Interaction) -> None:
        entries = await self.bot.access_service.list_entries()

        embed = discord.Embed(
            title="📋  Whitelist",
            description=f"Активных записей: **{len(entries)}**",
            color=discord.Color.blurple(),
        )

        rows: list[str] = []
        for entry in entries[:_MAX_LIST_ROWS]:
            try:
                char = self.bot.access_service.decrypt_character(entry)
                realm = self.bot.access_service.decrypt_realm(entry)
                char_str = f"`{char}@{realm}`"
            except Exception:
                char_str = "*(ошибка расшифровки)*"

            # Пытаемся получить упоминание пользователя
            member = (
                interaction.guild.get_member(int(entry.discord_id)) if interaction.guild else None
            )
            user_str = member.mention if member else f"`{entry.discord_id}`"

            rows.append(f"{user_str} — {char_str} — `{entry.role.value}`")

        if rows:
            embed.add_field(
                name="Игроки",
                value="\n".join(rows),
                inline=False,
            )
        else:
            embed.description = "Whitelist пуст."

        if len(entries) > _MAX_LIST_ROWS:
            embed.set_footer(text=f"Показаны первые {_MAX_LIST_ROWS} из {len(entries)}")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ── /access audit ────────────────────────────────────────────────────

    @access_group.command(name="audit", description="Последние записи audit-лога")
    @app_commands.describe(days="За сколько дней показать (по умолчанию 1)")
    @whitelist_required(Role.ADMIN)
    async def access_audit(
        self,
        interaction: discord.Interaction,
        days: int = 1,
    ) -> None:
        if days < 1 or days > 90:
            await interaction.response.send_message(
                "❌ `days` должно быть от 1 до 90.", ephemeral=True
            )
            return

        entries = read_recent_entries(days=days)
        entries = entries[-_MAX_AUDIT_ROWS:]  # последние N

        embed = discord.Embed(
            title=f"🔍  Audit log — последние {days} дн.",
            description=f"Найдено записей: **{len(entries)}**",
            color=discord.Color.blurple(),
        )

        if entries:
            rows: list[str] = []
            for e in reversed(entries):  # новые сверху
                ts_str = e.get("ts", "?")[:19].replace("T", " ")
                actor = e.get("actor", "?")
                action = e.get("action", "?")
                target = e.get("target") or "—"
                result = e.get("result", "?")
                rows.append(f"`{ts_str}` **{action}** `{actor}` → `{target}` [{result}]")

            embed.add_field(
                name="Записи",
                value="\n".join(rows[:_MAX_AUDIT_ROWS]),
                inline=False,
            )
        else:
            embed.description = f"Нет записей за последние {days} дн."

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: ArenaCoachBot) -> None:  # type: ignore[override]
    await bot.add_cog(AccessCog(bot))
