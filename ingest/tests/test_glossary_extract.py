"""Тесты экстрактора ability-глоссария."""

from __future__ import annotations

from pathlib import Path

from arena_ingest.glossary_extract import (
    derive_ability_slug,
    extract_abilities,
    extract_from_files,
)


class TestSlugDerivation:
    def test_label_takes_priority(self) -> None:
        slug = derive_ability_slug("cheap shot", "cheap shot to stall hots", "ability_cheapshot")
        assert slug == "cheap-shot"

    def test_label_with_capitals(self) -> None:
        slug = derive_ability_slug("Sap", "Sap the priest", "ability_sap")
        assert slug == "sap"

    def test_falls_back_to_trailing_when_label_empty(self) -> None:
        slug = derive_ability_slug("", "cheap shot", "ability_cheapshot")
        assert slug == "cheap-shot"

    def test_falls_back_to_icon_when_nothing_else(self) -> None:
        slug = derive_ability_slug("", None, "ability_cheapshot")
        # _icon_to_slug продакшен правило: 'ability_cheapshot' → 'cheapshot'
        assert slug == "cheapshot"


class TestExtractAbilities:
    def test_classicons_excluded(self) -> None:
        text = (
            "![druid](https://render.worldofwarcraft.com/icons/56/classicon_druid.jpg)"
            "![cheap shot](https://render.worldofwarcraft.com/icons/56/ability_cheapshot.jpg)cheap shot"
        )
        result = extract_abilities(text)
        assert "cheap-shot" in result
        # classicons не должны попасть
        assert not any(slug.startswith("classicon") for slug in result)

    def test_single_ability(self) -> None:
        text = "![cheap shot](https://render.worldofwarcraft.com/icons/56/ability_cheapshot.jpg)cheap shot"
        result = extract_abilities(text)
        assert "cheap-shot" in result
        entry = result["cheap-shot"]
        assert entry["icon"] == "ability_cheapshot"
        assert "cheap shot" in entry["aliases"]

    def test_aliases_aggregated(self) -> None:
        text = (
            "![cheap shot](https://render.worldofwarcraft.com/icons/56/ability_cheapshot.jpg)cheap shot. "
            "Later: ![cheap shot](https://render.worldofwarcraft.com/icons/56/ability_cheapshot.jpg)CHEAP SHOTTING"
        )
        result = extract_abilities(text)
        assert "cheap-shot" in result
        assert "cheap shot" in result["cheap-shot"]["aliases"]


class TestExtractFromMirlolFiles:
    """Интеграция: реальные файлы продакшен-проекта."""

    def test_rm_file_yields_expected_count(self, mirlol_rm_file: Path) -> None:
        result = extract_abilities(mirlol_rm_file.read_text(encoding="utf-8"))
        # Минимальный sanity-check: должно быть хотя бы 20 уникальных способностей
        assert len(result) >= 20
        # И ключевые точно есть
        for must_have in ["cheap-shot", "kidney-shot", "sap", "blind", "vanish", "premed"]:
            assert must_have in result, f"Ожидали slug {must_have} в глоссарии"

    def test_no_classicons_in_combined_extract(
        self, mirlol_rm_file: Path, mirlol_rp_file: Path
    ) -> None:
        result = extract_from_files([mirlol_rm_file, mirlol_rp_file])
        assert not any("classicon" in slug for slug in result), (
            "Класс-иконки не должны попадать в abilities-глоссарий"
        )
