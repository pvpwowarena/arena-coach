"""Мета-приоры (стелс-предугадывание v1): угадываем состав по частичной инфе.

Статическая таблица весов меты → при частичном раскрытии DM дополняется
строкой «🕵 По мете это чаще всего: …», при полном инвизе — топ стелс-компов.
Детерминированно, LLM не участвует, сигнатуры дедупа не меняются.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from arena_coach.kb.indexer import KBIndex
from arena_coach.kb.retriever import KBRetriever
from arena_coach.orchestrator import pipeline
from arena_coach.orchestrator.meta_comps import guess_line, likely_comps, stealth_comps
from arena_coach.shared.settings import Settings


class TestLikelyComps:
    def test_single_rogue_2v2_top_is_rm(self) -> None:
        got = likely_comps(["ROGUE"], "2v2")
        assert got[0] == (("mage", "rogue"), "Роге/Маг")
        assert len(got) == 2

    def test_multiset_double_rogue_3v3(self) -> None:
        got = likely_comps(["ROGUE", "ROGUE"], "3v3")
        labels = [label for _, label in got]
        assert "Дабл-роге/Друид" in labels  # RMP с одной рогой не подходит
        assert all(comp.count("rogue") >= 2 for comp, _ in got)

    def test_exotic_classes_give_no_guess(self) -> None:
        assert likely_comps(["PALADIN", "PALADIN"], "2v2") == []
        assert guess_line([]) is None

    def test_unknown_bracket_empty(self) -> None:
        assert likely_comps(["ROGUE"], "5v5") == []
        assert stealth_comps("5v5") == []

    def test_stealth_comps_only_stealth_classes(self) -> None:
        for bracket in ("2v2", "3v3"):
            for comp, _ in stealth_comps(bracket):
                assert set(comp) <= {"rogue", "druid"}


class _FakeAccess:
    async def find_by_character(self, character: str) -> SimpleNamespace:
        return SimpleNamespace(discord_id="111")


def _ctx(kb_dir: Path) -> Any:
    index = KBIndex()
    index.load(kb_dir)
    return pipeline.PipelineContext(
        access_service=_FakeAccess(),  # type: ignore[arg-type]
        kb_retriever=KBRetriever(index),
        anthropic_client=SimpleNamespace(),
        settings=Settings(discord_bot_token="t", discord_voice_channel_id=0, anthropic_api_key=""),
    )


def _env(enemies: list[dict[str, str]], *, bracket: str = "2v2") -> dict[str, Any]:
    return {
        "schema_version": 1,
        "bridge_ts": "2026-07-27T12:00:00Z",
        "session_id": "s1",
        "player_name": "Arenacoach",
        "event": {"type": "ARENA_START", "bracket": bracket},
        "match": {
            "bracket": bracket,
            "enemies": enemies,
            "allies": [],
            "our_comp_hint": "mage+rogue",
            "player_class": "ROGUE",
        },
    }


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


class TestMetaPriorsInDm:
    async def test_partial_dm_contains_meta_guess(self, kb_dir: Path, dms: list[str]) -> None:
        ctx = _ctx(kb_dir)
        r = await pipeline.process_event(ctx, _env([{"wow_class": "ROGUE", "race": "UNKNOWN"}]))
        assert r == "sent"
        assert "По мете это чаще всего" in dms[0]
        assert "Роге/Маг" in dms[0]

    async def test_stealth_dm_names_stealth_comps(self, kb_dir: Path, dms: list[str]) -> None:
        ctx = _ctx(kb_dir)
        r = await pipeline.process_event(ctx, _env([], bracket="3v3"))
        assert r == "sent"
        assert "стелс-опенер" in dms[0]
        assert "Дабл-роге/Друид" in dms[0]

    async def test_exotic_partial_has_no_meta_line(self, kb_dir: Path, dms: list[str]) -> None:
        ctx = _ctx(kb_dir)
        r = await pipeline.process_event(
            ctx,
            _env(
                [
                    {"wow_class": "PALADIN", "race": "UNKNOWN"},
                    {"wow_class": "PALADIN", "race": "UNKNOWN"},
                ],
                bracket="3v3",
            ),
        )
        assert r == "sent"
        assert "По мете" not in dms[0]
