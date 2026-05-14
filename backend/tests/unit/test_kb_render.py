"""Тесты KB render: embed генерация из KBDoc.

Smoke-тесты — проверяем что render не падает и возвращает discord.Embed
с нужными полями. Не проверяем точное содержание (UI-детали могут меняться).
"""

from __future__ import annotations

from datetime import date

import pytest

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
    """Создать минимальный валидный KBDoc для тестов."""
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
                body_md="Cheap-shot друида [[ability:cheap-shot]], потом gouge [[ability:gouge]].",
            )
        ],
    }
    defaults.update(overrides)  # type: ignore[arg-type]
    return KBDoc.model_validate(defaults)


def test_render_matchup_returns_embed() -> None:
    """render_matchup_embed возвращает discord.Embed без исключений."""
    import discord

    doc = _make_doc()
    embed = render_matchup_embed(doc, mode="full")
    assert isinstance(embed, discord.Embed)


def test_render_opener_mode() -> None:
    """mode='opener' возвращает embed с section Opener."""
    import discord

    doc = _make_doc()
    embed = render_matchup_embed(doc, mode="opener")
    assert isinstance(embed, discord.Embed)
    # Должна быть секция opener
    field_names = [f.name for f in embed.fields]
    assert any("opener" in name.lower() for name in field_names)


def test_embed_title_contains_comps() -> None:
    """Title embed содержит оба состава."""
    doc = _make_doc()
    embed = render_matchup_embed(doc)
    assert "rogue+mage" in embed.title.lower()
    assert "warrior+resto-druid" in embed.title.lower()


def test_embed_difficulty_field() -> None:
    """Embed содержит поле «Сложность»."""
    doc = _make_doc()
    embed = render_matchup_embed(doc)
    field_names = [f.name for f in embed.fields]
    assert any("сложность" in name.lower() for name in field_names)


def test_clean_ability_refs() -> None:
    """[[ability:cheap-shot]] → `cheap-shot`."""
    text = "Делаем [[ability:cheap-shot]] и [[ability:kidney-shot]] для CC."
    result = _clean_ability_refs(text)
    assert "[[ability:" not in result
    assert "`cheap-shot`" in result
    assert "`kidney-shot`" in result


def test_render_no_matchup_embed() -> None:
    """render_no_matchup_embed возвращает embed с suggestions."""
    import discord

    embed = render_no_matchup_embed(
        "rogue+mage",
        "warrior+rsham",
        suggestions=["`rogue+mage vs warrior+resto-druid`"],
    )
    assert isinstance(embed, discord.Embed)
    assert "rogue+mage" in embed.description


def test_render_long_section_truncated() -> None:
    """Длинный текст секции обрезается до 1024 символов."""
    long_body = "x" * 2000
    doc = _make_doc(
        sections=[Section(title="Opener", body_md=long_body)]
    )
    embed = render_matchup_embed(doc)
    for field in embed.fields:
        if field.value:
            assert len(field.value) <= 1024
