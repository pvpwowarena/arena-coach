"""Тесты Phase 4.10: реакции вместо анонса + анти-зацикливание.

Живой тест 2026-07-30 дал три претензии — «зациклило», «ничего полезного»,
«кривоватый перевод». Здесь закрываем первые две:

  • таблица реакций покрывает ВСЕ трекаемые спеллы, реплики короткие и
    императивные (голос читается за секунду, без имён игроков);
  • HintThrottle режет дубли тринкета (мост поднимает по два события на один
    спелл) и мелкие КД сразу после стартового разбора;
  • повторный ARENA_START в рамках сессии звучит дельтой («Плюс рога»), а не
    полной стартовой фразой.

Без сети и Discord: доставка глушится, проверяется очередь локального голоса.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from arena_coach.kb.indexer import KBIndex
from arena_coach.kb.retriever import KBRetriever
from arena_coach.orchestrator import pipeline
from arena_coach.orchestrator.reactions import (
    ABILITY_REACTIONS,
    GLOSSARY_GAPS,
    ability_reaction,
    trinket_reaction,
)
from arena_coach.orchestrator.voice_phrases import arena_delta_phrase
from arena_coach.shared.settings import Settings

# ── Таблица реакций ──────────────────────────────────────────────────────────


class TestReactionTable:
    def test_covers_every_hinted_spell(self) -> None:
        """_ABILITY_HINT_KEYS выводится из таблицы — хинт без реакции невозможен."""
        assert set(pipeline._ABILITY_HINT_KEYS) == set(ABILITY_REACTIONS)
        for key in pipeline._ABILITY_HINT_KEYS:
            assert ability_reaction(key) is not None

    def test_voice_is_short_and_actionable(self) -> None:
        """Голос — реакция, а не анонс: ≤9 слов и без «у <ник>»."""
        for key, reaction in ABILITY_REACTIONS.items():
            words = reaction.voice.split()
            assert len(words) <= 9, f"{key}: слишком длинная реплика ({len(words)} слов)"
            assert reaction.voice.endswith((".", "!")), key
            assert " у " not in reaction.voice, f"{key}: голос не должен называть ник"
            assert reaction.dm and reaction.dm != reaction.voice, key

    def test_trinket_reaction_says_what_to_do(self) -> None:
        reaction = trinket_reaction()
        assert "контроль" in reaction.voice.lower()
        assert reaction.voice != "Тринкет у X!"

    def test_gaps_have_no_invented_numbers(self) -> None:
        """У способностей без записи в abilities.json не выдумываем секунды."""
        for key in GLOSSARY_GAPS:
            assert key in ABILITY_REACTIONS
            assert "с на" not in ABILITY_REACTIONS[key].dm
            assert "сек" not in ABILITY_REACTIONS[key].voice


# ── HintThrottle ─────────────────────────────────────────────────────────────


class TestHintThrottle:
    def test_duplicate_trinket_event_suppressed(self) -> None:
        """Мост поднимает TRINKET дважды (cast_success + aura_applied) — второй режем."""
        th = pipeline.HintThrottle(trinket_window_s=45.0)
        assert th.allow("111", "TRINKET", "Cekraj", now=100.0)
        assert not th.allow("111", "TRINKET", "Cekraj", now=100.2)
        # другой враг тринкетнул — это отдельное важное событие
        assert th.allow("111", "TRINKET", "Frosty", now=100.3)
        # тот же враг за окном (тринкет на 2 мин КД) — снова пропускаем
        assert th.allow("111", "TRINKET", "Cekraj", now=150.0)

    def test_trinket_source_case_insensitive(self) -> None:
        th = pipeline.HintThrottle()
        assert th.allow("111", "TRINKET", "Cekraj", now=1.0)
        assert not th.allow("111", "TRINKET", "cekraj", now=2.0)

    def test_ability_quiet_window_after_any_hint(self) -> None:
        """Сразу после стартового разбора мелкий КД не лезет в уши."""
        th = pipeline.HintThrottle(quiet_after_hint_s=5.0)
        assert th.allow("111", "ARENA_START", "", now=10.0)
        assert not th.allow("111", "ABILITY", "vanish", now=12.0)
        assert th.allow("111", "ABILITY", "vanish", now=16.0)

    def test_ability_min_interval_and_repeat_window(self) -> None:
        th = pipeline.HintThrottle(min_interval_s=20.0, repeat_window_s=60.0)
        assert th.allow("111", "ABILITY", "vanish", now=100.0)
        assert not th.allow("111", "ABILITY", "blind", now=110.0)  # общий интервал
        assert th.allow("111", "ABILITY", "blind", now=125.0)
        assert not th.allow("111", "ABILITY", "vanish", now=150.0)  # тот же ключ в окне
        assert th.allow("111", "ABILITY", "vanish", now=165.0)

    def test_arena_start_not_throttled(self) -> None:
        """Доуточнение состава важнее анти-спама — его режет дельта, не троттл."""
        th = pipeline.HintThrottle()
        assert th.allow("111", "ARENA_START", "", now=1.0)
        assert th.allow("111", "ARENA_START", "", now=1.5)

    def test_players_isolated(self) -> None:
        th = pipeline.HintThrottle()
        assert th.allow("111", "ABILITY", "vanish", now=1.0)
        assert th.allow("222", "ABILITY", "vanish", now=1.0)

    def test_legacy_allow_ability_wrapper(self) -> None:
        th = pipeline.HintThrottle(min_interval_s=20.0)
        assert th.allow_ability("111", "vanish", now=1.0)
        assert not th.allow_ability("111", "blind", now=5.0)


# ── Дельта-анонс состава ─────────────────────────────────────────────────────


class TestArenaDeltaPhrase:
    def test_delta_lists_only_new_classes(self) -> None:
        assert arena_delta_phrase(["ROGUE"], "priest") == "Плюс рога. Килл таргет — прист."

    def test_delta_without_kill_target(self) -> None:
        assert arena_delta_phrase(["DRUID"], None) == "Плюс дру."

    def test_delta_without_new_classes(self) -> None:
        assert arena_delta_phrase([], "mage") == "Килл таргет — маг."

    def test_delta_fallback(self) -> None:
        assert arena_delta_phrase([], None) == "Состав уточнён."


# ── pipeline: голос при доуточнении состава ──────────────────────────────────


class _FakeAccess:
    async def find_by_character(self, character: str) -> SimpleNamespace:
        return SimpleNamespace(discord_id="111")


class _FakePlayerSettings:
    async def get_voice_mode(self, discord_id: str) -> str:
        return "on"


def _ctx(kb_dir: Path, throttle: pipeline.HintThrottle | None = None) -> pipeline.PipelineContext:
    index = KBIndex()
    index.load(kb_dir)
    return pipeline.PipelineContext(
        hint_throttle=throttle or pipeline.HintThrottle(),
        access_service=_FakeAccess(),  # type: ignore[arg-type]
        kb_retriever=KBRetriever(index),
        anthropic_client=SimpleNamespace(),  # type: ignore[arg-type]
        settings=Settings(discord_bot_token="t", discord_voice_channel_id=0, kb_path=kb_dir),
        player_settings=_FakePlayerSettings(),  # type: ignore[arg-type]
    )


def _envelope(enemies: list[dict[str, str]], ts: str) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "bridge_ts": ts,
        "session_id": "s1",
        "player_name": "Arenacoach",
        "event": {"type": "ARENA_START", "bracket": "2v2"},
        "match": {
            "bracket": "2v2",
            "enemies": enemies,
            "allies": [],
            "our_comp_hint": "rogue+warlock",
            "player_class": "ROGUE",
        },
    }


@pytest.fixture
def _no_delivery(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _dm(bot_token: str, discord_id: str, content: str) -> bool:
        return True

    async def _voice(settings: Settings, text: str) -> bool:
        return False

    monkeypatch.setattr(pipeline, "_send_discord_dm", _dm)
    monkeypatch.setattr(pipeline, "_send_voice_hint", _voice)


class TestPipelineRefinement:
    async def test_reemit_speaks_delta_not_full_phrase(
        self, kb_dir: Path, _no_delivery: None
    ) -> None:
        """Рога вышла из стелса → «Плюс рога», а не вся стартовая фраза заново."""
        ctx = _ctx(kb_dir)
        first = _envelope([{"wow_class": "MAGE", "race": "UNKNOWN"}], "2026-07-24T12:00:00Z")
        await pipeline.process_event(ctx, first)
        opener = ctx.hint_queue.pop_fresh("Arenacoach")
        assert opener and opener[0].startswith("Арена.")

        second = _envelope(
            [
                {"wow_class": "MAGE", "race": "UNKNOWN"},
                {"wow_class": "ROGUE", "race": "UNKNOWN"},
            ],
            "2026-07-24T12:00:05Z",
        )
        await pipeline.process_event(ctx, second)
        delta = ctx.hint_queue.pop_fresh("Arenacoach")
        assert delta, "доуточнение состава должно озвучиваться"
        assert delta[0].startswith("Плюс рога.")
        assert "Против" not in delta[0]

    async def test_ability_reaction_queued_not_announcement(
        self, kb_dir: Path, _no_delivery: None
    ) -> None:
        # Троттл здесь не проверяем (у него свои тесты) — окно тишины выключено,
        # иначе ABILITY через доли реальной секунды после старта будет подавлен.
        ctx = _ctx(kb_dir, pipeline.HintThrottle(min_interval_s=0.0, quiet_after_hint_s=0.0))
        start = _envelope(
            [
                {"wow_class": "ROGUE", "race": "UNKNOWN"},
                {"wow_class": "MAGE", "race": "UNKNOWN"},
            ],
            "2026-07-24T12:00:00Z",
        )
        await pipeline.process_event(ctx, start)
        ctx.hint_queue.pop_fresh("Arenacoach")

        env = _envelope(
            [
                {"wow_class": "ROGUE", "race": "UNKNOWN"},
                {"wow_class": "MAGE", "race": "UNKNOWN"},
            ],
            "2026-07-24T12:00:40Z",
        )
        env["event"] = {"type": "ABILITY", "source_name": "Frosty", "spell_key": "ice_block"}
        assert await pipeline.process_event(ctx, env) == "sent"
        queued = ctx.hint_queue.pop_fresh("Arenacoach")
        assert queued == [ABILITY_REACTIONS["ice_block"].voice]
        assert "Frosty" not in queued[0]
