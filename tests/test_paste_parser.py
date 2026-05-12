"""Тесты Mirlol paste-парсера: гарантированный inventory + smoke-валидация драфтов."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from arena_ingest.sources.paste import parse_and_write_drafts, parse_matchups, render_kb_draft


class TestInventory:
    """Контракт: парсер находит 12 RM + 10 RP матчапов в реальных Mirlol-файлах.

    Если эти числа изменятся — значит либо текст исходника обновился (ок, синк inventory),
    либо парсер регрессировал (надо чинить).
    """

    def test_rm_file_yields_12_matchups(self, mirlol_rm_file: Path) -> None:
        matchups = parse_matchups(mirlol_rm_file.read_text(encoding="utf-8"))
        assert len(matchups) == 12, (
            f"Ожидалось 12 матчапов в RM-файле, получено {len(matchups)}. "
            f"Найдено: {[m.enemy_comp_raw for m in matchups]}"
        )

    def test_rp_file_yields_10_matchups(self, mirlol_rp_file: Path) -> None:
        matchups = parse_matchups(mirlol_rp_file.read_text(encoding="utf-8"))
        assert len(matchups) == 10, (
            f"Ожидалось 10 матчапов в RP-файле, получено {len(matchups)}. "
            f"Найдено: {[m.enemy_comp_raw for m in matchups]}"
        )

    def test_rm_file_includes_key_matchups(self, mirlol_rm_file: Path) -> None:
        matchups = parse_matchups(mirlol_rm_file.read_text(encoding="utf-8"))
        enemy_comps = {m.enemy_comp_raw.lower() for m in matchups}
        for expected in [
            "warrior/resto druid",
            "rogue/mage",
            "warlock/priest",  # ← регрессия-кандидат: матчап с Option 1/Option 2 без ###
            "ret paladin/resto shaman",
        ]:
            assert expected in enemy_comps, f"Ожидали матчап {expected!r}"

    def test_difficulty_canonicalized(self, mirlol_rm_file: Path) -> None:
        matchups = parse_matchups(mirlol_rm_file.read_text(encoding="utf-8"))
        # Все difficulty должны быть из канонического набора
        for m in matchups:
            assert m.difficulty_raw in {"easy", "moderate", "hard", "very hard", "mirror"}


class TestRender:
    def test_inline_abilities_converted(self, mirlol_rm_file: Path) -> None:
        matchups = parse_matchups(mirlol_rm_file.read_text(encoding="utf-8"))
        wd = next(m for m in matchups if m.enemy_comp_raw == "Warrior/Resto Druid")
        _slug, content = render_kb_draft(
            matchup=wd,
            our_composition="rogue+mage",
            source_file_path=mirlol_rm_file,
            today=date(2026, 5, 12),
        )
        # Inline ability должна быть сконвертирована
        assert "[[ability:cheap-shot]]" in content
        assert "[[ability:kidney-shot]]" in content
        # Исходный inline-markdown с URL не должен остаться
        assert "render.worldofwarcraft.com/icons" not in content

    def test_slug_format(self, mirlol_rm_file: Path) -> None:
        matchups = parse_matchups(mirlol_rm_file.read_text(encoding="utf-8"))
        wd = next(m for m in matchups if m.enemy_comp_raw == "Warrior/Resto Druid")
        slug, _content = render_kb_draft(
            matchup=wd,
            our_composition="rogue+mage",
            source_file_path=mirlol_rm_file,
            today=date(2026, 5, 12),
        )
        assert slug == "rm-vs-warrior-rdruid"


class TestE2EWrite:
    def test_writes_22_drafts(
        self, mirlol_rm_file: Path, mirlol_rp_file: Path, tmp_path: Path
    ) -> None:
        rm = parse_and_write_drafts(
            source_file=mirlol_rm_file,
            our_composition="rogue+mage",
            output_dir=tmp_path,
        )
        rp = parse_and_write_drafts(
            source_file=mirlol_rp_file,
            our_composition="rogue+priest",
            output_dir=tmp_path,
        )
        assert len(rm) == 12
        assert len(rp) == 10
        # Каждый draft записан и парсится через KBDoc
        from arena_coach.kb.loader import load_kb_doc

        for _slug, path in [*rm, *rp]:
            assert path.is_file()
            doc = load_kb_doc(path)
            assert any(s.title for s in doc.sections)
