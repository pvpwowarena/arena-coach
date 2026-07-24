"""Тесты Phase 4.6 (backend): очередь персональных фраз + эндпоинт /v1/hints.

Покрываем без сети/Discord:
  • HintQueue — per-player изоляция, TTL-протухание, кап на игрока и на число
    игроков, дренаж (pop очищает), чистка протухших;
  • GET /v1/hints — bearer-аутентификация, дренаж очереди, 503 без контекста
    (через FastAPI TestClient с лёгким приложением);
  • pipeline — фраза кладётся в очередь при voice_mode on и НЕ кладётся при off.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from arena_coach.api.routes import events as events_module
from arena_coach.kb.indexer import KBIndex
from arena_coach.kb.retriever import KBRetriever
from arena_coach.orchestrator import pipeline
from arena_coach.orchestrator.hint_queue import HintQueue
from arena_coach.shared.settings import Settings

# ── HintQueue ────────────────────────────────────────────────────────────────


class TestHintQueue:
    def test_push_pop_roundtrip(self) -> None:
        q = HintQueue()
        q.push("Vladislav", "Айсблок у Фрости!")
        assert q.pop_fresh("Vladislav") == ["Айсблок у Фрости!"]

    def test_case_insensitive_key(self) -> None:
        """Ключ — как whitelist-lookup (lower); мост шлёт своё имя как есть."""
        q = HintQueue()
        q.push("Vladislav", "фраза")
        assert q.pop_fresh("vladislav") == ["фраза"]

    def test_per_player_isolation(self) -> None:
        q = HintQueue()
        q.push("Alice", "a1")
        q.push("Bob", "b1")
        assert q.pop_fresh("Alice") == ["a1"]
        assert q.pop_fresh("Bob") == ["b1"]

    def test_pop_drains(self) -> None:
        q = HintQueue()
        q.push("Alice", "one")
        assert q.pop_fresh("Alice") == ["one"]
        assert q.pop_fresh("Alice") == []  # второй раз пусто

    def test_order_preserved(self) -> None:
        q = HintQueue()
        q.push("Alice", "one")
        q.push("Alice", "two")
        assert q.pop_fresh("Alice") == ["one", "two"]

    def test_ttl_drops_stale(self) -> None:
        q = HintQueue(ttl_s=10.0)
        q.push("Alice", "старая", now=100.0)
        q.push("Alice", "свежая", now=108.0)
        # опрос на 111с: 'старая' (age 11с) протухла, 'свежая' (age 3с) — нет
        assert q.pop_fresh("Alice", now=111.0) == ["свежая"]

    def test_ttl_boundary_inclusive(self) -> None:
        q = HintQueue(ttl_s=10.0)
        q.push("Alice", "ровно", now=100.0)
        assert q.pop_fresh("Alice", now=110.0) == ["ровно"]  # ровно TTL — ещё свежая
        q.push("Alice", "чуть-позже", now=100.0)
        assert q.pop_fresh("Alice", now=110.01) == []  # >TTL — дропнута

    def test_per_player_cap(self) -> None:
        q = HintQueue(max_per_player=3)
        for i in range(5):
            q.push("Alice", f"p{i}")
        # deque(maxlen=3) держит только последние 3
        assert q.pop_fresh("Alice") == ["p2", "p3", "p4"]

    def test_max_players_evicts_least_active(self) -> None:
        q = HintQueue(max_players=2)
        q.push("A", "a", now=1.0)
        q.push("B", "b", now=2.0)
        q.push("A", "a2", now=3.0)  # A снова активен → B наименее активен
        q.push("C", "c", now=4.0)  # добавляем C → вытесняется B
        assert len(q) == 2
        assert q.pop_fresh("B", now=5.0) == []  # B вытеснен
        assert q.pop_fresh("A", now=5.0) == ["a", "a2"]
        assert q.pop_fresh("C", now=5.0) == ["c"]

    def test_empty_inputs_ignored(self) -> None:
        q = HintQueue()
        q.push("", "фраза")
        q.push("Alice", "   ")
        q.push("Alice", "")
        assert len(q) == 0
        assert q.pop_fresh("") == []

    def test_purge_stale_players(self) -> None:
        q = HintQueue(ttl_s=10.0)
        q.push("Ghost", "давно", now=100.0)
        # новый push на 200с чистит протухшего Ghost перед вставкой
        q.push("Live", "сейчас", now=200.0)
        assert len(q) == 1
        assert q.pop_fresh("Ghost", now=200.0) == []

    def test_len_counts_players(self) -> None:
        q = HintQueue()
        assert len(q) == 0
        q.push("A", "x")
        q.push("B", "y")
        assert len(q) == 2


# ── GET /v1/hints (эндпоинт) ─────────────────────────────────────────────────

_TOKEN = "secret-bridge-token"


def _client_with_queue(
    monkeypatch: pytest.MonkeyPatch, queue: HintQueue | None, *, token: str = _TOKEN
) -> TestClient:
    """Лёгкое FastAPI-приложение только с events.router (без lifespan/БД)."""
    monkeypatch.setattr(events_module._settings, "bridge_bearer_token", token)
    app = FastAPI()
    app.include_router(events_module.router)
    if queue is not None:
        app.state.pipeline_ctx = SimpleNamespace(hint_queue=queue)
    return TestClient(app)


def _auth(token: str = _TOKEN) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


class TestHintsEndpoint:
    def test_requires_auth(self, monkeypatch: pytest.MonkeyPatch) -> None:
        client = _client_with_queue(monkeypatch, HintQueue())
        resp = client.get("/v1/hints", params={"player": "Vlad"})
        assert resp.status_code == 403  # HTTPBearer(auto_error) без заголовка

    def test_wrong_token_401(self, monkeypatch: pytest.MonkeyPatch) -> None:
        client = _client_with_queue(monkeypatch, HintQueue())
        resp = client.get("/v1/hints", params={"player": "Vlad"}, headers=_auth("nope"))
        assert resp.status_code == 401

    def test_returns_and_drains(self, monkeypatch: pytest.MonkeyPatch) -> None:
        q = HintQueue()
        q.push("Vlad", "Тринкет у X!")
        client = _client_with_queue(monkeypatch, q)
        resp = client.get("/v1/hints", params={"player": "Vlad"}, headers=_auth())
        assert resp.status_code == 200
        assert resp.json() == {"player": "Vlad", "hints": ["Тринкет у X!"]}
        # очередь вычищена
        resp2 = client.get("/v1/hints", params={"player": "Vlad"}, headers=_auth())
        assert resp2.json()["hints"] == []

    def test_per_player_isolation_over_http(self, monkeypatch: pytest.MonkeyPatch) -> None:
        q = HintQueue()
        q.push("Alice", "a")
        q.push("Bob", "b")
        client = _client_with_queue(monkeypatch, q)
        assert client.get("/v1/hints", params={"player": "Alice"}, headers=_auth()).json()[
            "hints"
        ] == ["a"]
        # Bob не тронут дренажом Alice
        assert client.get("/v1/hints", params={"player": "Bob"}, headers=_auth()).json()[
            "hints"
        ] == ["b"]

    def test_missing_player_param_422(self, monkeypatch: pytest.MonkeyPatch) -> None:
        client = _client_with_queue(monkeypatch, HintQueue())
        resp = client.get("/v1/hints", headers=_auth())
        assert resp.status_code == 422

    def test_503_without_context(self, monkeypatch: pytest.MonkeyPatch) -> None:
        client = _client_with_queue(monkeypatch, None)  # app.state.pipeline_ctx не задан
        resp = client.get("/v1/hints", params={"player": "Vlad"}, headers=_auth())
        assert resp.status_code == 503

    def test_no_token_configured_503(self, monkeypatch: pytest.MonkeyPatch) -> None:
        client = _client_with_queue(monkeypatch, HintQueue(), token="")
        resp = client.get("/v1/hints", params={"player": "Vlad"}, headers=_auth())
        assert resp.status_code == 503


# ── pipeline: постановка фразы в очередь по voice_mode ────────────────────────


class _FakeAccess:
    async def find_by_character(self, character: str) -> SimpleNamespace:
        return SimpleNamespace(discord_id="111")


class _FakePlayerSettings:
    def __init__(self, mode: str) -> None:
        self.mode = mode

    async def get_voice_mode(self, discord_id: str) -> str:
        return self.mode


def _ctx(kb_dir: Path, mode: str) -> pipeline.PipelineContext:
    index = KBIndex()
    index.load(kb_dir)
    return pipeline.PipelineContext(
        access_service=_FakeAccess(),  # type: ignore[arg-type]
        kb_retriever=KBRetriever(index),
        anthropic_client=SimpleNamespace(),  # type: ignore[arg-type]
        settings=Settings(discord_bot_token="t", discord_voice_channel_id=0),
        player_settings=_FakePlayerSettings(mode),  # type: ignore[arg-type]
    )


def _start_envelope() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "bridge_ts": "2026-07-24T12:00:00Z",
        "session_id": "s1",
        "player_name": "Arenacoach",
        "event": {"type": "ARENA_START", "bracket": "2v2"},
        "match": {
            "bracket": "2v2",
            "enemies": [
                {"wow_class": "ROGUE", "race": "UNKNOWN"},
                {"wow_class": "MAGE", "race": "UNKNOWN"},
            ],
            "allies": [],
            "our_comp_hint": "rogue+warlock",
            "player_class": "ROGUE",
        },
    }


@pytest.fixture
def _no_delivery(monkeypatch: pytest.MonkeyPatch) -> None:
    """Глушим внешнюю доставку (DM/Discord-voice/LLM) — тестируем только очередь."""

    async def _dm(bot_token: str, discord_id: str, content: str) -> bool:
        return True

    async def _voice(settings: Settings, text: str) -> bool:
        return False  # Discord voice-канал не настроен (channel_id=0)

    async def _no_llm(*args: Any, **kwargs: Any) -> str:
        raise RuntimeError("LLM off")

    monkeypatch.setattr(pipeline, "_send_discord_dm", _dm)
    monkeypatch.setattr(pipeline, "_send_voice_hint", _voice)
    monkeypatch.setattr(pipeline, "_generate_hint", _no_llm)


class TestPipelineQueuesLocalHint:
    async def test_mode_on_queues_phrase(self, kb_dir: Path, _no_delivery: None) -> None:
        ctx = _ctx(kb_dir, "on")
        await pipeline.process_event(ctx, _start_envelope())
        queued = ctx.hint_queue.pop_fresh("Arenacoach")
        assert len(queued) == 1
        assert queued[0].startswith("Арена.")
        assert "Килл таргет" in queued[0]

    async def test_mode_only_queues_phrase(self, kb_dir: Path, _no_delivery: None) -> None:
        ctx = _ctx(kb_dir, "only")
        await pipeline.process_event(ctx, _start_envelope())
        assert len(ctx.hint_queue.pop_fresh("Arenacoach")) == 1

    async def test_mode_off_queues_nothing(self, kb_dir: Path, _no_delivery: None) -> None:
        ctx = _ctx(kb_dir, "off")
        await pipeline.process_event(ctx, _start_envelope())
        assert ctx.hint_queue.pop_fresh("Arenacoach") == []

    async def test_trinket_phrase_queued(self, kb_dir: Path, _no_delivery: None) -> None:
        ctx = _ctx(kb_dir, "on")
        await pipeline.process_event(ctx, _start_envelope())
        ctx.hint_queue.pop_fresh("Arenacoach")  # дренируем ARENA_START
        env = _start_envelope()
        env["event"] = {"type": "TRINKET", "source_name": "Cekraj", "trinket_key": "pvp_trinket"}
        env["bridge_ts"] = "2026-07-24T12:00:40Z"
        await pipeline.process_event(ctx, env)
        assert ctx.hint_queue.pop_fresh("Arenacoach") == ["Тринкет у Cekraj!"]
