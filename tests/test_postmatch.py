"""Тесты Phase 4.3: постматч-анализ (MatchRecorder + отчёт + ARENA_END-путь).

Проверяем:
  • MatchRecorder — start/note/finish, re-emit той же сессии, кап событий, TTL;
  • build_postmatch_report — формат, группировка, KB-план, лимит 2000;
  • process_event(ARENA_END) — полный путь до DM (моки Discord/whitelist);
  • normalize_raw(ARENA_END) — envelope уносит session_id/match ДО сброса.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from arena_bridge.normalizer import SessionState, normalize_raw
from arena_coach.kb.indexer import KBIndex
from arena_coach.kb.retriever import KBRetriever
from arena_coach.orchestrator import pipeline
from arena_coach.orchestrator.postmatch import (
    MatchRecord,
    MatchRecorder,
    RecordedEvent,
    build_postmatch_report,
    parse_bridge_ts,
)
from arena_coach.shared.settings import Settings

_T0 = datetime(2026, 7, 24, 12, 0, 0, tzinfo=timezone.utc)


def _ts(offset_s: float) -> datetime:
    return _T0 + timedelta(seconds=offset_s)


# ── parse_bridge_ts ──────────────────────────────────────────────────────────


class TestParseBridgeTs:
    def test_z_suffix(self) -> None:
        parsed = parse_bridge_ts("2026-07-24T12:00:00Z")
        assert parsed == _T0

    def test_garbage(self) -> None:
        assert parse_bridge_ts("не время") is None
        assert parse_bridge_ts("") is None


# ── MatchRecorder ────────────────────────────────────────────────────────────


class TestMatchRecorder:
    def test_start_note_finish(self) -> None:
        rec = MatchRecorder()
        rec.start("Arenacoach", "s1", _T0, "2v2", [{"wow_class": "MAGE"}], "rogue+warlock")
        rec.note("Arenacoach", _ts(41), "TRINKET", "Frostee", "pvp_trinket")
        rec.note("Arenacoach", _ts(70), "ABILITY", "Frostee", "ice_block")
        record = rec.finish("Arenacoach")
        assert record is not None
        assert record.session_id == "s1"
        assert [e.key for e in record.events] == ["pvp_trinket", "ice_block"]
        assert record.events[0].offset_s == pytest.approx(41.0)
        assert record.duration_s() == pytest.approx(70.0)
        # finish изымает запись
        assert rec.finish("Arenacoach") is None

    def test_case_insensitive_player_key(self) -> None:
        rec = MatchRecorder()
        rec.start("Arenacoach", "s1", _T0, "2v2", [], None)
        rec.note("arenacoach", _ts(5), "ABILITY", "X", "fear")
        record = rec.finish("ARENACOACH")
        assert record is not None
        assert len(record.events) == 1

    def test_reemit_same_session_keeps_events(self) -> None:
        """Re-emit ARENA_START (уточнение состава) не сбрасывает таймлайн."""
        rec = MatchRecorder()
        rec.start("P", "s1", _T0, "2v2", [{"wow_class": "MAGE"}], None)
        rec.note("P", _ts(10), "ABILITY", "Frostee", "polymorph")
        rec.start("P", "s1", _ts(12), "2v2", [{"wow_class": "MAGE"}, {"wow_class": "ROGUE"}], None)
        record = rec.finish("P")
        assert record is not None
        assert len(record.events) == 1
        assert record.started_at == _T0  # старт не переехал
        assert record.enemy_classes == ["MAGE", "ROGUE"]

    def test_new_session_replaces_old(self) -> None:
        rec = MatchRecorder()
        rec.start("P", "s1", _T0, "2v2", [], None)
        rec.note("P", _ts(10), "ABILITY", "X", "fear")
        rec.start("P", "s2", _ts(300), "3v3", [], None)
        record = rec.finish("P")
        assert record is not None
        assert record.session_id == "s2"
        assert record.events == []

    def test_note_without_start_ignored(self) -> None:
        rec = MatchRecorder()
        rec.note("P", _T0, "ABILITY", "X", "fear")
        assert rec.finish("P") is None

    def test_event_cap(self) -> None:
        rec = MatchRecorder()
        rec.start("P", "s1", _T0, "2v2", [], None)
        for i in range(400):
            rec.note("P", _ts(i), "ABILITY", "X", "fear")
        record = rec.finish("P")
        assert record is not None
        assert len(record.events) == 300
        assert record.dropped_events == 100

    def test_ttl_purge(self) -> None:
        rec = MatchRecorder()
        rec.start("Old", "s1", _T0, "2v2", [], None)
        rec.start("New", "s2", _ts(3 * 60 * 60), "2v2", [], None)  # +3ч → Old протух
        assert rec.finish("Old") is None
        assert rec.finish("New") is not None


# ── build_postmatch_report ───────────────────────────────────────────────────


def _make_record(**kwargs: Any) -> MatchRecord:
    defaults: dict[str, Any] = {
        "player_name": "Arenacoach",
        "session_id": "s1",
        "started_at": _T0,
        "bracket": "2v2",
        "enemies": [{"wow_class": "ROGUE"}, {"wow_class": "MAGE"}],
        "our_comp_hint": "rogue+warlock",
    }
    defaults.update(kwargs)
    return MatchRecord(**defaults)


@pytest.fixture(scope="module")
def rl_doc() -> Any:
    index = KBIndex()
    if index.load(Path(__file__).resolve().parent.parent / "kb") == 0:
        pytest.skip("KB пуста")
    docs = KBRetriever(index).find_realtime_candidates(["ROGUE", "MAGE"], "rogue+warlock")
    if not docs:
        pytest.skip("rl-vs-rogue-mage не найден в KB")
    return docs[0]


class TestBuildReport:
    def test_report_with_doc(self, rl_doc: Any) -> None:
        record = _make_record(
            events=[
                RecordedEvent(41.0, "TRINKET", "Frostee", "pvp_trinket"),
                RecordedEvent(72.0, "ABILITY", "Frostee", "ice_block"),
                RecordedEvent(80.0, "ABILITY", "Shadowz", "fear"),
                RecordedEvent(95.0, "ABILITY", "Shadowz", "fear"),
            ],
            last_event_at=_ts(95),
        )
        report = build_postmatch_report(record, rl_doc)
        assert "Разбор боя" in report
        assert "Frostee 0:41" in report  # тринкет с таймстампом
        assert "ice block 1:12" in report  # деф с таймстампом
        assert "fear ×2" in report  # CC агрегатом
        assert "Килл-таргет".lower() in report.lower()
        assert "После тринкета" in report  # тринкет был → секция KB
        assert "/matchup our:rogue+warlock vs:rogue+mage" in report
        assert "[[ability:" not in report  # ссылки глоссария вычищены
        assert len(report) <= 2000

    def test_report_without_doc(self) -> None:
        record = _make_record(
            enemies=[{"wow_class": "SHAMAN"}, {"wow_class": "SHAMAN"}],
            events=[RecordedEvent(10.0, "ABILITY", "X", "bloodlust")],
            last_event_at=_ts(10),
        )
        report = build_postmatch_report(record, None)
        assert "Матчапа в KB нет" in report
        assert "SHAMAN" in report

    def test_no_trinket_no_kb_trinket_section(self, rl_doc: Any) -> None:
        record = _make_record(
            events=[RecordedEvent(10.0, "ABILITY", "X", "fear")],
            last_event_at=_ts(10),
        )
        report = build_postmatch_report(record, rl_doc)
        assert "не замечены" in report
        assert "После тринкета" not in report

    def test_report_capped_at_2000(self, rl_doc: Any) -> None:
        events = [
            RecordedEvent(float(i), "ABILITY", f"ОченьДлинноеИмяВрага{i}", "barkskin")
            for i in range(299)
        ]
        record = _make_record(events=events, last_event_at=_ts(299))
        report = build_postmatch_report(record, rl_doc)
        assert len(report) <= 2000


# ── process_event: ARENA_END end-to-end (с моками) ───────────────────────────


class _FakeAccess:
    def __init__(self, known: dict[str, str]) -> None:
        self._known = {k.lower(): v for k, v in known.items()}

    async def find_by_character(self, character: str) -> SimpleNamespace | None:
        discord_id = self._known.get(character.lower())
        return SimpleNamespace(discord_id=discord_id) if discord_id else None


def _ctx(kb_dir: Path, known: dict[str, str]) -> pipeline.PipelineContext:
    index = KBIndex()
    index.load(kb_dir)
    return pipeline.PipelineContext(
        access_service=_FakeAccess(known),  # type: ignore[arg-type]
        kb_retriever=KBRetriever(index),
        anthropic_client=SimpleNamespace(),  # type: ignore[arg-type]
        settings=Settings(discord_bot_token="test-token"),
    )


def _envelope(
    event: dict[str, Any], *, session: str = "s1", ts: str = "2026-07-24T12:00:00Z"
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "bridge_ts": ts,
        "session_id": session,
        "player_name": "Arenacoach",
        "event": event,
        "match": {
            "bracket": "2v2",
            "enemies": [
                {"wow_class": "ROGUE", "race": "UNKNOWN"},
                {"wow_class": "MAGE", "race": "UNKNOWN"},
            ],
            "allies": [],
            "our_comp_hint": "rogue+warlock",
            "player_class": "ROGUE",
            "matchup_slug_hint": "mage-rogue",
        },
    }


@pytest.fixture
def sent_dms(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, str]]:
    sent: list[tuple[str, str]] = []

    async def _fake_dm(bot_token: str, discord_id: str, content: str) -> bool:
        sent.append((discord_id, content))
        return True

    monkeypatch.setattr(pipeline, "_send_discord_dm", _fake_dm)
    return sent


@pytest.fixture
def no_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    """Гарантируем детерминированный путь: даже если ключ где-то просочится,
    LLM-вызовы падают → фолбэк на шаблонный отчёт (Phase 4.7)."""

    async def _fail(*args: Any, **kwargs: Any) -> Any:
        raise RuntimeError("LLM недоступен в тесте")

    monkeypatch.setattr(pipeline.advice_mod, "generate_postmatch_review", _fail)
    monkeypatch.setattr(pipeline.advice_mod, "generate_comp_advice", _fail)


class TestArenaEndPipeline:
    async def test_full_match_report_flow(
        self, kb_dir: Path, sent_dms: list[tuple[str, str]], no_llm: None
    ) -> None:
        ctx = _ctx(kb_dir, {"Arenacoach": "111"})

        r1 = await pipeline.process_event(ctx, _envelope({"type": "ARENA_START", "bracket": "2v2"}))
        assert r1 in ("sent", "no_matchup")
        # CC-каст: в реалтайме skipped, но записан в таймлайн
        r2 = await pipeline.process_event(
            ctx,
            _envelope(
                {
                    "type": "ABILITY",
                    "source_name": "Shadowz",
                    "spell_id": 408,
                    "spell_key": "kidney_shot",
                },
                ts="2026-07-24T12:00:30Z",
            ),
        )
        assert r2 == "skipped"
        r3 = await pipeline.process_event(
            ctx,
            _envelope(
                {
                    "type": "TRINKET",
                    "source_name": "Frostee",
                    "spell_id": 42292,
                    "trinket_key": "pvp_trinket",
                },
                ts="2026-07-24T12:01:10Z",
            ),
        )
        assert r3 == "sent"

        dm_count_before_end = len(sent_dms)
        r4 = await pipeline.process_event(
            ctx, _envelope({"type": "ARENA_END", "event_count": 3}, ts="2026-07-24T12:04:00Z")
        )
        assert r4 == "sent"
        assert len(sent_dms) == dm_count_before_end + 1
        report = sent_dms[-1][1]
        assert "Разбор боя" in report
        assert "kidney shot ×1" in report  # CC попал в разбор, хоть и был skipped
        assert "Frostee 1:10" in report

    async def test_end_without_match_skipped(
        self, kb_dir: Path, sent_dms: list[tuple[str, str]]
    ) -> None:
        ctx = _ctx(kb_dir, {"Arenacoach": "111"})
        result = await pipeline.process_event(
            ctx, _envelope({"type": "ARENA_END", "event_count": 0})
        )
        assert result == "skipped"
        assert sent_dms == []

    async def test_end_with_zero_events_skipped(
        self, kb_dir: Path, sent_dms: list[tuple[str, str]], no_llm: None
    ) -> None:
        ctx = _ctx(kb_dir, {"Arenacoach": "111"})
        await pipeline.process_event(ctx, _envelope({"type": "ARENA_START", "bracket": "2v2"}))
        dm_before = len(sent_dms)
        result = await pipeline.process_event(
            ctx, _envelope({"type": "ARENA_END", "event_count": 0}, ts="2026-07-24T12:01:00Z")
        )
        assert result == "skipped"
        assert len(sent_dms) == dm_before

    async def test_end_unknown_player(
        self, kb_dir: Path, sent_dms: list[tuple[str, str]], no_llm: None
    ) -> None:
        ctx = _ctx(kb_dir, {})
        await pipeline.process_event(ctx, _envelope({"type": "ARENA_START", "bracket": "2v2"}))
        await pipeline.process_event(
            ctx,
            _envelope(
                {"type": "ABILITY", "source_name": "X", "spell_id": 5782, "spell_key": "fear"},
                ts="2026-07-24T12:00:20Z",
            ),
        )
        result = await pipeline.process_event(
            ctx, _envelope({"type": "ARENA_END", "event_count": 1}, ts="2026-07-24T12:02:00Z")
        )
        assert result == "no_player"
        assert sent_dms == []


# ── normalize_raw: ARENA_END уносит session_id и match ───────────────────────


class TestNormalizerArenaEnd:
    def test_arena_end_keeps_session_context(self) -> None:
        session = SessionState()
        start = normalize_raw(
            "ARENA_START#2v2#ROGUE/UNKNOWN,MAGE/UNKNOWN#ROGUE/UNKNOWN", session, "P"
        )
        assert start is not None
        sid = start.session_id
        assert sid

        end = normalize_raw("ARENA_END#7", session, "P")
        assert end is not None
        assert end.session_id == sid  # тот же матч, а не свежий uuid
        assert [e.wow_class for e in end.match.enemies] == ["ROGUE", "MAGE"]

        # А ПОСЛЕ envelope сессия действительно сброшена
        assert session.match.enemies == []
