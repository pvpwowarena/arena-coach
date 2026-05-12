"""Polling SavedVariables.lua → канонические события.

Phase 4 stub. Реализация:
1. watchdog.events.FileSystemEventHandler на SavedVariables/ArenaCoach.lua.
2. Парсер Lua-таблицы (slpp или регулярки, см. ADR будущего).
3. Diff с предыдущим состоянием — отправляем только новые sessions/events.
"""

from __future__ import annotations


def tail_savedvariables() -> None:
    """TODO(Phase 4): запустить watchdog observer + diff-логику."""
    raise NotImplementedError("Phase 4")
