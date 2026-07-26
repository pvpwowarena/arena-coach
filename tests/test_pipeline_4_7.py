"""Phase 4.7 pipeline: детерминированный горячий путь + LLM вне его.

Покрываем без Discord/сети (моки):
  • угрозы попадают в ARENA_START DM (любой сетап);
  • нестандартный сетап без ключа → эвристика+угрозы (floor), без фоновых задач;
  • нестандартный сетап с ключом → фоновой LLM-разбор, кэш, второй DM, учёт токенов;
  • кэш: повторная встреча того же сетапа — без нового вызова модели;
  • постматч с ключом → LLM-разбор + учёт токенов (модель synth);
  • дедуп ARENA_START при неизменном разборе.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from arena_coach.access.models import Base
from arena_coach.access.usage import UsageService
from arena_coach.kb.indexer import KBIndex
from arena_coach.kb.retriever import KBRetriever
from arena_coach.orchestrator import pipeline
from arena_coach.shared.settings import Settings


class _FakeAccess:
    async def find_by_character(self, character: str) -> SimpleNamespace:
        return SimpleNamespace(discord_id="111")


class _FakeMessages:
    def __init__(self, text: str) -> None:
        self.text = text
        self.calls: list[dict[str, Any]] = []

    async def create(self, **kwargs: Any) -> SimpleNamespace:
        self.calls.append(kwargs)
        return SimpleNamespace(
            content=[SimpleNamespace(text=self.text)],
            usage=SimpleNamespace(input_tokens=12, output_tokens=34),
        )


class _FakeAnthropic:
    def __init__(self, text: str = "🎯 Килл-таргет: mage.\nПлан: спред, ЛоС на нову.") -> None:
        self.messages = _FakeMessages(text)


async def _make_usage(tmp_path: Path) -> UsageService:
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/coach.db", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory: async_sessionmaker[AsyncSession] = async_sessionmaker(engine, expire_on_commit=False)
    return UsageService(factory)


def _ctx(
    kb_dir: Path,
    *,
    key: str,
    client: Any = None,
    usage: UsageService | None = None,
) -> pipeline.PipelineContext:
    index = KBIndex()
    index.load(kb_dir)
    return pipeline.PipelineContext(
        access_service=_FakeAccess(),  # type: ignore[arg-type]
        kb_retriever=KBRetriever(index),
        anthropic_client=client if client is not None else SimpleNamespace(),
        settings=Settings(discord_bot_token="t", discord_voice_channel_id=0, anthropic_api_key=key),
        usage_service=usage,
    )


def _env(
    enemies: list[dict[str, str]],
    *,
    our: str,
    bracket: str = "2v2",
    session: str = "s1",
    event: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ev = event or {"type": "ARENA_START", "bracket": bracket}
    return {
        "schema_version": 1,
        "bridge_ts": "2026-07-26T12:00:00Z",
        "session_id": session,
        "player_name": "Arenacoach",
        "event": ev,
        "match": {
            "bracket": bracket,
            "enemies": enemies,
            "allies": [],
            "our_comp_hint": our,
            "player_class": "ROGUE",
        },
    }


ROGUE_MAGE = [
    {"wow_class": "ROGUE", "race": "UNKNOWN"},
    {"wow_class": "MAGE", "race": "UNKNOWN"},
]
TRIPLE_MAGE = [
    {"wow_class": "MAGE", "race": "UNKNOWN"},
    {"wow_class": "MAGE", "race": "UNKNOWN"},
    {"wow_class": "MAGE", "race": "UNKNOWN"},
]


@pytest.fixture
def dms(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    sent: list[str] = []

    async def _dm(bot_token: str, discord_id: str, content: str) -> bool:
        sent.append(content)
        return True

    async def _voice(settings: Settings, text: str) -> bool:
        return False

    monkeypatch.setattr(pipeline, "_send_discord_dm", _dm)
    monkeypatch.setattr(pipeline, "_send_voice_hint", _voice)
    return sent


class TestThreatsAndDeterministicFloor:
    async def test_kb_dm_includes_threats(self, kb_dir: Path, dms: list[str]) -> None:
        ctx = _ctx(kb_dir, key="")
        r = await pipeline.process_event(ctx, _env(ROGUE_MAGE, our="rogue+warlock"))
        assert r == "sent"
        assert len(dms) == 1
        assert "шаттер" in dms[0]  # угроза мага
        assert "🎯 Килл-таргет" in dms[0]

    async def test_unknown_comp_floor_without_key(self, kb_dir: Path, dms: list[str]) -> None:
        ctx = _ctx(kb_dir, key="")
        r = await pipeline.process_event(
            ctx, _env(TRIPLE_MAGE, our="rogue+mage+priest", bracket="3v3")
        )
        assert r == "sent"
        assert len(dms) == 1  # только мгновенный floor, без фонового LLM
        assert "Нестандартный сетап" in dms[0]
        assert "эвристика" in dms[0]
        assert "**mage**" in dms[0]  # эвристический килл-таргет
        await ctx.drain_bg()
        assert len(dms) == 1  # фоновых задач не было


class TestUnknownCompLLM:
    async def test_generates_caches_and_second_dm(
        self, kb_dir: Path, tmp_path: Path, dms: list[str]
    ) -> None:
        usage = await _make_usage(tmp_path)
        client = _FakeAnthropic()
        ctx = _ctx(kb_dir, key="sk-test", client=client, usage=usage)

        r = await pipeline.process_event(
            ctx, _env(TRIPLE_MAGE, our="rogue+mage+priest", bracket="3v3")
        )
        assert r == "sent"
        assert len(dms) == 1
        assert "Генерю разбор" in dms[0]

        await ctx.drain_bg()
        assert len(dms) == 2
        assert "Разбор" in dms[1]
        assert len(ctx.advice_cache) == 1
        summary = await usage.summary()
        assert summary.calls == 1
        assert summary.buckets[0].purpose == "advice"

    async def test_cache_hit_skips_second_call(
        self, kb_dir: Path, tmp_path: Path, dms: list[str]
    ) -> None:
        usage = await _make_usage(tmp_path)
        client = _FakeAnthropic()
        ctx = _ctx(kb_dir, key="sk-test", client=client, usage=usage)

        await pipeline.process_event(
            ctx, _env(TRIPLE_MAGE, our="rogue+mage+priest", bracket="3v3", session="s1")
        )
        await ctx.drain_bg()
        calls_after_first = len(client.messages.calls)

        # тот же сетап, другая сессия (обходим дедуп) → кэш-хит, без нового вызова
        await pipeline.process_event(
            ctx, _env(TRIPLE_MAGE, our="rogue+mage+priest", bracket="3v3", session="s2")
        )
        await ctx.drain_bg()
        assert len(client.messages.calls) == calls_after_first  # модель не звалась второй раз
        assert "🧠" in dms[-1]  # кэшированный разбор в мгновенном DM


class TestPostmatchLLM:
    async def test_llm_review_and_usage(self, kb_dir: Path, tmp_path: Path, dms: list[str]) -> None:
        usage = await _make_usage(tmp_path)
        client = _FakeAnthropic(text="1) Ваниш слил рано — держи под тринкет.")
        ctx = _ctx(kb_dir, key="sk-test", client=client, usage=usage)

        await pipeline.process_event(ctx, _env(ROGUE_MAGE, our="rogue+warlock"))
        await pipeline.process_event(
            ctx,
            _env(
                ROGUE_MAGE,
                our="rogue+warlock",
                event={
                    "type": "TRINKET",
                    "source_name": "Frostee",
                    "spell_id": 42292,
                    "trinket_key": "pvp_trinket",
                },
            ),
        )
        r = await pipeline.process_event(
            ctx,
            _env(ROGUE_MAGE, our="rogue+warlock", event={"type": "ARENA_END", "event_count": 1}),
        )
        assert r == "sent"
        assert "Разбор тренера" in dms[-1]
        assert "Ваниш слил рано" in dms[-1]
        summary = await usage.summary()
        assert any(b.purpose == "postmatch" for b in summary.buckets)

    async def test_postmatch_falls_back_when_llm_errors(
        self, kb_dir: Path, tmp_path: Path, dms: list[str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        usage = await _make_usage(tmp_path)
        ctx = _ctx(kb_dir, key="sk-test", client=_FakeAnthropic(), usage=usage)

        async def _boom(*args: Any, **kwargs: Any) -> Any:
            raise RuntimeError("modeln't")

        monkeypatch.setattr(pipeline.advice_mod, "generate_postmatch_review", _boom)

        await pipeline.process_event(ctx, _env(ROGUE_MAGE, our="rogue+warlock"))
        await pipeline.process_event(
            ctx,
            _env(
                ROGUE_MAGE,
                our="rogue+warlock",
                event={
                    "type": "TRINKET",
                    "source_name": "Frostee",
                    "spell_id": 42292,
                    "trinket_key": "pvp_trinket",
                },
            ),
        )
        r = await pipeline.process_event(
            ctx,
            _env(ROGUE_MAGE, our="rogue+warlock", event={"type": "ARENA_END", "event_count": 1}),
        )
        assert r == "sent"
        assert "Разбор боя" in dms[-1]  # детерминированный фолбэк


class TestArenaStartDedup:
    async def test_same_signature_not_redelivered(self, kb_dir: Path, dms: list[str]) -> None:
        ctx = _ctx(kb_dir, key="")
        first = await pipeline.process_event(ctx, _env(ROGUE_MAGE, our="rogue+warlock"))
        second = await pipeline.process_event(ctx, _env(ROGUE_MAGE, our="rogue+warlock"))
        assert first == "sent"
        assert second == "skipped"
        assert len(dms) == 1
