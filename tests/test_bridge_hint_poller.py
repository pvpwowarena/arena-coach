"""Тесты Phase 4.6 (мост): поллер обратного канала + EventClient.get_hints.

Сеть/речь не трогаем: fetch/speak — async-фейки, а get_hints проверяется через
httpx.MockTransport (без реального backend).
"""

from __future__ import annotations

import asyncio

import httpx
import pytest

from arena_bridge.hint_poller import (
    LocalHintDedup,
    SpeechChannel,
    poll_hints_once,
    run_hint_poller,
)
from arena_bridge.ws_client import EventClient

# ── LocalHintDedup ───────────────────────────────────────────────────────────


class TestDedup:
    def test_blocks_repeat_within_window(self) -> None:
        t = [100.0]
        dedup = LocalHintDedup(window_s=6.0, clock=lambda: t[0])
        assert dedup.allow("Айсблок!") is True
        assert dedup.allow("Айсблок!") is False  # то же время — дубль
        t[0] = 107.0
        assert dedup.allow("Айсблок!") is True  # окно прошло

    def test_different_phrases_pass(self) -> None:
        dedup = LocalHintDedup(window_s=6.0, clock=lambda: 100.0)
        assert dedup.allow("раз") is True
        assert dedup.allow("два") is True

    def test_old_entries_purged(self) -> None:
        t = [0.0]
        dedup = LocalHintDedup(window_s=5.0, clock=lambda: t[0])
        for i in range(10):
            t[0] = float(i)
            dedup.allow(f"фраза-{i}")
        # словарь не хранит записи старше окна
        assert len(dedup._last_said) <= 6


# ── poll_hints_once ──────────────────────────────────────────────────────────


class TestPollOnce:
    async def test_speaks_fresh(self) -> None:
        spoken: list[str] = []

        async def fetch(player: str) -> list[str]:
            assert player == "Vlad"
            return ["раз", "два"]

        async def speak(text: str) -> bool:
            spoken.append(text)
            return True

        dedup = LocalHintDedup(window_s=6.0, clock=lambda: 100.0)
        n = await poll_hints_once(fetch, speak, "Vlad", dedup)
        # Phase 4.12: батч не выстраивается в очередь — произносится самая свежая
        # фраза, остальные вытесняются (иначе голос отстаёт от боя).
        assert n == 2
        assert spoken == ["два"]

    async def test_dedups_within_batch(self) -> None:
        spoken: list[str] = []

        async def fetch(player: str) -> list[str]:
            return ["a", "a", "b"]

        async def speak(text: str) -> bool:
            spoken.append(text)
            return True

        dedup = LocalHintDedup(window_s=6.0, clock=lambda: 100.0)
        n = await poll_hints_once(fetch, speak, "P", dedup)
        assert n == 2  # 'a' дедуплицирован внутри батча
        assert spoken == ["b"]  # озвучена самая свежая

    async def test_empty_batch(self) -> None:
        async def fetch(player: str) -> list[str]:
            return []

        async def speak(text: str) -> bool:  # pragma: no cover — не должен вызваться
            raise AssertionError("speak не должен вызываться на пустом батче")

        dedup = LocalHintDedup(window_s=6.0, clock=lambda: 100.0)
        assert await poll_hints_once(fetch, speak, "P", dedup) == 0


# ── SpeechChannel (Phase 4.12) ───────────────────────────────────────────────


class TestSpeechChannel:
    async def test_newer_phrase_replaces_pending(self) -> None:
        """Свежий совет отменяет прошлый, а не встаёт за ним в очередь."""
        spoken: list[str] = []
        release = asyncio.Event()

        async def speak(text: str) -> bool:
            spoken.append(text)
            await release.wait()
            return True

        ch = SpeechChannel(speak)
        ch.offer("первая")
        ch.pump()  # первая пошла в речь
        await asyncio.sleep(0)
        ch.offer("вторая")
        ch.offer("третья")  # вытесняет 'вторую'
        assert ch.dropped == 1
        release.set()
        await ch.drain()
        ch.pump()
        await ch.drain()
        assert spoken == ["первая", "третья"]

    async def test_stale_phrase_not_spoken(self) -> None:
        """«Тринкеть под кидни» через восемь секунд — вредный совет, молчим."""
        spoken: list[str] = []
        now = {"t": 100.0}

        async def speak(text: str) -> bool:
            spoken.append(text)
            return True

        ch = SpeechChannel(speak, clock=lambda: now["t"], max_age_s=6.0)
        ch.offer("устареет")
        now["t"] += 8.0
        ch.pump()
        await ch.drain()
        assert spoken == []
        assert ch.dropped == 1

    async def test_speech_does_not_block_polling(self) -> None:
        """Главный фикс: длинная речь больше не тормозит опрос /v1/hints."""
        stop = asyncio.Event()
        fetches = {"n": 0}
        release = asyncio.Event()

        async def fetch(player: str) -> list[str]:
            fetches["n"] += 1
            if fetches["n"] == 1:
                return ["длинная фраза"]
            if fetches["n"] >= 5:
                release.set()
                stop.set()
            return []

        async def speak(text: str) -> bool:
            await release.wait()  # «речь» длится, пока идут опросы
            return True

        await asyncio.wait_for(
            run_hint_poller(fetch, speak, "P", stop, interval_s=0.01),
            timeout=2.0,
        )
        assert fetches["n"] >= 5


# ── run_hint_poller ──────────────────────────────────────────────────────────


class TestRunPoller:
    async def test_speaks_then_stops(self) -> None:
        stop = asyncio.Event()
        spoken: list[str] = []
        calls = {"n": 0}

        async def fetch(player: str) -> list[str]:
            calls["n"] += 1
            if calls["n"] == 1:
                return ["раз", "два"]
            stop.set()
            return []

        async def speak(text: str) -> bool:
            spoken.append(text)
            return True

        await asyncio.wait_for(
            run_hint_poller(fetch, speak, "P", stop, interval_s=0.01),
            timeout=2.0,
        )
        assert spoken == ["два"]

    async def test_survives_fetch_error(self) -> None:
        stop = asyncio.Event()
        spoken: list[str] = []
        calls = {"n": 0}

        async def fetch(player: str) -> list[str]:
            calls["n"] += 1
            if calls["n"] == 1:
                raise RuntimeError("сеть моргнула")
            if calls["n"] == 2:
                return ["ok"]
            stop.set()
            return []

        async def speak(text: str) -> bool:
            spoken.append(text)
            return True

        await asyncio.wait_for(
            run_hint_poller(fetch, speak, "P", stop, interval_s=0.01),
            timeout=2.0,
        )
        assert spoken == ["ok"]  # цикл пережил ошибку и продолжил

    async def test_cancellable(self) -> None:
        stop = asyncio.Event()

        async def fetch(player: str) -> list[str]:
            return []

        async def speak(text: str) -> bool:
            return True

        task = asyncio.create_task(run_hint_poller(fetch, speak, "P", stop, interval_s=5.0))
        await asyncio.sleep(0.02)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task


# ── EventClient.get_hints (httpx.MockTransport) ──────────────────────────────


async def _client(handler: httpx.MockTransport | object) -> EventClient:
    client = EventClient("http://backend", "tok")
    await client._client.aclose()  # закрываем авто-созданный, ставим мок-транспорт
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler),  # type: ignore[arg-type]
        headers={"Authorization": "Bearer tok"},
    )
    return client


class TestGetHints:
    async def test_success(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/hints"
            assert request.url.params.get("player") == "Vlad"
            assert request.headers["Authorization"] == "Bearer tok"
            return httpx.Response(200, json={"player": "Vlad", "hints": ["a", "b"]})

        client = await _client(handler)
        assert await client.get_hints("Vlad") == ["a", "b"]
        await client.close()

    async def test_filters_non_strings(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"hints": ["a", 5, None, "   ", "b"]})

        client = await _client(handler)
        assert await client.get_hints("P") == ["a", "b"]
        await client.close()

    async def test_missing_hints_key(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"player": "P"})

        client = await _client(handler)
        assert await client.get_hints("P") == []
        await client.close()

    async def test_non_dict_body(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json=["a", "b"])

        client = await _client(handler)
        assert await client.get_hints("P") == []
        await client.close()

    async def test_401_returns_empty(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(401, json={"detail": "nope"})

        client = await _client(handler)
        assert await client.get_hints("P") == []
        await client.close()

    async def test_404_returns_empty(self) -> None:
        """Старый backend без эндпоинта → пусто, мост не падает (обратная совместимость)."""

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(404)

        client = await _client(handler)
        assert await client.get_hints("P") == []
        await client.close()

    async def test_network_error_returns_empty(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("backend недоступен")

        client = await _client(handler)
        assert await client.get_hints("P") == []
        await client.close()
