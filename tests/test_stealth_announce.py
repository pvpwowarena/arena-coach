"""Стелс-анонс: полный инвиз врагов на воротах → предупреждение, а не пустышка.

Раньше при пустом ростере (дабл/трипл-стелс) DM был «видно: ? (состав
уточняется…)», голос — «Арена.» Теперь: явное предупреждение о стелс-опенере
(кучкуйтесь/берегите тринкет) + голосовая фраза; раскрытие первого класса
меняет сигнатуру → прилетает обычное уточнение. LLM в этом пути не участвует.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from arena_coach.kb.indexer import KBIndex
from arena_coach.kb.retriever import KBRetriever
from arena_coach.orchestrator import pipeline
from arena_coach.shared.settings import Settings


class _FakeAccess:
    async def find_by_character(self, character: str) -> SimpleNamespace:
        return SimpleNamespace(discord_id="111")


class _FakeMessages:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def create(self, **kwargs: Any) -> SimpleNamespace:  # pragma: no cover - не зовётся
        self.calls.append(kwargs)
        return SimpleNamespace(
            content=[SimpleNamespace(text="x")],
            usage=SimpleNamespace(input_tokens=0, output_tokens=0),
        )


def _ctx(kb_dir: Path, *, key: str = "sk-test") -> Any:
    index = KBIndex()
    index.load(kb_dir)
    return pipeline.PipelineContext(
        access_service=_FakeAccess(),  # type: ignore[arg-type]
        kb_retriever=KBRetriever(index),
        anthropic_client=SimpleNamespace(messages=_FakeMessages()),
        settings=Settings(discord_bot_token="t", discord_voice_channel_id=0, anthropic_api_key=key),
    )


def _env(enemies: list[dict[str, str]], *, session: str = "s1") -> dict[str, Any]:
    return {
        "schema_version": 1,
        "bridge_ts": "2026-07-27T12:00:00Z",
        "session_id": session,
        "player_name": "Arenacoach",
        "event": {"type": "ARENA_START", "bracket": "2v2"},
        "match": {
            "bracket": "2v2",
            "enemies": enemies,
            "allies": [],
            "our_comp_hint": "mage+rogue",
            "player_class": "ROGUE",
        },
    }


@pytest.fixture
def sent(monkeypatch: pytest.MonkeyPatch) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {"dm": [], "voice": []}

    async def _dm(bot_token: str, discord_id: str, content: str) -> bool:
        out["dm"].append(content)
        return True

    async def _voice(settings: Settings, text: str) -> bool:
        out["voice"].append(text)
        return False

    monkeypatch.setattr(pipeline, "_send_discord_dm", _dm)
    monkeypatch.setattr(pipeline, "_send_voice_hint", _voice)
    return out


class TestStealthAnnounce:
    async def test_empty_roster_warns_about_stealth_opener(
        self, kb_dir: Path, sent: dict[str, list[str]]
    ) -> None:
        ctx = _ctx(kb_dir)
        r = await pipeline.process_event(ctx, _env([]))
        assert r == "sent"
        assert len(sent["dm"]) == 1
        assert "стелс-опенер" in sent["dm"][0]
        assert "Кучкуйтесь" in sent["dm"][0]
        assert "видно: ?" not in sent["dm"][0]
        await ctx.drain_bg()
        assert ctx.anthropic_client.messages.calls == []  # LLM не зовётся

    async def test_empty_roster_voice_phrase(
        self, kb_dir: Path, sent: dict[str, list[str]]
    ) -> None:
        ctx = _ctx(kb_dir)
        await pipeline.process_event(ctx, _env([]))
        assert sent["voice"] == ["Арена. Никого не видно — стелс опенер. Кучкуйтесь."]

    async def test_reemit_empty_is_deduped(self, kb_dir: Path, sent: dict[str, list[str]]) -> None:
        ctx = _ctx(kb_dir)
        r1 = await pipeline.process_event(ctx, _env([], session="s3"))
        r2 = await pipeline.process_event(ctx, _env([], session="s3"))
        assert (r1, r2) == ("sent", "skipped")
        assert len(sent["dm"]) == 1

    async def test_first_reveal_after_stealth_sends_update(
        self, kb_dir: Path, sent: dict[str, list[str]]
    ) -> None:
        ctx = _ctx(kb_dir)
        await pipeline.process_event(ctx, _env([], session="s4"))
        r = await pipeline.process_event(
            ctx, _env([{"wow_class": "ROGUE", "race": "UNKNOWN"}], session="s4")
        )
        assert r == "sent"
        assert len(sent["dm"]) == 2
        assert "видно: ROGUE" in sent["dm"][1]
