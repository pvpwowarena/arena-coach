"""Phase 4.18: сеть вне горячего пути — бэкенд не ждёт Discord, мост не ждёт POST.

Это регресс-тесты на КОРЕНЬ измеренной 26-секундной задержки (память проекта:
root-cause-26s-inline-post). Оба звена проверяются одинаково: медленная сеть
подменяется заглушкой, и утверждается, что горячий путь всё равно быстрый.
"""

from __future__ import annotations

import asyncio
import time
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from arena_bridge.combat_tail import CombatInterpreter
from arena_bridge.send_queue import EventSender, LagClock
from arena_coach.orchestrator import pipeline

pytestmark = pytest.mark.asyncio


# ── Мост: очередь между чтением лога и отправкой ─────────────────────────────


class TestSendQueue:
    async def test_submit_does_not_wait_for_network(self) -> None:
        released = asyncio.Event()

        async def _slow_send(payload: dict[str, object]) -> bool:
            await released.wait()
            return True

        sender = EventSender(_slow_send)
        sender.start()

        started = time.monotonic()
        for i in range(5):
            sender.submit({"n": i}, log_lag_s=0.0, label=f"EV{i}")
        elapsed = time.monotonic() - started

        # Пять событий при намертво висящей сети — цикл чтения лога свободен.
        assert elapsed < 0.05
        assert sender.stats.submitted == 5

        released.set()
        await sender.stop()
        assert sender.stats.sent == 5

    async def test_overflow_drops_oldest_not_newest(self) -> None:
        seen: list[int] = []
        gate = asyncio.Event()

        async def _send(payload: dict[str, object]) -> bool:
            await gate.wait()
            seen.append(int(payload["n"]))  # type: ignore[arg-type]
            return True

        sender = EventSender(_send, max_queue=3)
        sender.start()
        for i in range(10):
            sender.submit({"n": i}, log_lag_s=0.0, label=f"EV{i}")

        assert sender.stats.dropped_full > 0
        gate.set()
        await sender.stop()
        # Выживают САМЫЕ СВЕЖИЕ: просроченная подсказка в арене вредна.
        assert seen and max(seen) == 9
        assert 0 not in seen

    async def test_stale_events_are_not_sent(self) -> None:
        sent: list[dict[str, object]] = []

        async def _send(payload: dict[str, object]) -> bool:
            sent.append(payload)
            return True

        sender = EventSender(_send, stale_after_s=0.0)
        sender.submit({"n": 1}, log_lag_s=0.0, label="EV")
        sender.start()
        await sender.stop()
        assert sent == []
        assert sender.stats.dropped_stale == 1

    async def test_lag_clock_measures_log_to_wallclock(self) -> None:
        line_ts = datetime(2026, 7, 30, 13, 49, 45)
        clock = LagClock(now=lambda: line_ts + timedelta(seconds=2.5))
        assert clock.lag_s(line_ts) == pytest.approx(2.5)
        # Часы клиента чуть впереди — не показываем отрицательную задержку.
        ahead = LagClock(now=lambda: line_ts - timedelta(seconds=1))
        assert ahead.lag_s(line_ts) == 0.0
        assert clock.lag_s(None) is None

    async def test_interpreter_exposes_line_timestamp(self) -> None:
        it = CombatInterpreter(player_name="Vlad")
        it.feed_line(
            '7/30/2026 13:49:45.260  SPELL_AURA_REMOVED,0x1,"Vlad",0x511,0x2,"Vlad",'
            '0x511,32727,"Arena Preparation",0x1'
        )
        assert it.last_line_ts == datetime(2026, 7, 30, 13, 49, 45, 260000)


# ── Бэкенд: /v1/events не ждёт Discord ───────────────────────────────────────


class TestHotPathWithoutDiscord:
    async def test_deliver_returns_before_discord_answers(
        self, kb_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        delivered: list[str] = []
        release = asyncio.Event()

        async def _slow_dm(bot_token: str, discord_id: str, content: str) -> bool:
            await release.wait()
            delivered.append(content)
            return True

        monkeypatch.setattr(pipeline, "_send_discord_dm", _slow_dm)
        ctx = _ctx(kb_dir)

        started = time.monotonic()
        status = await pipeline._deliver(ctx, "42", "Vlad", "текст в DM", "фраза", voice_mode="on")
        elapsed = time.monotonic() - started

        assert status == "sent"
        assert elapsed < 0.05  # Discord ещё висит, а горячий путь уже свободен
        assert delivered == []
        # Голос — единственный канал, который обязан быть мгновенным.
        assert ctx.hint_queue.pop_fresh("Vlad")

        release.set()
        await ctx.drain_bg()
        assert delivered == ["текст в DM"]

    async def test_dm_order_is_preserved_per_player(
        self, kb_dir: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        delivered: list[str] = []

        async def _dm(bot_token: str, discord_id: str, content: str) -> bool:
            # Первый DM «медленный»: без цепочки он бы приехал вторым.
            await asyncio.sleep(0.02 if content == "первый" else 0.0)
            delivered.append(content)
            return True

        monkeypatch.setattr(pipeline, "_send_discord_dm", _dm)
        ctx = _ctx(kb_dir)
        ctx.spawn_dm("42", "первый")
        ctx.spawn_dm("42", "второй")
        await ctx.drain_bg()
        assert delivered == ["первый", "второй"]


def _ctx(kb_dir: Path) -> pipeline.PipelineContext:
    from types import SimpleNamespace

    from arena_coach.kb.indexer import KBIndex
    from arena_coach.kb.retriever import KBRetriever
    from arena_coach.shared.settings import Settings

    index = KBIndex()
    index.load(kb_dir)
    return pipeline.PipelineContext(
        access_service=SimpleNamespace(),  # type: ignore[arg-type] — здесь не нужен
        kb_retriever=KBRetriever(index),
        anthropic_client=SimpleNamespace(),
        settings=Settings(discord_bot_token="t", anthropic_api_key=""),
    )
