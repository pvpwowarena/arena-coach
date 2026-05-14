"""Whitelist-чекеры для Discord app commands. Default-deny.

Использование в cog'е:
    @app_commands.command(name="matchup")
    @whitelist_required(Role.VIEWER)
    async def matchup(self, interaction: discord.Interaction, ...) -> None:
        ...

Если проверка не проходит:
- Пишем в audit log (action=«command.denied»)
- Бросаем app_commands.CheckFailure
- Error handler в client.py отправляет ephemeral access-denied embed
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import discord
from discord import app_commands

from arena_coach.access.audit import write_audit_entry
from arena_coach.access.models import Role

if TYPE_CHECKING:
    from arena_coach.bot.client import ArenaCoachBot


def whitelist_required(required_role: Role = Role.VIEWER) -> Any:
    """Декоратор для app_commands: проверяет whitelist перед выполнением команды.

    Аргументы:
        required_role: минимальная роль для выполнения команды.
    """

    async def predicate(interaction: discord.Interaction) -> bool:
        bot: ArenaCoachBot = interaction.client  # type: ignore[assignment]
        actor_id = str(interaction.user.id)
        cmd_name = interaction.command.name if interaction.command else "unknown"

        has_access = await bot.access_service.check_access(
            discord_id=actor_id,
            required_role=required_role,
        )

        if not has_access:
            write_audit_entry(
                actor_discord_id=actor_id,
                action="command.denied",
                target=cmd_name,
                payload={"role_required": required_role.value},
                result="denied",
            )
            # Бросаем CheckFailure — error handler отправит embed
            raise app_commands.CheckFailure(
                f"Access denied for {actor_id!r}, required role: {required_role.value}"
            )

        return True

    return app_commands.check(predicate)


def access_denied_embed() -> discord.Embed:
    """Стандартный ephemeral embed для отказа в доступе."""
    return discord.Embed(
        title="🚫  Нет доступа",
        description=(
            "У тебя нет доступа к этой команде.\n"
            "Попроси администратора добавить тебя: `/access add @ты role:viewer character:... realm:...`"
        ),
        color=discord.Color.red(),
    )


__all__ = ["access_denied_embed", "whitelist_required"]
