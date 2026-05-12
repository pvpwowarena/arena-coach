"""Tail Logs/Chat-YYYY-MM-DD.txt → канонические события.

Phase 4 stub. Реализация согласно ADR-0003:
1. Открыть актуальный Chat-<today>.txt в режиме «следящего чтения».
2. Прочитать новые строки, отфильтровать по префиксу `[AC|`.
3. Декодировать base64 → JSON → pydantic event-модель.
4. Эмитить событие в шину для отправки по WSS.
5. На полночь — переключиться на новый файл Chat-<tomorrow>.txt.
"""

from __future__ import annotations


def tail_chat_log() -> None:
    """TODO(Phase 4): line-buffered tail + префикс-фильтр + base64-декод."""
    raise NotImplementedError("Phase 4")
