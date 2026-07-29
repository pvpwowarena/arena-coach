"""Тесты Phase 4.10: RU-сленг на выходе бота вместо английских вставок.

Претензия живого теста 2026-07-30 — «кривоватый перевод»: в русском тексте DM
стояли английские слова («Рог shadowstep → cheap shot на ханта»), потому что
`[[ability:x]]` разворачивался в слаг с пробелами. Проверяем:

  • `register: standard` → форма команды («кидни», «блайнд»);
  • `register: colloquial` → в вывод НЕ идёт (по схеме slang.json), берём
    корректное `en_name` из abilities.json;
  • резолв через алиасы abilities.json (KB-слаг `kidney-shot` ↔ сленг `kidney`);
  • отсутствие глоссария не роняет рендер (деградация на прежнее поведение);
  • pipeline._clean действительно ходит через рендерер.
"""

from __future__ import annotations

import json
from pathlib import Path

from arena_coach.kb.slang import SlangRenderer
from arena_coach.orchestrator import pipeline

# ── Юнит: резолв имён ────────────────────────────────────────────────────────

_SLANG = {
    "kidney": {"slug": "kidney", "en": "kidney shot", "voice": "кидни", "register": "standard"},
    "cloak": {
        "slug": "cloak",
        "en": "cloak",
        "voice": "клоак",
        "register": "colloquial",  # понимаем на входе, сами не произносим
    },
}
_ABILITIES = {
    "kidney-shot": {"slug": "kidney-shot", "en_name": "Kidney Shot", "aliases": ["kidney"]},
    "cloak-of-shadows": {"slug": "cloak-of-shadows", "en_name": "Cloak of Shadows"},
    "faerie-fire": {"slug": "faerie-fire", "en_name": "Faerie Fire"},
}


class TestSlangRenderer:
    def test_direct_slug_hit(self) -> None:
        assert SlangRenderer(_SLANG, _ABILITIES).name("kidney") == "кидни"

    def test_resolves_via_ability_alias(self) -> None:
        """KB пишет `kidney-shot`, лексикон знает `kidney` — связь через aliases."""
        assert SlangRenderer(_SLANG, _ABILITIES).name("kidney-shot") == "кидни"

    def test_colloquial_not_emitted(self) -> None:
        """`клоак` — только на вход; на выход идёт аккуратное английское имя."""
        assert SlangRenderer(_SLANG, _ABILITIES).name("cloak-of-shadows") == "Cloak of Shadows"

    def test_unknown_slug_uses_en_name(self) -> None:
        assert SlangRenderer(_SLANG, _ABILITIES).name("faerie-fire") == "Faerie Fire"

    def test_unknown_everywhere_falls_back_to_slug(self) -> None:
        assert SlangRenderer(_SLANG, _ABILITIES).name("some-new-spell") == "some new spell"

    def test_render_refs_replaces_all(self) -> None:
        r = SlangRenderer(_SLANG, _ABILITIES)
        text = "Рог [[ability:kidney-shot]] → бурст; [[ability:cloak-of-shadows]] снимает доты."
        assert r.render_refs(text) == "Рог кидни → бурст; Cloak of Shadows снимает доты."

    def test_empty_glossary_is_safe(self) -> None:
        assert SlangRenderer().name("kidney-shot") == "kidney shot"

    def test_missing_files_degrade(self, tmp_path: Path) -> None:
        assert SlangRenderer.from_kb_path(tmp_path).name("kidney-shot") == "kidney shot"

    def test_loads_from_kb_layout(self, tmp_path: Path) -> None:
        glossary = tmp_path / "glossary"
        glossary.mkdir()
        (glossary / "slang.json").write_text(json.dumps(_SLANG), encoding="utf-8")
        (glossary / "abilities.json").write_text(json.dumps(_ABILITIES), encoding="utf-8")
        assert SlangRenderer.from_kb_path(tmp_path).name("kidney-shot") == "кидни"


class TestRealGlossary:
    """Боевой лексикон репо: самые частые ссылки KB должны звучать по-русски."""

    def test_top_refs_are_russian(self, kb_dir: Path) -> None:
        r = SlangRenderer.from_kb_path(kb_dir)
        assert r.name("kidney-shot") == "кидни"
        assert r.name("blind") == "блайнд"
        assert r.name("vanish") == "ваниш"

    def test_no_lowercase_slug_leakage(self, kb_dir: Path) -> None:
        """Не покрытые лексиконом — с большой буквы (имя), а не «cloak of shadows»."""
        assert SlangRenderer.from_kb_path(kb_dir).name("cloak-of-shadows") == "Cloak of Shadows"


# ── Интеграция с pipeline._clean ─────────────────────────────────────────────


class TestCleanUsesSlang:
    def test_clean_with_renderer(self) -> None:
        r = SlangRenderer(_SLANG, _ABILITIES)
        assert pipeline._clean("держи [[ability:kidney-shot]]", 100, r) == "держи кидни"

    def test_clean_without_renderer_keeps_legacy(self) -> None:
        assert pipeline._clean("держи [[ability:kidney-shot]]", 100) == "держи kidney shot"

    def test_clean_still_strips_provenance_and_trims(self) -> None:
        text = "_Провенанс: источник такой-то_\n\n\n\nПлан: [[ability:kidney-shot]] в бурст."
        out = pipeline._clean(text, 200, SlangRenderer(_SLANG, _ABILITIES))
        assert "Провенанс" not in out
        assert out == "План: кидни в бурст."

    def test_clean_respects_limit(self) -> None:
        out = pipeline._clean("a" * 50, 10, SlangRenderer(_SLANG, _ABILITIES))
        assert len(out) == 10 and out.endswith("…")
