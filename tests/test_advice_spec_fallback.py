"""Wave 0: спек-фоллбэк advice-кэша + контент-дедуп ARENA_START.

Сценарий из жизни: на воротах спеки неизвестны → класс-сигнатура попадает в
офлайн-сид (мгновенный разбор, $0). Через несколько секунд мост раскрывает спек
(Chain Heal → resto-shaman), сигнатура сужается и раньше ПРОМАХИВАЛАСЬ мимо
кэша — уходил лишний Haiku-вызов, а игроку прилетал дубль-DM. Теперь:
  • промах спек-сигнатуры → лукап класс-сигнатуры (L1, затем L2);
  • хит → LLM не спавнится, спек-ключ прогревается;
  • дедуп ARENA_START по хешу содержимого — тот же разбор не шлётся дважды,
    а реально новое содержимое (угрозы по спеку в эвристике) шлётся.
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
from arena_coach.orchestrator.advice import comp_signature
from arena_coach.shared.settings import Settings

SEED_TEXT = "🎯 Килл-таргет: шаман — без эскейпов (если элем — тем более он).\nПлан: тотемы."


class _FakeAccess:
    async def find_by_character(self, character: str) -> SimpleNamespace:
        return SimpleNamespace(discord_id="111")


class _FakeMessages:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def create(self, **kwargs: Any) -> SimpleNamespace:
        self.calls.append(kwargs)
        return SimpleNamespace(
            content=[SimpleNamespace(text="LLM-разбор")],
            usage=SimpleNamespace(input_tokens=1, output_tokens=2),
        )


def _ctx(kb_dir: Path, *, key: str = "sk-test", store: AdviceStore | None = None) -> Any:
    index = KBIndex()
    index.load(kb_dir)
    client = SimpleNamespace(messages=_FakeMessages())
    ctx = pipeline.PipelineContext(
        access_service=_FakeAccess(),  # type: ignore[arg-type]
        kb_retriever=KBRetriever(index),
        anthropic_client=client,
        settings=Settings(discord_bot_token="t", anthropic_api_key=key),
        advice_store=store,
    )
    return ctx


async def _make_store(tmp_path: Path) -> AdviceStore:
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/coach.db", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory: async_sessionmaker[AsyncSession] = async_sessionmaker(engine, expire_on_commit=False)
    return AdviceStore(factory)


def _env(
    enemies: list[dict[str, str]],
    *,
    our: str = "mage+rogue",
    bracket: str = "2v2",
    session: str = "s1",
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "bridge_ts": "2026-07-27T12:00:00Z",
        "session_id": session,
        "player_name": "Arenacoach",
        "event": {"type": "ARENA_START", "bracket": bracket},
        "match": {
            "bracket": bracket,
            "enemies": enemies,
            "allies": [],
            "our_comp_hint": our,
            "player_class": "ROGUE",
        },
    }


# mage+shaman нет в KB-фикстурах → путь «нестандартный сетап»
NO_SPECS = [
    {"wow_class": "MAGE", "race": "UNKNOWN"},
    {"wow_class": "SHAMAN", "race": "UNKNOWN"},
]
WITH_SPEC = [
    {"wow_class": "MAGE", "race": "UNKNOWN"},
    {"wow_class": "SHAMAN", "race": "UNKNOWN", "spec": "resto-shaman"},
]

CLASS_SIG = comp_signature("mage+rogue", ["MAGE", "SHAMAN"], None, "2v2")
SPEC_SIG = comp_signature("mage+rogue", ["MAGE", "SHAMAN"], [None, "resto-shaman"], "2v2")


@pytest.fixture
def dms(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    sent: list[str] = []

    async def _dm(bot_token: str, discord_id: str, content: str) -> bool:
        sent.append(content)
        return True

    monkeypatch.setattr(pipeline, "_send_discord_dm", _dm)
    return sent


class TestSpecFallback:
    async def test_spec_miss_falls_back_to_class_seed_in_l1(
        self, kb_dir: Path, dms: list[str]
    ) -> None:
        ctx = _ctx(kb_dir)
        ctx.advice_cache.put(CLASS_SIG, SEED_TEXT)

        r = await pipeline.process_event(ctx, _env(WITH_SPEC))
        await ctx.drain_bg()
        assert r == "sent"
        assert len(dms) == 1
        assert SEED_TEXT in dms[0]
        await ctx.drain_bg()
        assert ctx.anthropic_client.messages.calls == []  # LLM не звали
        assert len(dms) == 1

    async def test_spec_key_warmed_after_fallback(self, kb_dir: Path, dms: list[str]) -> None:
        ctx = _ctx(kb_dir)
        ctx.advice_cache.put(CLASS_SIG, SEED_TEXT)
        await pipeline.process_event(ctx, _env(WITH_SPEC))
        await ctx.drain_bg()
        assert ctx.advice_cache.get(SPEC_SIG) == SEED_TEXT

    async def test_fallback_reads_l2_store(
        self, kb_dir: Path, tmp_path: Path, dms: list[str]
    ) -> None:
        store = await _make_store(tmp_path)
        await store.put(CLASS_SIG, SEED_TEXT, "claude-fable-manual")
        ctx = _ctx(kb_dir, store=store)

        r = await pipeline.process_event(ctx, _env(WITH_SPEC))
        await ctx.drain_bg()
        assert r == "sent"
        assert SEED_TEXT in dms[0]
        await ctx.drain_bg()
        assert ctx.anthropic_client.messages.calls == []
        assert ctx.advice_cache.get(SPEC_SIG) == SEED_TEXT  # L1 прогрет

    async def test_fallback_serves_without_llm_key(self, kb_dir: Path, dms: list[str]) -> None:
        ctx = _ctx(kb_dir, key="")
        ctx.advice_cache.put(CLASS_SIG, SEED_TEXT)
        r = await pipeline.process_event(ctx, _env(WITH_SPEC))
        await ctx.drain_bg()
        assert r == "sent"
        assert SEED_TEXT in dms[0]
        assert "Матчапа в KB нет" not in dms[0]

    async def test_no_fallback_when_nothing_seeded(self, kb_dir: Path, dms: list[str]) -> None:
        ctx = _ctx(kb_dir)
        r = await pipeline.process_event(ctx, _env(WITH_SPEC))
        await ctx.drain_bg()
        assert r == "sent"
        assert "Генерю разбор" in dms[0]  # старое поведение: эвристика + фон-LLM
        await ctx.drain_bg()
        assert len(ctx.anthropic_client.messages.calls) == 1

    async def test_classlevel_lookup_not_duplicated_without_specs(
        self, kb_dir: Path, dms: list[str]
    ) -> None:
        # Без спеков class_sig == sig_key: фоллбэк не делает второй лукап и
        # поведение прежнее (сид отдаётся, LLM молчит).
        ctx = _ctx(kb_dir)
        ctx.advice_cache.put(CLASS_SIG, SEED_TEXT)
        r = await pipeline.process_event(ctx, _env(NO_SPECS))
        await ctx.drain_bg()
        assert r == "sent"
        assert SEED_TEXT in dms[0]
        await ctx.drain_bg()
        assert ctx.anthropic_client.messages.calls == []


class TestContentDedup:
    async def test_spec_reveal_with_same_text_is_not_resent(
        self, kb_dir: Path, dms: list[str]
    ) -> None:
        ctx = _ctx(kb_dir)
        ctx.advice_cache.put(CLASS_SIG, SEED_TEXT)

        r1 = await pipeline.process_event(ctx, _env(NO_SPECS, session="s7"))
        await ctx.drain_bg()
        assert r1 == "sent"
        # re-emit той же сессии: мост раскрыл спек, разбор тот же → дубль не шлём
        r2 = await pipeline.process_event(ctx, _env(WITH_SPEC, session="s7"))
        await ctx.drain_bg()
        assert r2 == "skipped"
        assert len(dms) == 1

    async def test_changed_content_is_resent(self, kb_dir: Path, dms: list[str]) -> None:
        # Первый DM — эвристика (кэш пуст); потом сид «появился» (фон/сосед),
        # содержимое изменилось → re-emit шлём.
        ctx = _ctx(kb_dir, key="")
        r1 = await pipeline.process_event(ctx, _env(NO_SPECS, session="s8"))
        await ctx.drain_bg()
        assert r1 == "sent"
        ctx.advice_cache.put(CLASS_SIG, SEED_TEXT)
        ctx.advice_cache.put(SPEC_SIG, SEED_TEXT)
        r2 = await pipeline.process_event(ctx, _env(WITH_SPEC, session="s8"))
        await ctx.drain_bg()
        assert r2 == "sent"
        assert len(dms) == 2
        assert SEED_TEXT in dms[1]

    async def test_identical_reemit_still_skipped(self, kb_dir: Path, dms: list[str]) -> None:
        ctx = _ctx(kb_dir, key="")
        r1 = await pipeline.process_event(ctx, _env(NO_SPECS, session="s9"))
        await ctx.drain_bg()
        r2 = await pipeline.process_event(ctx, _env(NO_SPECS, session="s9"))
        await ctx.drain_bg()
        assert (r1, r2) == ("sent", "skipped")
        assert len(dms) == 1
