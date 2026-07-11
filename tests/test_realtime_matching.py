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


class TestHintThrottle:
    def test_first_ability_allowed(self) -> None:
        t = HintThrottle()
        assert t.allow_ability("u1", "evasion", now=100.0)

    def test_min_interval_blocks(self) -> None:
        t = HintThrottle(min_interval_s=20.0)
        assert t.allow_ability("u1", "evasion", now=100.0)
        assert not t.allow_ability("u1", "ice_block", now=110.0)  # < 20с
        assert t.allow_ability("u1", "ice_block", now=121.0)  # > 20с

    def test_repeat_key_blocked_longer(self) -> None:
        t = HintThrottle(min_interval_s=20.0, repeat_window_s=60.0)
        assert t.allow_ability("u1", "evasion", now=100.0)
        assert not t.allow_ability("u1", "evasion", now=125.0)  # тот же ключ, < 60с
        assert t.allow_ability("u1", "evasion", now=161.0)  # > 60с

    def test_users_independent(self) -> None:
        t = HintThrottle()
        assert t.allow_ability("u1", "evasion", now=100.0)
        assert t.allow_ability("u2", "evasion", now=101.0)
