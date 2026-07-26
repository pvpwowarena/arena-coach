"""Тесты эвристического килл-таргета (orchestrator/killpriority.py, Phase 4.7)."""

from __future__ import annotations

from arena_coach.orchestrator.killpriority import heuristic_kill_target


def test_empty_returns_none() -> None:
    assert heuristic_kill_target([]) is None


def test_clothie_over_warrior() -> None:
    pick = heuristic_kill_target(["WARRIOR", "MAGE"])
    assert pick is not None
    assert pick.target == "mage"
    assert pick.provisional is True


def test_warlock_top_priority() -> None:
    pick = heuristic_kill_target(["WARLOCK", "MAGE", "HUNTER"])
    assert pick is not None
    assert pick.target == "warlock"


def test_healer_spec_deprioritized() -> None:
    # resto-druid (хилер) не должен выбираться при наличии дпс
    pick = heuristic_kill_target(["DRUID", "HUNTER"], ["resto-druid", None])
    assert pick is not None
    assert pick.target == "hunter"


def test_all_healers_picks_one() -> None:
    pick = heuristic_kill_target(["PALADIN", "DRUID"], ["holy-paladin", "resto-druid"])
    assert pick is not None
    # оба хилеры — всё равно выбираем детерминированно (не None)
    assert pick.target in {"holy-paladin", "resto-druid"}


def test_spec_returned_when_known() -> None:
    pick = heuristic_kill_target(["MAGE"], ["fire-mage"])
    assert pick is not None
    assert pick.target == "fire-mage"


def test_likely_healer_paladin_deprioritized_without_spec() -> None:
    # paladin без спека считается вероятным хилером → уступает магу
    pick = heuristic_kill_target(["PALADIN", "MAGE"])
    assert pick is not None
    assert pick.target == "mage"
