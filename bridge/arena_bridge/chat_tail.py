"""Tail Logs/Chat-YYYY-MM-DD.txt → канонические события.

WoW TBC пишет исходящие whisper-to-self в файл чата мгновенно.
Аддон отправляет события в формате [AC|TYPE|field1|field2|...].
Bridge читает файл раз в poll_interval секунд и извлекает AC-строки.

Ротация файла: в полночь WoW начинает писать в новый Chat-<new_date>.txt.
Мы отслеживаем это и переключаемся автоматически.
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
# WoW пишет whisper-to-self как «To PlayerName: [AC|...]»
# В русском клиенте может быть «Кому PlayerName: [AC|...]»
# Мы ищем [AC|...] независимо от языка интерфейса.
_AC_RE = re.compile(r"\[AC\|([^\]]+)\]")


def _today_chat_path(log_dir: Path) -> Path:
    """Путь к Chat-файлу на сегодня."""
    today = date.today().strftime("%Y-%m-%d")
    return log_dir / f"Chat-{today}.txt"


class ChatTailer:
    """Asyncio tailer для WoW Chat-лога.

    Использование::

        tailer = ChatTailer(Path("C:/WoW/Logs"), poll_interval=0.5)
        async for raw_line in tailer.lines():
            print(raw_line)  # содержимое внутри [AC|...|]

    Генерирует только строки, содержащие [AC|...|].
    При полуночной ротации автоматически переключается на новый файл.
    """

    def __init__(self, log_dir: Path, poll_interval: float = 0.5) -> None:
        self.log_dir = log_dir
        self.poll_interval = poll_interval
        self._running = False

    async def lines(self) -> AsyncIterator[str]:
        """Асинхронный генератор AC-строк из chat-лога."""
        self._running = True
        current_path = _today_chat_path(self.log_dir)
        file_handle = None
        current_date = date.today()
        # Файл уже существовал при старте? → seek END (пропускаем историю).
        # Файл появился позже (ротация или bridge стартовал раньше WoW) → читаем с начала.
        initial_file_existed = current_path.exists()

        try:
            while self._running:
                # Ротация файла в полночь
                today = date.today()
                if today != current_date:
                    log.info(
                        "Ротация chat-лога: %s → %s",
                        current_path.name,
                        _today_chat_path(self.log_dir).name,
                    )
                    if file_handle is not None:
                        file_handle.close()
                        file_handle = None
                    current_date = today
                    current_path = _today_chat_path(self.log_dir)
                    initial_file_existed = False  # новый файл — читаем с начала

                # Открываем файл, если ещё не открыт
                if file_handle is None:
                    if not current_path.exists():
                        log.debug("Chat-лог не найден: %s — жду", current_path)
                        await asyncio.sleep(self.poll_interval)
                        continue
                    file_handle = current_path.open("r", encoding="utf-8", errors="replace")
                    if initial_file_existed:
                        # Файл был до нашего старта — пропускаем историю
                        file_handle.seek(0, 2)  # SEEK_END
                    # Если файл появился после старта — читаем с позиции 0 (по умолчанию)
                    log.info(
                        "Открыт chat-лог: %s (с позиции %d, skip_history=%s)",
                        current_path,
                        file_handle.tell(),
                        initial_file_existed,
                    )

                # Читаем новые строки
                while True:
                    line = file_handle.readline()
                    if not line:
                        break  # нет новых данных — ждём следующего poll
                    match = _AC_RE.search(line)
                    if match:
                        payload = match.group(1)
                        log.debug("AC event: %s", payload)
                        yield payload

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
    """Разобрать payload из [AC|...] в список полей [type, field1, field2, ...].

    Args:
        raw: содержимое внутри [AC|...] — строка вида «TYPE|field1|field2»

    Returns:
        Список строк (type, fields...) или None если формат нераспознан.

    Examples:
        >>> parse_ac_line("TRINKET|EnemyName|42292|pvp_trinket")
        ['TRINKET', 'EnemyName', '42292', 'pvp_trinket']
        >>> parse_ac_line("ARENA_START|2v2|ROGUE/HUMAN,MAGE/GNOME")
        ['ARENA_START', '2v2', 'ROGUE/HUMAN,MAGE/GNOME']
    """
    if not raw:
        return None
    parts = raw.split("|")
    if not parts:
        return None
    return parts


def get_bridge_timestamp() -> str:
    """ISO8601 UTC timestamp для envelope события."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
