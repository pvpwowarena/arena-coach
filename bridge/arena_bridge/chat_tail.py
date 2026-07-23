"""Tail WoW chat-лога → канонические события.

Имя файла зависит от клиента:
  • Классические/современные клиенты: ``Logs/WoWChatLog.txt`` (один файл,
    append-only, НЕ ротируется) — стандартное поведение ``/chatlog``.
  • Гипотетический date-stamped вариант: ``Logs/Chat-YYYY-MM-DD.txt``
    (изначальное допущение ADR-0003 — оставлено как второй кандидат).

Мы НЕ знаем заранее, какой формат у Anniversary-клиента, поэтому tailer
следит за обоими кандидатами и переключается на тот, который реально растёт.

Аддон отправляет события в формате [AC#TYPE#field1#field2#...]
(разделитель «#» с addon 0.2.1; легаси «|» тоже принимается — см. _AC_RE).
Bridge читает файл раз в poll_interval секунд и извлекает AC-строки.

Устойчивость:
  • Усечение/пересоздание файла (size < offset) → читаем с начала.
  • Недописанная строка (без \\n на конце) → откатываемся и ждём следующего
    poll — WoW флашит буфер кусками, строка может оборваться посередине.
  • Полуночная ротация date-stamped файла → автоматическое переключение.
  • Оффсеты помнятся per-file — переключение туда-обратно не теряет данные.
"""

from __future__ import annotations

import asyncio
import logging
import re
from collections.abc import AsyncIterator
from datetime import date, datetime, timezone
from pathlib import Path

log = logging.getLogger(__name__)

# Регулярка для строк аддона в chat-логе.
# WoW пишет whisper-to-self как «To PlayerName: [AC#...]»
# В русском клиенте может быть «Кому PlayerName: [AC#...]»
# Мы ищем [AC#...] независимо от языка интерфейса.
#
# Разделитель полей:
#   «#» — канонический (аддон >= 0.2.1). Символ «|» запрещён современным
#         Anniversary-клиентом в SendChatMessage (Lua-ошибка «invalid escape»),
#         из-за чего аддон 0.2.0 вообще не мог отправить события.
#   «|» — легаси (ADR-0003, synthetic-логи e2e_dryrun и старые фикстуры) —
#         поддерживаем для обратной совместимости.
_AC_RE = re.compile(r"\[AC[#|]([^\]]+)\]")

# Стандартное имя chat-лога (``/chatlog`` во всех известных клиентах).
_FIXED_CHAT_LOG = "WoWChatLog.txt"


def _today_chat_path(log_dir: Path) -> Path:
    """Путь к date-stamped Chat-файлу на сегодня (кандидат №2)."""
    today = date.today().strftime("%Y-%m-%d")
    return log_dir / f"Chat-{today}.txt"


def candidate_chat_paths(log_dir: Path) -> list[Path]:
    """Все возможные пути chat-лога в порядке приоритета."""
    return [log_dir / _FIXED_CHAT_LOG, _today_chat_path(log_dir)]


def _safe_stat(path: Path) -> tuple[float, int] | None:
    """(mtime, size) или None если файл исчез между exists() и stat()."""
    try:
        st = path.stat()
        return (st.st_mtime, st.st_size)
    except OSError:
        return None


class ChatTailer:
    """Asyncio tailer для WoW chat-лога с автодетектом имени файла.

    Использование::

        tailer = ChatTailer(Path("C:/WoW/Logs"), poll_interval=0.5)
        async for raw_line in tailer.lines():
            print(raw_line)  # содержимое внутри [AC|...]

    Генерирует только payload'ы строк, содержащих [AC|...].
    """

    def __init__(self, log_dir: Path, poll_interval: float = 0.5) -> None:
        self.log_dir = log_dir
        self.poll_interval = poll_interval
        self._running = False
        # Оффсеты чтения per-file: переключение между кандидатами не теряет данные
        self._offsets: dict[str, int] = {}

    # ── Выбор активного файла ────────────────────────────────────────────

    def _pick_active(self, current: Path | None) -> Path | None:
        """Выбрать файл для чтения.

        Логика: из существующих кандидатов берём тот, где есть непрочитанные
        данные (size > offset); при нескольких — с самым свежим mtime.
        Если непрочитанного нет нигде — остаёмся на текущем (или самом свежем).
        """
        stats: list[tuple[Path, float, int]] = []
        for p in candidate_chat_paths(self.log_dir):
            if p.exists():
                st = _safe_stat(p)
                if st is not None:
                    stats.append((p, st[0], st[1]))

        if not stats:
            return None

        # Кандидаты с непрочитанными данными
        unread = [(p, mtime) for p, mtime, size in stats if size != self._offsets.get(str(p), 0)]
        if unread:
            # Приоритет текущему файлу — не дёргаемся, пока он растёт
            if current is not None and any(p == current for p, _ in unread):
                return current
            return max(unread, key=lambda t: t[1])[0]

        if current is not None and any(p == current for p, _, _ in stats):
            return current
        return max(stats, key=lambda t: t[1])[0]

    # ── Основной цикл ────────────────────────────────────────────────────

    async def lines(self) -> AsyncIterator[str]:
        """Асинхронный генератор AC-строк из chat-лога."""
        self._running = True
        file_handle = None
        current_path: Path | None = None

        # Файлы, существовавшие при старте: их историю пропускаем (seek END
        # при первом открытии). Новые файлы читаем с нуля — их содержимое
        # гарантированно свежее.
        preexisting = {str(p) for p in candidate_chat_paths(self.log_dir) if p.exists()}

        try:
            while self._running:
                active = self._pick_active(current_path)

                if active is None:
                    log.debug("Chat-лог не найден в %s — жду", self.log_dir)
                    await asyncio.sleep(self.poll_interval)
                    continue

                # Переключение на другой файл (или первое открытие)
                if active != current_path:
                    if file_handle is not None:
                        self._offsets[str(current_path)] = file_handle.tell()
                        file_handle.close()
                        file_handle = None
                    current_path = active

                if file_handle is None:
                    file_handle = current_path.open("r", encoding="utf-8", errors="replace")
                    key = str(current_path)
                    if key in self._offsets:
                        file_handle.seek(self._offsets[key])
                    elif key in preexisting:
                        file_handle.seek(0, 2)  # SEEK_END — пропускаем историю
                    log.info(
                        "Открыт chat-лог: %s (позиция %d)",
                        current_path,
                        file_handle.tell(),
                    )

                # Усечение/пересоздание файла? (например, игрок удалил лог)
                st = _safe_stat(current_path)
                if st is not None and st[1] < file_handle.tell():
                    log.info("Chat-лог усечён (%s) — читаю с начала", current_path.name)
                    file_handle.seek(0)

                # Читаем новые строки
                while True:
                    pos_before = file_handle.tell()
                    line = file_handle.readline()
                    if not line:
                        break  # нет новых данных — ждём следующего poll
                    if not line.endswith("\n"):
                        # Недописанная строка (WoW флашит кусками) —
                        # откатываемся, дочитаем когда появится \n
                        file_handle.seek(pos_before)
                        break
                    match = _AC_RE.search(line)
                    if match:
                        payload = match.group(1)
                        log.debug("AC event: %s", payload)
                        yield payload

                self._offsets[str(current_path)] = file_handle.tell()
                await asyncio.sleep(self.poll_interval)

        finally:
            self._running = False
            if file_handle is not None:
                file_handle.close()
            log.info("Chat tailer остановлен")

    def stop(self) -> None:
        """Остановить tailer."""
        self._running = False


def parse_ac_line(raw: str) -> list[str] | None:
    """Разобрать payload из [AC#...] в список полей [type, field1, field2, ...].

    Разделитель — «#» (аддон >= 0.2.1) или легаси «|» (см. коммент к _AC_RE).
    В одном сообщении используется ровно один разделитель; поля не могут
    содержать ни «#», ни «|» (имена персонажей/слаги WoW их не допускают).

    Args:
        raw: содержимое внутри [AC#...] — строка вида «TYPE#field1#field2»

    Returns:
        Список строк (type, fields...) или None если формат нераспознан.

    Examples:
        >>> parse_ac_line("TRINKET#EnemyName#42292#pvp_trinket")
        ['TRINKET', 'EnemyName', '42292', 'pvp_trinket']
        >>> parse_ac_line("ARENA_START|2v2|ROGUE/HUMAN,MAGE/GNOME")
        ['ARENA_START', '2v2', 'ROGUE/HUMAN,MAGE/GNOME']
    """
    if not raw:
        return None
    delimiter = "#" if "#" in raw else "|"
    parts = raw.split(delimiter)
    if not parts:
        return None
    return parts


def get_bridge_timestamp() -> str:
    """ISO8601 UTC timestamp для envelope события."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
