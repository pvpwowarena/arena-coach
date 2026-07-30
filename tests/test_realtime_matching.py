"""Тесты Phase 4.1: class-level KB-матчинг + троттлинг in-fight подсказок.

Проверяем цепочку «классы врагов из аддона → KB-документ»:
  • comp_part_to_class / comp_to_classes — сведение спек-slug'ов к классам
  • KBIndex.find_by_classes — индекс по базовым классам vs
  • KBRetriever.find_realtime_candidates — включая fallback без нашего состава
  • HintThrottle — анти-спам ABILITY-подсказок
"""

from __future__ import annotations

from pathlib import Path

import pytest

from arena_coach.kb.indexer import KBIndex, comp_part_to_class, comp_to_classes
from arena_coach.kb.retriever import KBRetriever
from arena_coach.orchestrator.pipeline import HintThrottle

# ── comp_part_to_class / comp_to_classes ─────────────────────────────────────


class TestCompToClasses:
    def test_plain_class(self) -> None:
        assert comp_part_to_class("rogue") == "rogue"
        assert comp_part_to_class("WARRIOR") == "warrior"

    def test_spec_slug(self) -> None:
        assert comp_part_to_class("resto-druid") == "druid"
        assert comp_part_to_class("holy-paladin") == "paladin"
        assert comp_part_to_class("shadow-priest") == "priest"
        assert comp_part_to_class("bm-hunter") == "hunter"

    def test_special_boomkin(self) -> None:
        assert comp_part_to_class("boomkin") == "druid"

    def test_unknown_passthrough(self) -> None:
        assert comp_part_to_class("necromancer") == "necromancer"

    def test_comp_to_classes_sorted(self) -> None:
        assert comp_to_classes("warrior+holy-paladin") == ("paladin", "warrior")
        assert comp_to_classes("rogue+mage") == ("mage", "rogue")
        assert comp_to_classes("rogue+mage+priest") == ("mage", "priest", "rogue")


# ── KBIndex.find_by_classes / KBRetriever.find_realtime_candidates ───────────


@pytest.fixture
def loaded_index(kb_dir: Path) -> KBIndex:
    index = KBIndex()
    loaded = index.load(kb_dir)
    if loaded == 0:
        pytest.skip("KB пуста — нечего матчить")
    return index


class TestFindByClasses:
    def test_enemy_classes_match_spec_docs(self, loaded_index: KBIndex) -> None:
        """Враги WARRIOR+PALADIN находят документ vs warrior+holy-paladin."""
        docs = loaded_index.find_by_classes(None, ("paladin", "warrior"))
        assert docs, "rm-vs-warrior-hpala должен матчиться по классам"
        assert any(d.slug == "rm-vs-warrior-hpala" for d in docs)

    def test_our_comp_filters(self, loaded_index: KBIndex) -> None:
        """Фильтр по нашему составу оставляет только rogue+mage документы."""
        docs = loaded_index.find_by_classes(("mage", "rogue"), ("paladin", "warrior"))
        assert docs
        assert all(comp_to_classes(d.composition) == ("mage", "rogue") for d in docs)

    def test_no_match_returns_empty(self, loaded_index: KBIndex) -> None:
        docs = loaded_index.find_by_classes(None, ("shaman", "shaman", "shaman"))
        assert docs == []


class TestFindRealtimeCandidates:
    def test_addon_style_input(self, loaded_index: KBIndex) -> None:
        """Вход как из envelope: классы UPPERCASE, наш состав class-level."""
        r = KBRetriever(loaded_index)
        docs = r.find_realtime_candidates(["WARRIOR", "PALADIN"], "mage+rogue")
        assert docs
        assert any(d.slug == "rm-vs-warrior-hpala" for d in docs)

    def test_fallback_without_our_comp(self, loaded_index: KBIndex) -> None:
        """Наш состав неизвестен (старый аддон) — ищем по любому."""
        r = KBRetriever(loaded_index)
        docs = r.find_realtime_candidates(["WARRIOR", "PALADIN"], None)
        assert docs

    def test_unknown_our_comp_falls_back(self, loaded_index: KBIndex) -> None:
        """Наш состав есть, но таких документов нет — fallback на любой состав."""
        r = KBRetriever(loaded_index)
        docs = r.find_realtime_candidates(["WARRIOR", "PALADIN"], "shaman+shaman")
        assert docs, "должен вернуть кандидатов чужого состава, а не пустоту"

    def test_empty_enemies(self, loaded_index: KBIndex) -> None:
        r = KBRetriever(loaded_index)
        assert r.find_realtime_candidates([], "rogue+mage") == []

    def test_deterministic_order(self, loaded_index: KBIndex) -> None:
        r = KBRetriever(loaded_index)
        a = r.find_realtime_candidates(["WARRIOR", "PALADIN"], None)
        b = r.find_realtime_candidates(["WARRIOR", "PALADIN"], None)
        assert [d.slug for d in a] == [d.slug for d in b]


# ── HintThrottle ─────────────────────────────────────────────────────────────


class TestSpecAwareMatching:
    def test_spec_narrows_out_wrong_spec_doc(self, loaded_index: KBIndex) -> None:
        r = KBRetriever(loaded_index)
        base = r.find_realtime_candidates(["WARRIOR", "PALADIN"], "rogue+mage")
        assert any(d.slug == "rm-vs-warrior-hpala" for d in base)
        # знаем ret → holy-документ исключается (чужой спек = неверный план)
        ret = r.find_realtime_candidates(
            ["WARRIOR", "PALADIN"], "rogue+mage", enemy_specs=[None, "ret-paladin"]
        )
        assert not any(d.slug == "rm-vs-warrior-hpala" for d in ret)
        # знаем holy → документ остаётся
        holy = r.find_realtime_candidates(
            ["WARRIOR", "PALADIN"], "rogue+mage", enemy_specs=[None, "holy-paladin"]
        )
        assert any(d.slug == "rm-vs-warrior-hpala" for d in holy)

    def test_base_class_doc_matches_any_spec(self, loaded_index: KBIndex) -> None:
        # rl-vs-rogue-mage имеет vs rogue+mage (база) → любой спек мага подходит
        r = KBRetriever(loaded_index)
        docs = r.find_realtime_candidates(
            ["ROGUE", "MAGE"], "rogue+warlock", enemy_specs=[None, "fire-mage"]
        )
        assert any(d.slug == "rl-vs-rogue-mage" for d in docs)

    def test_none_specs_no_narrowing(self, loaded_index: KBIndex) -> None:
        r = KBRetriever(loaded_index)
        with_none = r.find_realtime_candidates(
            ["WARRIOR", "PALADIN"], "rogue+mage", enemy_specs=[None, None]
        )
        plain = r.find_realtime_candidates(["WARRIOR", "PALADIN"], "rogue+mage")
        assert [d.slug for d in with_none] == [d.slug for d in plain]


class TestPartialCandidates:
    def test_partial_by_known_class(self, loaded_index: KBIndex) -> None:
        r = KBRetriever(loaded_index)
        docs = r.find_partial_candidates(["DRUID"], "rogue+mage")
        assert docs
        assert all("druid" in comp_to_classes(d.vs) for d in docs)
        assert all(comp_to_classes(d.composition) == ("mage", "rogue") for d in docs)

    def test_partial_empty_when_no_class(self, loaded_index: KBIndex) -> None:
        r = KBRetriever(loaded_index)
        assert r.find_partial_candidates([], "rogue+mage") == []


class TestHintThrottle:
    def test_first_ability_allowed(self) -> None:
        t = HintThrottle()
        assert t.allow_ability("u1", "evasion", now=100.0)

    def test_gap_between_hints(self) -> None:
        """Phase 4.11: общий интервал между репликами — секунды, а не 20с."""
        t = HintThrottle(gap_s=5.0)
        assert t.allow_ability("u1", "evasion", now=100.0)
        assert not t.allow_ability("u1", "ice_block", now=102.0)  # < 5с
        assert t.allow_ability("u1", "ice_block", now=106.0)  # > 5с

    def test_repeat_key_blocked_longer(self) -> None:
        t = HintThrottle(gap_s=5.0, default_repeat_s=60.0)
        assert t.allow_ability("u1", "evasion", now=100.0)
        assert not t.allow_ability("u1", "evasion", now=125.0)  # тот же ключ, < 60с
        assert t.allow_ability("u1", "evasion", now=161.0)  # > 60с

    def test_users_independent(self) -> None:
        t = HintThrottle()
        assert t.allow_ability("u1", "evasion", now=100.0)
        assert t.allow_ability("u2", "evasion", now=101.0)
