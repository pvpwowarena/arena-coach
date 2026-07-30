"""Phase 4.15 — упрощение: Discord-голос снят, боевой DM в opt-in.

Что проверяем:
  • `_send_voice_hint` и `bot.voice` удалены, `Settings` больше не знает про
    `discord_voice_channel_id` — то есть хоп api→bot действительно вырезан, а не
    просто отключён флагом;
  • боевой DM по умолчанию НЕ шлётся (голос при этом идёт), а разбор на воротах и
    постматч приходят всегда;
  • если голоса у игрока нет (`voice off`), боевой текст шлётся ВСЕГДА — иначе он
    остался бы вообще без подсказки. Это главный предохранитель фичи.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from arena_coach.access.player_settings import (
    COMBAT_TEXT_MODES,
    DEFAULT_COMBAT_TEXT,
)
from arena_coach.kb.indexer import KBIndex
from arena_coach.kb.retriever import KBRetriever
from arena_coach.orchestrator import pipeline
from arena_coach.shared.settings import Settings

ROGUE_MAGE = [
    {"wow_class": "ROGUE", "race": "UNKNOWN"},
    {"wow_class": "MAGE", "race": "UNKNOWN"},
]


class _FakeAccess:
    async def find_by_character(self, character: str) -> SimpleNamespace:
        return SimpleNamespace(discord_id="111")


class _Settings:
    def __init__(self, voice_mode: str, combat_text: str) -> None:
        self._voice_mode = voice_mode
        self._combat_text = combat_text

    async def get_voice_mode(self, discord_id: str) -> str:
        return self._voice_mode

    async def get_combat_text(self, discord_id: str) -> str:
        return self._combat_text


def _ctx(kb_dir: Path, voice_mode: str, combat_text: str) -> pipeline.PipelineContext:
    index = KBIndex()
    index.load(kb_dir)
    return pipeline.PipelineContext(
        access_service=_FakeAccess(),  # type: ignore[arg-type]
        kb_retriever=KBRetriever(index),
        anthropic_client=SimpleNamespace(),
        settings=Settings(discord_bot_token="t", anthropic_api_key=""),
        hint_throttle=pipeline.HintThrottle(gap_s=0.0, high_gap_s=0.0, default_repeat_s=0.0),
        player_settings=_Settings(voice_mode, combat_text),  # type: ignore[arg-type]
    )


def _env(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "bridge_ts": "2026-07-30T12:00:00Z",
        "session_id": "s1",
        "player_name": "Arenacoach",
        "event": event,
        "match": {
            "bracket": "2v2",
            "enemies": ROGUE_MAGE,
            "allies": [],
            "our_comp_hint": "rogue+mage",
            "player_class": "ROGUE",
        },
    }


_TRINKET = {"type": "TRINKET", "source_name": "Frosty", "trinket_key": "pvp_trinket"}


@pytest.fixture
def dms(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    sent: list[str] = []

    async def _dm(bot_token: str, discord_id: str, content: str) -> bool:
        sent.append(content)
        return True

    monkeypatch.setattr(pipeline, "_send_discord_dm", _dm)
    return sent


class TestDiscordVoiceRemoved:
    def test_pipeline_has_no_voice_hop(self) -> None:
        assert not hasattr(pipeline, "_send_voice_hint")

    def test_settings_forget_voice_channel(self) -> None:
        assert not hasattr(Settings(), "discord_voice_channel_id")
        assert not hasattr(Settings(), "voice_http_port")

    def test_bot_voice_module_gone(self) -> None:
        with pytest.raises(ModuleNotFoundError):
            __import__("arena_coach.bot.voice")


class TestCombatTextOptIn:
    def test_default_is_off(self) -> None:
        assert DEFAULT_COMBAT_TEXT == "off"
        assert set(COMBAT_TEXT_MODES) == {"on", "off"}

    async def test_in_fight_dm_suppressed_but_voice_still_speaks(
        self, kb_dir: Path, dms: list[str]
    ) -> None:
        ctx = _ctx(kb_dir, voice_mode="on", combat_text="off")
        await pipeline.process_event(ctx, _env({"type": "ARENA_START"}))
        dms.clear()

        r = await pipeline.process_event(ctx, _env(_TRINKET))
        assert r == "sent"
        assert dms == []  # текста в бою нет
        assert ctx.hint_queue.pop_fresh("Arenacoach")  # а голос есть

    async def test_in_fight_dm_sent_when_opted_in(self, kb_dir: Path, dms: list[str]) -> None:
        ctx = _ctx(kb_dir, voice_mode="on", combat_text="on")
        await pipeline.process_event(ctx, _env({"type": "ARENA_START"}))
        dms.clear()

        await pipeline.process_event(ctx, _env(_TRINKET))
        assert len(dms) == 1
        assert "тринкетнул" in dms[0]

    async def test_gates_dm_always_sent(self, kb_dir: Path, dms: list[str]) -> None:
        """Разбор на воротах читают — он не боевой поток и под opt-in не попадает."""
        ctx = _ctx(kb_dir, voice_mode="on", combat_text="off")
        r = await pipeline.process_event(ctx, _env({"type": "ARENA_START"}))
        assert r == "sent"
        assert len(dms) == 1
        assert "Килл-таргет" in dms[0]

    async def test_postmatch_dm_always_sent(self, kb_dir: Path, dms: list[str]) -> None:
        ctx = _ctx(kb_dir, voice_mode="on", combat_text="off")
        await pipeline.process_event(ctx, _env({"type": "ARENA_START"}))
        for _ in range(3):  # POSTMATCH_MIN_EVENTS
            await pipeline.process_event(ctx, _env(_TRINKET))
        dms.clear()

        await pipeline.process_event(ctx, _env({"type": "ARENA_END"}))
        assert len(dms) == 1

    async def test_without_voice_text_survives(self, kb_dir: Path, dms: list[str]) -> None:
        """Главный предохранитель: без голоса игрок не должен остаться ни с чем."""
        ctx = _ctx(kb_dir, voice_mode="off", combat_text="off")
        await pipeline.process_event(ctx, _env({"type": "ARENA_START"}))
        dms.clear()

        await pipeline.process_event(ctx, _env(_TRINKET))
        assert len(dms) == 1
        assert not ctx.hint_queue.pop_fresh("Arenacoach")

    async def test_voice_only_still_suppresses_everything(
        self, kb_dir: Path, dms: list[str]
    ) -> None:
        ctx = _ctx(kb_dir, voice_mode="only", combat_text="on")
        await pipeline.process_event(ctx, _env({"type": "ARENA_START"}))
        assert dms == []
        assert ctx.hint_queue.pop_fresh("Arenacoach")
