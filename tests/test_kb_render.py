"""Тесты KB render: Discord embed из KBDoc (Phase 2)."""

from __future__ import annotations

from datetime import date

import discord

from arena_coach.kb.render import (
    _clean_ability_refs,
    render_matchup_embed,
    render_no_matchup_embed,
)
from arena_coach.kb.schema import (
    Confidence,
    Difficulty,
    KBDoc,
    KillTarget,
    Section,
    SourceFile,
)


def _make_doc(**overrides: object) -> KBDoc:
    defaults: dict[str, object] = {
        "slug": "rm-vs-warrior-rdruid",
        "composition": "rogue+mage",
        "vs": "warrior+resto-druid",
        "difficulty": Difficulty.EASY,
        "kill_target": KillTarget(primary="druid"),
        "sources": [
            SourceFile(
                path="WOW TBC ARENA - Rogue  Mage.md",
                author="Mirlol",
                retrieved=date(2026, 5, 12),
            )
        ],
        "last_reviewed": date(2026, 5, 12),
        "confidence": Confidence.DRAFT,
        "sections": [
            Section(
                title="Opener",
                body_md="Cheap-shot [[ability:cheap-shot]], потом gouge [[ability:gouge]].",
            )
        ],
    }
    defaults.update(overrides)  # type: ignore[arg-type]
    return KBDoc.model_validate(defaults)


def test_render_full_returns_embed() -> None:
    embed = render_matchup_embed(_make_doc(), mode="full")
    assert isinstance(embed, discord.Embed)


def test_render_opener_mode() -> None:
    embed = render_matchup_embed(_make_doc(), mode="opener")
    assert isinstance(embed, discord.Embed)
    field_names = [f.name for f in embed.fields]
    assert any("opener" in n.lower() for n in field_names)


def test_title_contains_both_comps() -> None:
    embed = render_matchup_embed(_make_doc())
    assert "rogue+mage" in embed.title.lower()
    assert "warrior+resto-druid" in embed.title.lower()


def test_difficulty_field_present() -> None:
    embed = render_matchup_embed(_make_doc())
    names = [f.name for f in embed.fields]
    assert any("сложность" in n.lower() for n in names)


def test_clean_ability_refs() -> None:
    result = _clean_ability_refs("[[ability:cheap-shot]] и [[ability:gouge]]")
    assert "[[ability:" not in result
    assert "`cheap-shot`" in result
    assert "`gouge`" in result


def test_no_matchup_embed_with_suggestions() -> None:
    embed = render_no_matchup_embed(
        "rogue+mage", "warrior+rsham", ["`rogue+mage vs warrior+resto-druid`"]
    )
    assert isinstance(embed, discord.Embed)
    assert "rogue+mage" in embed.description


def test_long_section_truncated() -> None:
    doc = _make_doc(sections=[Section(title="Opener", body_md="x" * 2000)])
    embed = render_matchup_embed(doc)
    for field in embed.fields:
        if field.value:
            assert len(field.value) <= 1024


def test_different_difficulties_different_colors() -> None:
    easy = render_matchup_embed(_make_doc(difficulty=Difficulty.EASY))
    hard = render_matchup_embed(_make_doc(difficulty=Difficulty.HARD))
    assert easy.color != hard.color
