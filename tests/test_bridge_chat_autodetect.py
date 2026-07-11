"""Тесты автодетекта chat-лога (v0.3.0): WoWChatLog.txt vs Chat-YYYY-MM-DD.txt.

Стандартное имя файла ``/chatlog`` — ``Logs/WoWChatLog.txt`` (append-only,
без ротации). Date-stamped ``Chat-*.txt`` оставлен вторым кандидатом.
Плюс устойчивость: усечение файла, недописанные строки (флаш кусками).
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from arena_bridge.chat_tail import ChatTailer, candidate_chat_paths


async def _collect(tailer: ChatTailer, n: int, timeout: float = 3.0) -> list[str]:
    """Собрать n payload'ов из tailer.lines() с таймаутом."""
    results: list[str] = []

    async def _reader() -> None:
        async for payload in tailer.lines():
            results.append(payload)
            if len(results) >= n:
                tailer.stop()
                break

    try:
        await asyncio.wait_for(_reader(), timeout=timeout)
    except asyncio.TimeoutError:
        tailer.stop()
    return results


class TestCandidatePaths:
    def test_both_candidates_listed(self, tmp_path: Path) -> None:
        paths = candidate_chat_paths(tmp_path)
        names = [p.name for p in paths]
        assert "WoWChatLog.txt" in names
        assert any(n.startswith("Chat-") and n.endswith(".txt") for n in names)


class TestWowChatLogDetect:
    async def test_picks_up_wowchatlog(self, tmp_path: Path) -> None:
        """Основной сценарий: клиент пишет в WoWChatLog.txt."""
        log_file = tmp_path / "WoWChatLog.txt"
        log_file.write_text("7/11 12:00:00.000  Old history line\n", encoding="utf-8")

        tailer = ChatTailer(log_dir=tmp_path, poll_interval=0.05)

        async def _writer() -> None:
            await asyncio.sleep(0.15)
            with log_file.open("a", encoding="utf-8") as f:
                f.write("7/11 12:00:01.000  To Vlad: [AC|ARENA_START|2v2|WARRIOR/ORC]\n")

        results, _ = await asyncio.gather(_collect(tailer, 1), _writer())
        assert results == ["ARENA_START|2v2|WARRIOR/ORC"]

    async def test_history_skipped(self, tmp_path: Path) -> None:
        """AC-строки, записанные ДО старта bridge, не переигрываются."""
        log_file = tmp_path / "WoWChatLog.txt"
        log_file.write_text(
            "7/11 11:00:00.000  To Vlad: [AC|ARENA_START|2v2|MAGE/GNOME]\n",
            encoding="utf-8",
        )

        tailer = ChatTailer(log_dir=tmp_path, poll_interval=0.05)

        async def _writer() -> None:
            await asyncio.sleep(0.15)
            with log_file.open("a", encoding="utf-8") as f:
                f.write("7/11 12:00:00.000  To Vlad: [AC|ARENA_END|3]\n")

        results, _ = await asyncio.gather(_collect(tailer, 1), _writer())
        assert results == ["ARENA_END|3"]

    async def test_truncated_file_reread(self, tmp_path: Path) -> None:
        """Файл пересоздан/усечён (например, игрок удалил лог) → читаем заново."""
        log_file = tmp_path / "WoWChatLog.txt"
        log_file.write_text("x" * 500 + "\n", encoding="utf-8")

        tailer = ChatTailer(log_dir=tmp_path, poll_interval=0.05)

        async def _writer() -> None:
            await asyncio.sleep(0.15)
            # Усечение: файл стал короче текущего оффсета
            log_file.write_text(
                "7/11 12:00:00.000  To Vlad: [AC|TRINKET|Enemy|42292|pvp_trinket]\n",
                encoding="utf-8",
            )

        results, _ = await asyncio.gather(_collect(tailer, 1), _writer())
        assert results == ["TRINKET|Enemy|42292|pvp_trinket"]

    async def test_partial_line_not_lost(self, tmp_path: Path) -> None:
        """WoW флашит буфер кусками — строка может оборваться посередине.

        Недописанная строка не должна ни потеряться, ни выдаться дважды.
        """
        log_file = tmp_path / "WoWChatLog.txt"
        log_file.write_text("", encoding="utf-8")

        tailer = ChatTailer(log_dir=tmp_path, poll_interval=0.05)

        async def _writer() -> None:
            await asyncio.sleep(0.15)
            with log_file.open("a", encoding="utf-8") as f:
                f.write("7/11 12:00:00.000  To Vlad: [AC|ARENA_EN")  # обрыв, без \n
                f.flush()
            await asyncio.sleep(0.2)  # несколько poll-циклов над обрывком
            with log_file.open("a", encoding="utf-8") as f:
                f.write("D|7]\n")  # дописали хвост

        results, _ = await asyncio.gather(_collect(tailer, 1), _writer())
        assert results == ["ARENA_END|7"]

    async def test_switches_to_growing_file(self, tmp_path: Path) -> None:
        """Оба файла существуют — читаем тот, который реально растёт."""
        stale = tmp_path / "WoWChatLog.txt"
        stale.write_text("old\n", encoding="utf-8")
        # date-stamped появится позже и начнёт расти
        dated = candidate_chat_paths(tmp_path)[1]

        tailer = ChatTailer(log_dir=tmp_path, poll_interval=0.05)

        async def _writer() -> None:
            await asyncio.sleep(0.15)
            with dated.open("a", encoding="utf-8") as f:
                f.write("7/11 12:00:00.000  To Vlad: [AC|ARENA_END|9]\n")

        results, _ = await asyncio.gather(_collect(tailer, 1), _writer())
        assert results == ["ARENA_END|9"]
