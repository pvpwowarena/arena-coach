"""Phase 4.7 Batch 1.5: персистентный кэш разборов (L2) + warm-advice.

• AdviceStore — put/get/upsert/count (SQLite);
• L2 переживает «рестарт процесса»: новый PipelineContext с пустым L1, но тем же
  L2 не зовёт модель повторно для того же сетапа;
• _parse_warm_line — разбор строки списка сетапов (класс/спек).
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from arena_coach.access.advice_store import AdviceStore
from arena_coach.access.models import Base
from arena_coach.kb.indexer import KBIndex
from arena_coach.kb.retriever import KBRetriever
from arena_coach.orchestrator import pipeline
from arena_coach.shared.settings import Settings


@pytest.fixture
async def store(tmp_path: Path) -> AdviceStore:
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/coach.db", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory: async_sessionmaker[AsyncSession] = async_sessionmaker(engine, expire_on_commit=False)
    return AdviceStore(factory)


class TestAdviceStore:
    async def test_put_get_roundtrip(self, store: AdviceStore) -> None:
        await store.put("2v2|rogue+mage|mage,mage", "разбор", "haiku")
        row = await store.get("2v2|rogue+mage|mage,mage")
        assert row is not None
        assert row.text == "разбор"
        assert row.model == "haiku"

    async def test_upsert_updates_and_counts_once(self, store: AdviceStore) -> None:
        await store.put("sig1", "v1", "haiku")
        await store.put("sig1", "v2", "sonnet")  # улучшили сильной моделью
        row = await store.get("sig1")
        assert row is not None and row.text == "v2" and row.model == "sonnet"
        assert await store.count() == 1

    async def test_missing_returns_none(self, store: AdviceStore) -> None:
        assert await store.get("нет-такого") is None

    async def test_empty_text_ignored(self, store: AdviceStore) -> None:
        await store.put("sig2", "   ", "haiku")
        assert await store.get("sig2") is None


# ── L2 переживает рестарт процесса ───────────────────────────────────────────


class _FakeAccess:
    async def find_by_character(self, character: str) -> SimpleNamespace:
        return SimpleNamespace(discord_id="111")


class _FakeMessages:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def create(self, **kwargs: Any) -> SimpleNamespace:
        self.calls.append(kwargs)
        return SimpleNamespace(
            content=[SimpleNamespace(text="Разбор: спред и ЛоС.")],
            usage=SimpleNamespace(input_tokens=5, output_tokens=7),
        )


class _FakeAnthropic:
    def __init__(self) -> None:
        self.messages = _FakeMessages()


def _triple_mage_env(session: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "bridge_ts": "2026-07-26T12:00:00Z",
        "session_id": session,
        "player_name": "Arenacoach",
        "event": {"type": "ARENA_START", "bracket": "3v3"},
        "match": {
            "bracket": "3v3",
            "enemies": [{"wow_class": "MAGE", "race": "UNKNOWN"}] * 3,
            "allies": [],
            "our_comp_hint": "rogue+mage+priest",
            "player_class": "ROGUE",
        },
    }


async def test_l2_survives_process_restart(
    kb_dir: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    dms: list[str] = []

    async def _dm(bot_token: str, discord_id: str, content: str) -> bool:
        dms.append(content)
        return True

    monkeypatch.setattr(pipeline, "_send_discord_dm", _dm)

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/coach.db", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory: async_sessionmaker[AsyncSession] = async_sessionmaker(engine, expire_on_commit=False)
    shared_store = AdviceStore(factory)
    client = _FakeAnthropic()

    def _mk_ctx() -> pipeline.PipelineContext:
        index = KBIndex()
        index.load(kb_dir)
        return pipeline.PipelineContext(
            access_service=_FakeAccess(),  # type: ignore[arg-type]
            kb_retriever=KBRetriever(index),
            anthropic_client=client,
            settings=Settings(discord_bot_token="t", anthropic_api_key="sk-test"),
            advice_store=shared_store,
        )

    # процесс №1: генерит и пишет L2
    ctx1 = _mk_ctx()
    await pipeline.process_event(ctx1, _triple_mage_env("s1"))
    await ctx1.drain_bg()
    assert len(client.messages.calls) == 1
    assert await shared_store.count() == 1

    # «рестарт»: свежий ctx (пустой L1-кэш), тот же L2
    ctx2 = _mk_ctx()
    assert len(ctx2.advice_cache) == 0
    await pipeline.process_event(ctx2, _triple_mage_env("s2"))
    await ctx2.drain_bg()
    assert len(client.messages.calls) == 1  # L2-хит → модель НЕ звалась повторно
    assert "🧠" in dms[-1]


# ── warm-advice parsing ──────────────────────────────────────────────────────


def test_parse_warm_line_class_and_spec() -> None:
    from arena_coach.__main__ import _parse_warm_line

    our, enemies = _parse_warm_line("rogue+mage vs ret-paladin+warrior")
    assert our == "rogue+mage"
    assert enemies == [("PALADIN", "ret-paladin"), ("WARRIOR", None)]


def test_parse_warm_line_enemies_only() -> None:
    from arena_coach.__main__ import _parse_warm_line

    our, enemies = _parse_warm_line("mage+mage+mage")
    assert our is None
    assert enemies == [("MAGE", None), ("MAGE", None), ("MAGE", None)]
