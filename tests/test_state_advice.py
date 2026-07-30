"""Фразы по состоянию врага (Phase 4.14).

Критерий приёмки из аудита 30.07: подсказка проходит, если она (1) невидима на
экране, (2) успевает до решения, (3) из неё следует ровно одно действие. Тесты
следят за формой, которая это обеспечивает: короткий императив, без выдуманных
цифр, с ником только когда ник действительно решает.
"""

from __future__ import annotations

import re

from arena_coach.orchestrator.enemy_state import TRINKET, OpenWindow, ReadyAgain
from arena_coach.orchestrator.reactions import HIGH
from arena_coach.orchestrator.state_advice import (
    MIN_RETURN_CD_S,
    kill_target_dm,
    kill_target_voice,
    ready_again_hint,
    trinket_voice,
    window_hint,
)

_DIGITS = re.compile(r"\d")


class TestWindowHint:
    def test_names_the_enemy_and_says_what_to_do(self) -> None:
        hint = window_hint(OpenWindow(enemy="Cekraj", wow_class="ROGUE", spent=(TRINKET, "vanish")))
        assert "Cekraj" in hint.voice
        assert hint.priority == HIGH
        assert len(hint.voice.split()) <= 9
        assert hint.voice.endswith(".")
        assert "рога" in hint.dm  # класс расшифрован по-русски
        assert "тринкет" in hint.dm and "ваниш" in hint.dm

    def test_no_invented_numbers_in_voice(self) -> None:
        """Окно — про «сейчас», а не про остаток секунд, которых мы не знаем."""
        hint = window_hint(OpenWindow(enemy="Cekraj", wow_class="ROGUE", spent=(TRINKET,)))
        assert not _DIGITS.search(hint.voice)

    def test_throttle_key_is_per_enemy(self) -> None:
        a = window_hint(OpenWindow(enemy="Cekraj", wow_class="ROGUE", spent=(TRINKET,)))
        b = window_hint(OpenWindow(enemy="Shadow", wow_class="ROGUE", spent=(TRINKET,)))
        assert a.throttle_key != b.throttle_key

    def test_missing_class_does_not_break_dm(self) -> None:
        hint = window_hint(OpenWindow(enemy="Cekraj", wow_class="", spent=(TRINKET,)))
        assert "Cekraj" in hint.dm


class TestReadyAgainHint:
    def test_small_cooldowns_stay_silent(self) -> None:
        """Кик откатывается каждые 24с — объявлять это значит вернуть «заевшую пластинку»."""
        assert ready_again_hint(ReadyAgain("Cekraj", "kick", cooldown_s=24.0)) is None
        assert ready_again_hint(ReadyAgain("Cekraj", "vanish", cooldown_s=0.0)) is None

    def test_big_cooldown_announced_with_slang_name(self) -> None:
        hint = ready_again_hint(ReadyAgain("Cekraj", "vanish", cooldown_s=180.0))
        assert hint is not None
        assert "ваниш" in hint.voice
        assert "Cekraj" in hint.voice
        assert len(hint.voice.split()) <= 9

    def test_repeat_window_equals_cooldown(self) -> None:
        hint = ready_again_hint(ReadyAgain("Cekraj", "ice_block", cooldown_s=MIN_RETURN_CD_S))
        assert hint is not None
        assert hint.repeat_s == MIN_RETURN_CD_S


class TestTrinketVoice:
    def test_name_only_when_class_duplicated(self) -> None:
        assert trinket_voice("Cekraj", duplicated=False) is None
        voice = trinket_voice("Cekraj", duplicated=True)
        assert voice is not None and "Cekraj" in voice
        assert len(voice.split()) <= 9

    def test_empty_name_falls_back(self) -> None:
        assert trinket_voice("", duplicated=True) is None


class TestKillTargetDisambiguation:
    def test_silent_without_duplicates(self) -> None:
        assert kill_target_voice("ROGUE", ["Cekraj"], []) is None
        assert kill_target_dm("ROGUE", ["Cekraj"], []) is None

    def test_single_exposed_enemy_is_named(self) -> None:
        voice = kill_target_voice("ROGUE", ["Cekraj", "Shadow"], ["Shadow"])
        assert voice is not None
        assert "Shadow" in voice and "Cekraj" not in voice
        dm = kill_target_dm("ROGUE", ["Cekraj", "Shadow"], ["Shadow"])
        assert dm is not None and "**Shadow**" in dm

    def test_criterion_when_nobody_trinketed(self) -> None:
        """Ник без причины игрок не запомнит — отдаём признак выбора."""
        voice = kill_target_voice("ROGUE", ["Cekraj", "Shadow"], [])
        assert voice is not None
        assert "тринкета" in voice.lower()
        assert "Cekraj" not in voice and "Shadow" not in voice

    def test_criterion_when_both_trinketed(self) -> None:
        voice = kill_target_voice("ROGUE", ["Cekraj", "Shadow"], ["Cekraj", "Shadow"])
        assert voice is not None
        assert "рога" in voice

    def test_exposed_outside_class_ignored(self) -> None:
        voice = kill_target_voice("ROGUE", ["Cekraj", "Shadow"], ["Frosty"])
        assert voice is not None
        assert "Frosty" not in voice

    def test_dm_lists_the_whole_roster(self) -> None:
        dm = kill_target_dm("ROGUE", ["Cekraj", "Shadow"], [])
        assert dm is not None
        assert "Cekraj" in dm and "Shadow" in dm


class TestDuplicateAnnounce:
    """«Против рога и рога» звучало как сбой и ничего не сообщало (Phase 4.14)."""

    def test_double_collapsed_into_player_slang(self) -> None:
        from arena_coach.orchestrator.voice_phrases import arena_start_phrase

        assert arena_start_phrase(["ROGUE", "ROGUE"], "rogue") == (
            "Арена. Против дабл рога. Килл таргет — рога."
        )

    def test_triple_collapsed(self) -> None:
        from arena_coach.orchestrator.voice_phrases import arena_start_phrase

        assert "трипл маг" in arena_start_phrase(["MAGE"] * 3, "mage")

    def test_mixed_comp_keeps_order(self) -> None:
        from arena_coach.orchestrator.voice_phrases import arena_start_phrase

        assert "дабл рога и прист" in arena_start_phrase(["ROGUE", "ROGUE", "PRIEST"], "priest")

    def test_unique_classes_unchanged(self) -> None:
        from arena_coach.orchestrator.voice_phrases import arena_start_phrase

        assert arena_start_phrase(["WARRIOR", "DRUID"], "druid") == (
            "Арена. Против вар и дру. Килл таргет — дру."
        )

    def test_empty_roster(self) -> None:
        from arena_coach.orchestrator.voice_phrases import arena_start_phrase

        assert arena_start_phrase([], None) == "Арена."
