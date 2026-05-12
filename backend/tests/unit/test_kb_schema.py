"""Тесты KB pydantic-схемы."""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from arena_coach.kb.schema import (
    Bracket,
    Confidence,
    Difficulty,
    KBDoc,
    KillTarget,
    Section,
    SourceFile,
)


def _make_base_doc(**overrides: object) -> dict[str, object]:
    """Минимальный валидный набор полей для KBDoc."""
    base: dict[str, object] = {
        "slug": "rm-vs-warrior-rdruid",
        "composition": "rogue+mage",
        "vs": "warrior+resto-druid",
        "bracket": Bracket.TWO_V_TWO,
        "difficulty": Difficulty.EASY,
        "kill_target": KillTarget(primary="druid"),
        "sources": [SourceFile(path="test.md", lines="1-10")],
        "last_reviewed": date(2026, 5, 12),
        "sections": [Section(title="Opener", body_md="Open with cheap shot.")],
    }
    base.update(overrides)
    return base


class TestKBDocCreation:
    def test_minimal_valid(self) -> None:
        doc = KBDoc(**_make_base_doc())  # type: ignore[arg-type]
        assert doc.slug == "rm-vs-warrior-rdruid"
        assert doc.confidence == Confidence.DRAFT

    def test_composition_lowercased(self) -> None:
        doc = KBDoc(**_make_base_doc(composition="Rogue+Mage", vs="Warrior+Resto-Druid"))  # type: ignore[arg-type]
        assert doc.composition == "rogue+mage"
        assert doc.vs == "warrior+resto-druid"


class TestKBDocValidation:
    def test_opener_section_required(self) -> None:
        with pytest.raises(ValidationError, match="хотя бы одну секцию"):
            KBDoc(**_make_base_doc(sections=[Section(title="Mid-fight rotation", body_md="x")]))  # type: ignore[arg-type]

    def test_strategy_synonym_accepted(self) -> None:
        # Stealth Game / Strategy / General — синонимы Opener
        for synonym in ["Strategy", "Stealth Game", "General"]:
            doc = KBDoc(**_make_base_doc(sections=[Section(title=synonym, body_md="x")]))  # type: ignore[arg-type]
            assert any(s.title == synonym for s in doc.sections)

    def test_non_draft_requires_reviewer(self) -> None:
        with pytest.raises(ValidationError, match="требует заполненного поля reviewer"):
            KBDoc(**_make_base_doc(confidence=Confidence.HIGH))  # type: ignore[arg-type]

    def test_non_draft_with_reviewer_ok(self) -> None:
        doc = KBDoc(**_make_base_doc(confidence=Confidence.HIGH, reviewer="<vladislav>"))  # type: ignore[arg-type]
        assert doc.reviewer == "<vladislav>"

    def test_sources_non_empty(self) -> None:
        with pytest.raises(ValidationError):
            KBDoc(**_make_base_doc(sources=[]))  # type: ignore[arg-type]

    def test_slug_format(self) -> None:
        with pytest.raises(ValidationError):
            KBDoc(**_make_base_doc(slug="RM-vs-Warrior"))  # type: ignore[arg-type]
        with pytest.raises(ValidationError):
            KBDoc(**_make_base_doc(slug="rm vs warrior"))  # type: ignore[arg-type]

    def test_invalid_composition_format(self) -> None:
        with pytest.raises(ValidationError):
            KBDoc(**_make_base_doc(composition="rogue"))  # type: ignore[arg-type]
        with pytest.raises(ValidationError):
            KBDoc(**_make_base_doc(composition="rogue+"))  # type: ignore[arg-type]

    def test_extra_fields_rejected(self) -> None:
        data = _make_base_doc()
        data["unexpected_field"] = "foo"
        with pytest.raises(ValidationError):
            KBDoc(**data)  # type: ignore[arg-type]
