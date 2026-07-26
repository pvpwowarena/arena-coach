"""Тесты Phase 4.5: голосовые подсказки.

Покрываем без Discord/сети:
  • voice_phrases — короткие RU-фразы для TTS;
  • VoiceManager.process_hint — троттлинг, TTL, дедуп, LRU-кэш TTS, ошибки TTS;
  • enqueue — дроп при переполнении очереди;
  • PlayerSettingsService — get/set voice_mode (SQLite in-memory);
  • pipeline: режимы on/off/only и best-effort доставка voice-хинта.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from arena_coach.access.models import Base
from arena_coach.access.player_settings import PlayerSettingsService
from arena_coach.bot.voice import QueuedHint, VoiceManager
from arena_coach.kb.indexer import KBIndex
from arena_coach.kb.retriever import KBRetriever
from arena_coach.orchestrator import pipeline
from arena_coach.orchestrator.voice_phrases import (
    ability_phrase,
    arena_start_phrase,
    trinket_phrase,
)
from arena_coach.shared.settings import Settings

# ── voice_phrases ────────────────────────────────────────────────────────────


class TestPhrases:
    def test_arena_start(self) -> None:
        phrase = arena_start_phrase(["WARRIOR", "DRUID"], "druid")
        assert phrase == "Арена. Против вар и дру. Килл таргет — дру."

    def test_arena_start_spec_target(self) -> None:
        assert "дру" in arena_start_phrase(["MAGE"], "resto-druid")

    def test_arena_start_without_target(self) -> None:
        phrase = arena_start_phrase(["MAGE", "ROGUE"], None)
        assert phrase == "Арена. Против маг и рога."

    def test_trinket(self) -> None:
        assert trinket_phrase("Cekraj") == "Тринкет у Cekraj!"
        assert trinket_phrase("") == "Тринкет врага!"

    def test_ability_slang(self) -> None:
        assert ability_phrase("Frostee", "ice_block") == "Айсблок у Frostee!"
        assert ability_phrase("Omgad", "barkskin") == "Кора у Omgad!"

    def test_ability_unknown_key_fallback(self) -> None:
        assert ability_phrase("X", "strange_spell") == "Strange spell у X!"

    def test_phrases_short(self) -> None:
        """Голосовые фразы обязаны быть короткими (риск из phase-4.5-voice.md)."""
        samples = [
            arena_start_phrase(["WARRIOR", "PRIEST", "ROGUE"], "priest"),
            trinket_phrase("Длинноеимяперсонажа"),
            ability_phrase("Длинноеимяперсонажа", "elemental_mastery"),
        ]
        for phrase in samples:
            assert len(phrase.split()) <= 10


# ── VoiceManager ─────────────────────────────────────────────────────────────


class _FakeEngine:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.fail = False

    async def synth(self, text: str) -> bytes:
        self.calls.append(text)
        if self.fail:
            raise RuntimeError("TTS сломан")
        return b"mp3:" + text.encode()


class _TestableManager(VoiceManager):
    """VoiceManager с фейковым проигрыванием (без Discord/ffmpeg)."""

    def __init__(self, **kwargs: Any) -> None:
        self.played: list[bytes] = []
        self.audience = True
        super().__init__(**kwargs)

    async def _play(self, data: bytes) -> bool:
        if not self.audience:
            return False
        self.played.append(data)
        return True


class _Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def _manager(clock: _Clock, engine: _FakeEngine | None = None, **kwargs: Any) -> _TestableManager:
    return _TestableManager(
        bot=None,
        channel_id=42,
        engine=engine or _FakeEngine(),
        clock=clock,
        **kwargs,
    )


class TestVoiceManager:
    async def test_plays_first_hint(self) -> None:
        clock = _Clock()
        m = _manager(clock)
        status = await m.process_hint(QueuedHint("Тринкет у X!", clock.now))
        assert status == "played"
        assert m.played == [b"mp3:" + "Тринкет у X!".encode()]

    async def test_throttle_window(self) -> None:
        clock = _Clock()
        m = _manager(clock, min_interval_s=8.0)
        assert await m.process_hint(QueuedHint("раз", clock.now)) == "played"
        clock.now += 3.0
        assert await m.process_hint(QueuedHint("два", clock.now)) == "throttled"
        clock.now += 6.0  # суммарно 9с от первого
        assert await m.process_hint(QueuedHint("три", clock.now)) == "played"
        assert m.stats.played == 2
        assert m.stats.dropped_throttled == 1

    async def test_stale_hint_dropped(self) -> None:
        clock = _Clock()
        m = _manager(clock, hint_ttl_s=15.0)
        hint = QueuedHint("протухла", clock.now)
        clock.now += 16.0
        assert await m.process_hint(hint) == "stale"
        assert m.played == []

    async def test_duplicate_dropped(self) -> None:
        clock = _Clock()
        m = _manager(clock, min_interval_s=0.0, dedupe_window_s=10.0)
        assert await m.process_hint(QueuedHint("Тринкет у X!", clock.now)) == "played"
        clock.now += 2.0
        assert await m.process_hint(QueuedHint("Тринкет у X!", clock.now)) == "duplicate"
        clock.now += 11.0
        assert await m.process_hint(QueuedHint("Тринкет у X!", clock.now)) == "played"

    async def test_tts_cache(self) -> None:
        clock = _Clock()
        engine = _FakeEngine()
        m = _manager(clock, engine=engine, min_interval_s=0.0, dedupe_window_s=0.0)
        await m.process_hint(QueuedHint("одно и то же", clock.now))
        clock.now += 1.0
        await m.process_hint(QueuedHint("одно и то же", clock.now))
        assert engine.calls == ["одно и то же"]  # второй раз — из кэша

    async def test_tts_error_does_not_mark_played(self) -> None:
        clock = _Clock()
        engine = _FakeEngine()
        engine.fail = True
        m = _manager(clock, engine=engine)
        assert await m.process_hint(QueuedHint("сломается", clock.now)) == "tts_error"
        # TTS упал — окно троттлинга НЕ съедено, следующая фраза пройдёт
        engine.fail = False
        assert await m.process_hint(QueuedHint("работает", clock.now)) == "played"

    async def test_empty_channel_no_audience(self) -> None:
        clock = _Clock()
        m = _manager(clock)
        m.audience = False
        assert await m.process_hint(QueuedHint("в пустоту", clock.now)) == "no_audience"
        assert m.stats.skipped_empty_channel == 1

    async def test_enqueue_overflow_drops(self) -> None:
        clock = _Clock()
        m = _manager(clock, queue_size=2)
        assert m.enqueue("раз")
        assert m.enqueue("два")
        assert not m.enqueue("три")  # очередь полна
        assert m.stats.dropped_full == 1

    async def test_enqueue_empty_rejected(self) -> None:
        clock = _Clock()
        m = _manager(clock)
        assert not m.enqueue("   ")


# ── PlayerSettingsService ────────────────────────────────────────────────────


@pytest.fixture
async def settings_service() -> Any:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    service = PlayerSettingsService(async_sessionmaker(engine, expire_on_commit=False))
    yield service
    await engine.dispose()


class TestPlayerSettings:
    async def test_default_is_on(self, settings_service: PlayerSettingsService) -> None:
        assert await settings_service.get_voice_mode("нет-такого") == "on"

    async def test_set_get_roundtrip(self, settings_service: PlayerSettingsService) -> None:
        await settings_service.set_voice_mode("111", "only")
        assert await settings_service.get_voice_mode("111") == "only"
        await settings_service.set_voice_mode("111", "off")
        assert await settings_service.get_voice_mode("111") == "off"

    async def test_invalid_mode_raises(self, settings_service: PlayerSettingsService) -> None:
        with pytest.raises(ValueError):
            await settings_service.set_voice_mode("111", "громко")


# ── pipeline: режимы голоса ──────────────────────────────────────────────────


class _FakeAccess:
    async def find_by_character(self, character: str) -> SimpleNamespace:
        return SimpleNamespace(discord_id="111")


class _FakePlayerSettings:
    def __init__(self, mode: str) -> None:
        self.mode = mode

    async def get_voice_mode(self, discord_id: str) -> str:
        return self.mode


def _voice_ctx(kb_dir: Path, mode: str, voice_on: bool = True) -> pipeline.PipelineContext:
    index = KBIndex()
    index.load(kb_dir)
    return pipeline.PipelineContext(
        access_service=_FakeAccess(),  # type: ignore[arg-type]
        kb_retriever=KBRetriever(index),
        anthropic_client=SimpleNamespace(),  # type: ignore[arg-type]
        settings=Settings(
            discord_bot_token="t",
            discord_voice_channel_id=555 if voice_on else 0,
        ),
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
            "matchup_slug_hint": "mage-rogue",
        },
    }


@pytest.fixture
def delivery(monkeypatch: pytest.MonkeyPatch) -> dict[str, list[str]]:
    """Перехват обоих каналов доставки + отключение LLM."""
    sent: dict[str, list[str]] = {"dm": [], "voice": []}

    async def _fake_dm(bot_token: str, discord_id: str, content: str) -> bool:
        sent["dm"].append(content)
        return True

    async def _fake_voice(settings: Settings, text: str) -> bool:
        if not settings.discord_voice_channel_id or not text:
            return False
        sent["voice"].append(text)
        return True

    # Phase 4.7: LLM в горячем пути нет; ключ пуст → llm_enabled=False.
    monkeypatch.setattr(pipeline, "_send_discord_dm", _fake_dm)
    monkeypatch.setattr(pipeline, "_send_voice_hint", _fake_voice)
    return sent


class TestPipelineVoiceModes:
    async def test_mode_on_sends_both(self, kb_dir: Path, delivery: dict[str, list[str]]) -> None:
        ctx = _voice_ctx(kb_dir, "on")
        result = await pipeline.process_event(ctx, _start_envelope())
        assert result == "sent"
        assert len(delivery["dm"]) == 1
        assert len(delivery["voice"]) == 1
        assert delivery["voice"][0].startswith("Арена.")
        assert "Килл таргет" in delivery["voice"][0]

    async def test_mode_off_text_only(self, kb_dir: Path, delivery: dict[str, list[str]]) -> None:
        ctx = _voice_ctx(kb_dir, "off")
        result = await pipeline.process_event(ctx, _start_envelope())
        assert result == "sent"
        assert len(delivery["dm"]) == 1
        assert delivery["voice"] == []

    async def test_mode_only_voice_suppresses_text(
        self, kb_dir: Path, delivery: dict[str, list[str]]
    ) -> None:
        ctx = _voice_ctx(kb_dir, "only")
        result = await pipeline.process_event(ctx, _start_envelope())
        assert result == "sent"
        assert delivery["dm"] == []
        assert len(delivery["voice"]) == 1

    async def test_mode_only_falls_back_to_text_when_voice_down(
        self, kb_dir: Path, delivery: dict[str, list[str]]
    ) -> None:
        """Голос недоступен (канал не настроен) → 'only' НЕ оставляет игрока ни с чем."""
        ctx = _voice_ctx(kb_dir, "only", voice_on=False)
        result = await pipeline.process_event(ctx, _start_envelope())
        assert result == "sent"
        assert len(delivery["dm"]) == 1  # fallback на текст
        assert delivery["voice"] == []

    async def test_trinket_voice_phrase(self, kb_dir: Path, delivery: dict[str, list[str]]) -> None:
        ctx = _voice_ctx(kb_dir, "on")
        await pipeline.process_event(ctx, _start_envelope())
        env = _start_envelope()
        env["event"] = {
            "type": "TRINKET",
            "source_name": "Cekraj",
            "spell_id": 42292,
            "trinket_key": "pvp_trinket",
        }
        env["bridge_ts"] = "2026-07-24T12:00:40Z"
        await pipeline.process_event(ctx, env)
        assert delivery["voice"][-1] == "Тринкет у Cekraj!"
