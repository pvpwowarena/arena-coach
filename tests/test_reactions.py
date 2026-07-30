"""Тесты Phase 4.10/4.11: реакции вместо анонса + поток подсказок в бою.

Две итерации живого теста 2026-07-30:
  • «зациклило, ничего полезного, кривоватый перевод» → реакции вместо анонса;
  • «нет подсказок по ходу боя, старт + 1-2 реплики за матч» → покрытие всех
    трекаемых мостом спеллов и троттлинг с приоритетами вместо «раз в 20 секунд».

Что проверяем: таблица отвечает на КАЖДЫЙ спелл из TRACKED_SPELLS моста (тест
ловит расхождение автоматически), реплики короткие и без ников, CC пробивает
общий интервал, минутный бюджет ограничивает скороговорку, дубли тринкета
режутся, повторный ARENA_START звучит дельтой.

Без сети и Discord: доставка глушится, проверяется очередь локального голоса.
"""

from __future__ import annotations

import re
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from arena_bridge.combat_tail import TRACKED_SPELLS
from arena_coach.kb.indexer import KBIndex
from arena_coach.kb.retriever import KBRetriever
from arena_coach.orchestrator import pipeline
from arena_coach.orchestrator.reactions import (
    ABILITY_REACTIONS,
    AWAITING_BRIDGE,
    GLOSSARY_GAPS,
    HIGH,
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
            assert not re.search(r"\bу [A-ZА-ЯЁ]", reaction.voice), (
                f"{key}: голос не должен называть ник"
            )
            assert reaction.dm and reaction.dm != reaction.voice, key

    def test_every_tracked_spell_answered(self) -> None:
        """Мост трекает 27 спеллов — на каждый должна быть реакция.

        Именно это расхождение дало «нет подсказок по ходу боя»: вся CC-механика
        (сап, кидни, овца, нова, страх, циклон, подж) доезжала до бэкенда и
        отбрасывалась как skipped, потому что реакции были только на дефы.
        """
        tracked = set(TRACKED_SPELLS.values())
        missing = tracked - set(ABILITY_REACTIONS)
        assert not missing, f"мост шлёт, а ответить нечем: {sorted(missing)}"
        # обратное расхождение допускается только осознанно
        extra = set(ABILITY_REACTIONS) - tracked
        assert extra <= AWAITING_BRIDGE, (
            f"реакция без события моста: {sorted(extra - AWAITING_BRIDGE)}"
        )

    def test_cc_reactions_are_high_priority_and_short_window(self) -> None:
        """CC — это моменты решения: пробивают интервал и повторяются чаще КД."""
        for key in ("kidney_shot", "cyclone", "polymorph", "fear"):
            assert ABILITY_REACTIONS[key].priority == HIGH, key
            assert ABILITY_REACTIONS[key].repeat_s <= 20.0, key

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
        th = pipeline.HintThrottle()
        # приоритет как в pipeline: у тринкета реакция high
        kw = {"priority": HIGH, "repeat_s": 45.0}
        assert th.allow("111", "TRINKET", "Cekraj", now=100.0, **kw)
        assert not th.allow("111", "TRINKET", "Cekraj", now=100.2, **kw)
        # другой враг тринкетнул — отдельное важное событие
        assert th.allow("111", "TRINKET", "Frosty", now=103.0, **kw)
        # тот же враг за окном (тринкет на 2 мин КД) — снова пропускаем
        assert th.allow("111", "TRINKET", "Cekraj", now=150.0, **kw)

    def test_trinket_source_case_insensitive(self) -> None:
        th = pipeline.HintThrottle(default_repeat_s=45.0)
        assert th.allow("111", "TRINKET", "Cekraj", now=1.0)
        assert not th.allow("111", "TRINKET", "cekraj", now=20.0)

    def test_high_priority_breaks_through_gap(self) -> None:
        """Тринкет и стан под добивание не ждут общего интервала."""
        th = pipeline.HintThrottle(gap_s=5.0, high_gap_s=2.5)
        assert th.allow("111", "ABILITY", "barkskin", now=100.0)
        assert not th.allow("111", "ABILITY", "counterspell", now=103.0)  # normal < 5с
        assert th.allow("111", "ABILITY", "kidney_shot", now=103.0, priority="high")

    def test_cc_flows_unlike_before(self) -> None:
        """Регресс на «старт + 1-2 реплики»: разные CC подряд должны проходить."""
        th = pipeline.HintThrottle(gap_s=5.0, high_gap_s=2.5)
        allowed = 0
        for i, key in enumerate(["sap", "cheap_shot", "kidney_shot", "polymorph", "cyclone"]):
            if th.allow("111", "ABILITY", key, now=100.0 + i * 3.0, priority="high"):
                allowed += 1
        assert allowed >= 4

    def test_same_key_repeat_window(self) -> None:
        th = pipeline.HintThrottle(gap_s=1.0)
        assert th.allow("111", "ABILITY", "kidney_shot", now=100.0, repeat_s=20.0)
        assert not th.allow("111", "ABILITY", "kidney_shot", now=115.0, repeat_s=20.0)
        assert th.allow("111", "ABILITY", "kidney_shot", now=121.0, repeat_s=20.0)

    def test_minute_budget_caps_burst(self) -> None:
        """Потолок реплик в минуту — чтобы мясорубка 3v3 не стала скороговоркой."""
        th = pipeline.HintThrottle(gap_s=0.0, high_gap_s=0.0, default_repeat_s=0.0, max_per_min=5)
        allowed = sum(
            1 for i in range(12) if th.allow("111", "ABILITY", f"k{i}", now=100.0 + i * 2.0)
        )
        assert allowed == 5
        # через минуту бюджет восстанавливается
        assert th.allow("111", "ABILITY", "k0", now=200.0)

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
        th = pipeline.HintThrottle(gap_s=5.0)
        assert th.allow_ability("111", "vanish", now=1.0)
        assert not th.allow_ability("111", "blind", now=3.0)


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
        # «ро́га» — с ударением из словаря произношения (Phase 4.12): в очередь
        # голоса кладётся уже озвучиваемый вариант, в DM текст остаётся обычным.
        assert delta[0].startswith("Плюс ро")
        assert "Килл таргет" in delta[0]
        assert "Против" not in delta[0]

    async def test_ability_reaction_queued_not_announcement(
        self, kb_dir: Path, _no_delivery: None
    ) -> None:
        # Троттл здесь не проверяем (у него свои тесты) — паузы выключены, иначе
        # ABILITY через доли реальной секунды после старта будет подавлен.
        ctx = _ctx(kb_dir, pipeline.HintThrottle(gap_s=0.0, high_gap_s=0.0, default_repeat_s=0.0))
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
