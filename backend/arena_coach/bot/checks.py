"""Whitelist-чекеры для Discord-команд. Phase 2 skeleton.

Каждая команда обёрнута декоратором @whitelist_required(role=...) — default-deny.
Денай → ephemeral ответ из mock'а §4.6 phase-0-design.
"""

from __future__ import annotations


def whitelist_required(role: str | None = None) -> object:
    """TODO(Phase 2): декоратор для discord.py command'ов. Проверка через access.service."""
    raise NotImplementedError("Phase 2")
