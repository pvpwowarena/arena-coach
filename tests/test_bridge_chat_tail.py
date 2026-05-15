"""Тесты для arena_bridge.chat_tail — парсинг AC-строк из chat-лога."""

from __future__ import annotations

import asyncio
import datetime
from pathlib import Path

from arena_bridge.chat_tail import ChatTailer, get_bridge_timestamp, parse_ac_line


def _today_chat_filename() -> str:
    """Имя файла, который ChatTailer ожидает увидеть «на сегодня»."""
    return f"Chat-{datetime.date.today().strftime('%Y-%m-%d')}.txt"

# ── parse_ac_line ─────────────────────────────────────────────────────────────


class TestParseAcLine:
    def test_trinket(self) -> None:
        parts = parse_ac_line("TRINKET|EnemyName|42292|pvp_trinket")
        assert parts == ["TRINKET", "EnemyName", "42292", "pvp_trinket"]

    def test_arena_start(self) -> None:
        parts = parse_ac_line("ARENA_START|2v2|ROGUE/HUMAN,MAGE/GNOME")
        assert parts == ["ARENA_START", "2v2", "ROGUE/HUMAN,MAGE/GNOME"]

    def test_single_field(self) -> None:
        parts = parse_ac_line("ARENA_END")
        assert parts == ["ARENA_END"]

    def test_empty_returns_none(self) -> None:
        assert parse_ac_line("") is None

    def test_preserves_slash(self) -> None:
        parts = parse_ac_line("ARENA_START|3v3|ROGUE/HUMAN,PRIEST/UNDEAD,MAGE/GNOME")
        assert parts is not None
        assert "ROGUE/HUMAN,PRIEST/UNDEAD,MAGE/GNOME" in parts


# ── get_bridge_timestamp ──────────────────────────────────────────────────────


class TestGetBridgeTimestamp:
    def test_format(self) -> None:
        ts = get_bridge_timestamp()
        assert ts.endswith("Z")
        # ISO format: YYYY-MM-DDTHH:MM:SSZ
        assert "T" in ts
        assert len(ts) == 20  # 2026-05-14T12:34:56Z


# ── ChatTailer (файловый тест) ────────────────────────────────────────────────


class TestChatTailer:
    async def test_picks_up_ac_lines(self, tmp_path: Path) -> None:
        """Tailer находит [AC|...] строки в файле написанном после старта."""
        log_file = tmp_path / _today_chat_filename()
        log_file.write_text(
            "[12:00:00] OldLine: ignored\n",
            encoding="utf-8",
        )

        results: list[str] = []
        tailer = ChatTailer(log_dir=tmp_path, poll_interval=0.05)

        async def _writer() -> None:
            await asyncio.sleep(0.12)
            with log_file.open("a", encoding="utf-8") as f:
                f.write("[12:00:01] To Player: [AC|TRINKET|Enemy|42292|pvp_trinket]\n")
                f.write("[12:00:02] Normal line without AC\n")
                f.write("[12:00:03] To Player: [AC|ARENA_END|15]\n")

        async def _reader() -> None:
            async for payload in tailer.lines():
                results.append(payload)
                if len(results) >= 2:
                    tailer.stop()
                    break

        await asyncio.gather(_writer(), _reader())

        assert len(results) == 2
        assert results[0] == "TRINKET|Enemy|42292|pvp_trinket"
        assert results[1] == "ARENA_END|15"

    async def test_ignores_lines_before_start(self, tmp_path: Path) -> None:
        """Строки в файле до запуска tailer должны быть пропущены."""
        log_file = tmp_path / _today_chat_filename()
        # Уже есть [AC|...] строки — они должны быть пропущены
        log_file.write_text(
            "[11:00:00] To Player: [AC|ARENA_START|2v2|ROGUE/HUMAN]\n"
            "[11:00:01] To Player: [AC|TRINKET|Old|42292|pvp_trinket]\n",
            encoding="utf-8",
        )

        results: list[str] = []
        tailer = ChatTailer(log_dir=tmp_path, poll_interval=0.05)

        async def _writer() -> None:
            await asyncio.sleep(0.12)
            with log_file.open("a", encoding="utf-8") as f:
                f.write("[12:00:01] To Player: [AC|ARENA_END|5]\n")

        async def _reader() -> None:
            async for payload in tailer.lines():
                results.append(payload)
                tailer.stop()
                break

        await asyncio.gather(_writer(), _reader())

        # Только новая строка, не старые
        assert results == ["ARENA_END|5"]

    async def test_waits_for_file(self, tmp_path: Path) -> None:
        """Tailer ждёт пока файл появится (создаём файл с текущей датой)."""
        log_file = tmp_path / _today_chat_filename()

        results: list[str] = []
        tailer = ChatTailer(log_dir=tmp_path, poll_interval=0.05)

        async def _writer() -> None:
            # Файл ещё не существует — появится через 150ms
            await asyncio.sleep(0.15)
            log_file.write_text(
                "[12:00:00] To Player: [AC|ARENA_START|2v2|WARRIOR/ORC]\n",
                encoding="utf-8",
            )

        async def _reader() -> None:
            async for payload in tailer.lines():
                results.append(payload)
                tailer.stop()
                break

        await asyncio.gather(_writer(), _reader())
        assert len(results) == 1
        assert "ARENA_START" in results[0]
