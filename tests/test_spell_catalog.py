"""Тесты Phase 4.12: каталог способностей на бэкенде + произношение.

Живой тест 30.07 (третья итерация): «попался хант — весь бой тишина» и «некоторые
ударения и произношения некорректные». Первое оказалось архитектурным: список
важных спеллов был зашит в бинарь моста и покрывал 7 классов из 9. Теперь мост
форвардит все касты (id + slug имени), а решает каталог
`kb/glossary/realtime_spells.json` — то есть новый класс добавляется правкой
данных, без релиза.

Проверяем: резолв по id/ключу/имени, покрытие категорий реакциями, что хант и
шаман больше не молчат, и что словарь произношения меняет только голос.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from arena_coach.kb.indexer import KBIndex
from arena_coach.kb.pronunciation import Pronouncer
from arena_coach.kb.retriever import KBRetriever
from arena_coach.kb.spells import SpellCatalog, slugify
from arena_coach.orchestrator import pipeline
from arena_coach.orchestrator.reactions import (
    CAST_REACTIONS,
    CATEGORY_REACTIONS,
    category_reaction,
)
from arena_coach.shared.settings import Settings

# ── SpellCatalog ─────────────────────────────────────────────────────────────

_SPELLS = {
    "kidney_shot": {"category": "stun", "class": "ROGUE", "ids": [408], "names": ["Kidney Shot"]},
    "scatter_shot": {"category": "incapacitate", "class": "HUNTER", "names": ["Scatter Shot"]},
}


class TestSlugify:
    def test_basic(self) -> None:
        assert slugify("Scatter Shot") == "scatter_shot"

    def test_apostrophe_and_case(self) -> None:
        assert slugify("Nature's Swiftness") == "nature_s_swiftness"

    def test_empty(self) -> None:
        assert slugify("   ") == ""


class TestSpellCatalog:
    def test_resolve_by_id_wins(self) -> None:
        cat = SpellCatalog(_SPELLS)
        info = cat.resolve(spell_id=408, spell_key="что-угодно")
        assert info.key == "kidney_shot" and info.category == "stun"

    def test_resolve_by_key(self) -> None:
        assert SpellCatalog(_SPELLS).resolve(spell_key="scatter_shot").category == "incapacitate"

    def test_resolve_by_english_name(self) -> None:
        """Хант в мосту без id — резолвим по имени из combat-лога."""
        info = SpellCatalog(_SPELLS).resolve(spell_name="Scatter Shot")
        assert info.key == "scatter_shot" and info.wow_class == "HUNTER"

    def test_unknown_returns_slug_without_category(self) -> None:
        info = SpellCatalog(_SPELLS).resolve(spell_name="Some New Spell")
        assert info.key == "some_new_spell" and info.category == ""

    def test_empty_catalog_is_safe(self) -> None:
        assert SpellCatalog().resolve(spell_key="vanish").key == "vanish"

    def test_missing_file_degrades(self, tmp_path: Path) -> None:
        assert len(SpellCatalog.from_kb_path(tmp_path)) == 0

    def test_loads_from_kb_layout(self, tmp_path: Path) -> None:
        glossary = tmp_path / "glossary"
        glossary.mkdir()
        (glossary / "realtime_spells.json").write_text(
            json.dumps({"spells": _SPELLS}), encoding="utf-8"
        )
        assert SpellCatalog.from_kb_path(tmp_path).resolve(spell_id=408).key == "kidney_shot"


class TestRealCatalog:
    """Боевой каталог репо: девять классов и ни одной категории без реакции."""

    def test_covers_hunter_and_shaman(self, kb_dir: Path) -> None:
        cat = SpellCatalog.from_kb_path(kb_dir)
        for name in ("Scatter Shot", "Freezing Trap Effect", "Bestial Wrath", "Silencing Shot"):
            assert cat.resolve(spell_name=name).category, f"хант молчит на {name}"
        for name in ("Bloodlust", "Grounding Totem", "Purge", "Elemental Mastery"):
            assert cat.resolve(spell_name=name).category, f"шаман молчит на {name}"

    def test_every_category_has_reaction(self, kb_dir: Path) -> None:
        """Категория без реакции = молчание на целый класс способностей.

        Категории каста (`heal`, `cast_cc`) живут в CAST_REACTIONS: на них
        предупреждают ДО факта, а состоявшийся хил комментировать поздно.
        """
        raw = json.loads((kb_dir / "glossary" / "realtime_spells.json").read_text(encoding="utf-8"))
        used = {v.get("category") for v in raw["spells"].values() if v.get("category")}
        known = set(CATEGORY_REACTIONS) | set(CAST_REACTIONS)
        missing = sorted(c for c in used if c not in known)
        assert not missing, f"категории без реакции: {missing}"

    def test_cast_alert_entries_have_cast_reaction(self, kb_dir: Path) -> None:
        """Пометил спелл как cast_alert — будь добр иметь на него реплику."""
        raw = json.loads((kb_dir / "glossary" / "realtime_spells.json").read_text(encoding="utf-8"))
        alerts = {k: v for k, v in raw["spells"].items() if v.get("cast_alert")}
        assert alerts, "каталог потерял предупреждения о кастах"
        for key, entry in alerts.items():
            cast_cat = entry.get("cast_category") or entry["category"]
            assert cast_cat in CAST_REACTIONS, key

    def test_known_spells_keep_named_reactions(self, kb_dir: Path) -> None:
        """Каталог не должен переименовывать спеллы, у которых есть своя реплика."""
        cat = SpellCatalog.from_kb_path(kb_dir)
        assert cat.resolve(spell_id=408).key == "kidney_shot"
        assert cat.resolve(spell_id=45438).key == "ice_block"


class TestCategoryReactions:
    def test_generic_reaction_is_actionable(self) -> None:
        for name, reaction in CATEGORY_REACTIONS.items():
            assert len(reaction.voice.split()) <= 8, name
            assert reaction.dm and reaction.voice

    def test_lookup(self) -> None:
        assert category_reaction("stun") is not None
        assert category_reaction("нет-такой") is None


# ── Произношение ─────────────────────────────────────────────────────────────


class TestPronouncer:
    def test_replaces_whole_word_only(self) -> None:
        p = Pronouncer({"рога": "ро́га"})
        assert p.apply("Килл таргет — рога.") == "Килл таргет — ро́га."
        assert p.apply("рогатка") == "рогатка"

    def test_case_insensitive(self) -> None:
        assert Pronouncer({"кс": "ко́нтру"}).apply("КС прошёл") == "ко́нтру прошёл"

    def test_empty_map_is_noop(self) -> None:
        assert Pronouncer().apply("текст") == "текст"

    def test_missing_file_degrades(self, tmp_path: Path) -> None:
        assert len(Pronouncer.from_kb_path(tmp_path)) == 0

    def test_real_dictionary_has_rogue(self, kb_dir: Path) -> None:
        assert "ро" in Pronouncer.from_kb_path(kb_dir).apply("рога")


# ── pipeline: хант больше не молчит ──────────────────────────────────────────


class _FakeAccess:
    async def find_by_character(self, character: str) -> SimpleNamespace:
        return SimpleNamespace(discord_id="111")


class _FakePlayerSettings:
    async def get_voice_mode(self, discord_id: str) -> str:
        return "on"

    async def get_combat_text(self, discord_id: str) -> str:
        # Тесты ниже написаны до Phase 4.15 и проверяют боевой ТЕКСТ, поэтому
        # здесь он включён явно. Прод-дефолт ("off") покрыт test_phase_4_15.py.
        return "on"


def _ctx(kb_dir: Path) -> pipeline.PipelineContext:
    index = KBIndex()
    index.load(kb_dir)
    return pipeline.PipelineContext(
        hint_throttle=pipeline.HintThrottle(gap_s=0.0, high_gap_s=0.0, default_repeat_s=0.0),
        access_service=_FakeAccess(),  # type: ignore[arg-type]
        kb_retriever=KBRetriever(index),
        anthropic_client=SimpleNamespace(),  # type: ignore[arg-type]
        settings=Settings(discord_bot_token="t", kb_path=kb_dir),
        player_settings=_FakePlayerSettings(),  # type: ignore[arg-type]
    )


def _ability(spell_key: str, spell_name: str, spell_id: int = 0) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "bridge_ts": "2026-07-30T02:00:00Z",
        "session_id": "s1",
        "player_name": "Arenacoach",
        "event": {
            "type": "ABILITY",
            "source_name": "Huntard",
            "spell_id": spell_id,
            "spell_key": spell_key,
            "spell_name": spell_name,
        },
        "match": {
            "bracket": "2v2",
            "enemies": [{"wow_class": "HUNTER"}, {"wow_class": "DRUID"}],
            "allies": [],
            "our_comp_hint": "rogue+resto-druid",
            "player_class": "ROGUE",
        },
    }


@pytest.fixture
def _no_delivery(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _dm(bot_token: str, discord_id: str, content: str) -> bool:
        return True

    monkeypatch.setattr(pipeline, "_send_discord_dm", _dm)


class TestPipelineUniversalSpells:
    async def test_hunter_spell_answered_by_category(
        self, kb_dir: Path, _no_delivery: None
    ) -> None:
        """Скаттер-шот ханта: id мосту неизвестен — резолв по имени, ответ по категории."""
        ctx = _ctx(kb_dir)
        env = _ability("scatter_shot", "Scatter Shot")
        assert await pipeline.process_event(ctx, env) == "sent"
        queued = ctx.hint_queue.pop_fresh("Arenacoach")
        assert queued and queued[0] == CATEGORY_REACTIONS["incapacitate"].voice

    async def test_unknown_spell_stays_silent(self, kb_dir: Path, _no_delivery: None) -> None:
        """Незнакомая способность вне каталога — молчим, а не выдумываем совет."""
        ctx = _ctx(kb_dir)
        env = _ability("auto_shot", "Auto Shot")
        assert await pipeline.process_event(ctx, env) == "skipped"
        assert ctx.hint_queue.pop_fresh("Arenacoach") == []

    async def test_named_reaction_beats_category(self, kb_dir: Path, _no_delivery: None) -> None:
        ctx = _ctx(kb_dir)
        env = _ability("", "Ice Block", spell_id=45438)
        assert await pipeline.process_event(ctx, env) == "sent"
        queued = ctx.hint_queue.pop_fresh("Arenacoach")
        assert queued and queued[0].startswith("Блок —")


# ── Стелс: пустой ростер ≠ инвиз (Phase 4.12) ────────────────────────────────


def _arena_start(enemies: list[dict[str, str]], phase: str = "") -> dict[str, Any]:
    return {
        "schema_version": 1,
        "bridge_ts": "2026-07-30T02:00:00Z",
        "session_id": "s-stealth",
        "player_name": "Arenacoach",
        "event": {"type": "ARENA_START", "bracket": "2v2", "phase": phase},
        "match": {
            "bracket": "2v2",
            "enemies": enemies,
            "allies": [],
            "our_comp_hint": "rogue+resto-druid",
            "player_class": "ROGUE",
        },
    }


class TestStealthIsNotIgnorance:
    async def test_gates_are_silent(self, kb_dir: Path, _no_delivery: None) -> None:
        """На воротах состав ещё не раскрыт — это НЕ инвиз, голос молчит."""
        ctx = _ctx(kb_dir)
        assert await pipeline.process_event(ctx, _arena_start([])) == "sent"
        assert ctx.hint_queue.pop_fresh("Arenacoach") == []

    async def test_stealth_marker_announces(self, kb_dir: Path, _no_delivery: None) -> None:
        """А вот явный маркер от моста (6с после ворот, никого) — озвучиваем."""
        ctx = _ctx(kb_dir)
        assert await pipeline.process_event(ctx, _arena_start([], phase="stealth")) == "sent"
        queued = ctx.hint_queue.pop_fresh("Arenacoach")
        assert queued and "не видно" in queued[0]


# ── Предупреждение ДО факта: начало каста (Phase 4.12) ───────────────────────


def _cast(spell_name: str, phase: str) -> dict[str, Any]:
    env = _ability("", spell_name)
    env["event"]["spell_name"] = spell_name
    env["event"]["cast_phase"] = phase
    env["event"]["source_name"] = "Shamy"
    return env


class TestCastAlerts:
    async def test_heal_cast_start_warns(self, kb_dir: Path, _no_delivery: None) -> None:
        """Пока хилер кастует — кик ещё возможен, это и есть «время на решение»."""
        ctx = _ctx(kb_dir)
        assert await pipeline.process_event(ctx, _cast("Healing Wave", "start")) == "sent"
        queued = ctx.hint_queue.pop_fresh("Arenacoach")
        assert queued and queued[0] == CAST_REACTIONS["heal"].voice

    async def test_completed_heal_is_silent(self, kb_dir: Path, _no_delivery: None) -> None:
        """Состоявшийся хил комментировать поздно — молчим."""
        ctx = _ctx(kb_dir)
        assert await pipeline.process_event(ctx, _cast("Healing Wave", "")) == "skipped"
        assert ctx.hint_queue.pop_fresh("Arenacoach") == []

    async def test_ordinary_cast_start_is_silent(self, kb_dir: Path, _no_delivery: None) -> None:
        """Начало каста без пометки cast_alert не предупреждаем — иначе поток шума."""
        ctx = _ctx(kb_dir)
        assert await pipeline.process_event(ctx, _cast("Frost Shock", "start")) == "skipped"

    async def test_cc_cast_start_warns(self, kb_dir: Path, _no_delivery: None) -> None:
        ctx = _ctx(kb_dir)
        assert await pipeline.process_event(ctx, _cast("Polymorph", "start")) == "sent"
        queued = ctx.hint_queue.pop_fresh("Arenacoach")
        assert queued and queued[0] == CAST_REACTIONS["cast_cc"].voice
