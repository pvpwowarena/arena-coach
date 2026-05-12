"""Тесты KB-лоадера: parse .md → KBDoc."""

from __future__ import annotations

from pathlib import Path

import pytest

from arena_coach.kb.loader import (
    GlossaryIndex,
    KBFrontmatterError,
    KBOrphanAbilityError,
    KBSchemaError,
    load_kb_doc,
    validate_directory,
)


class TestLoadKBDoc:
    def test_minimal_valid_loads(self, fixtures_dir: Path) -> None:
        doc = load_kb_doc(fixtures_dir / "minimal_valid.md")
        assert doc.slug == "rm-vs-test-comp"
        assert doc.composition == "rogue+mage"
        assert any(s.title == "Opener" for s in doc.sections)

    def test_missing_frontmatter_raises(self, tmp_path: Path) -> None:
        p = tmp_path / "no-fm.md"
        p.write_text("# Just a heading\n\nNo frontmatter at all.", encoding="utf-8")
        with pytest.raises(KBFrontmatterError):
            load_kb_doc(p)

    def test_invalid_yaml_raises(self, tmp_path: Path) -> None:
        p = tmp_path / "bad.md"
        p.write_text("---\nbroken: : yaml :\n---\n\n## Opener\n\nbody", encoding="utf-8")
        with pytest.raises(KBFrontmatterError):
            load_kb_doc(p)

    def test_missing_opener_raises(self, tmp_path: Path) -> None:
        p = tmp_path / "no-opener.md"
        p.write_text(
            "---\nslug: rm-vs-x\ncomposition: rogue+mage\nvs: warrior+druid\n"
            "difficulty: easy\nkill_target:\n  primary: druid\n"
            "sources:\n- type: file\n  path: x.md\nlast_reviewed: '2026-05-12'\n---\n\n"
            "## Mid-fight rotation\n\nfoo\n",
            encoding="utf-8",
        )
        with pytest.raises(KBSchemaError):
            load_kb_doc(p)


class TestGlossaryResolution:
    def test_orphan_ability_raises(self, tmp_path: Path) -> None:
        p = tmp_path / "orphan.md"
        p.write_text(
            "---\nslug: rm-vs-x\ncomposition: rogue+mage\nvs: warrior+druid\n"
            "difficulty: easy\nkill_target:\n  primary: druid\n"
            "sources:\n- type: file\n  path: x.md\nlast_reviewed: '2026-05-12'\n---\n\n"
            "## Opener\n\nOpen with [[ability:nonexistent-spell]].\n",
            encoding="utf-8",
        )
        glossary = GlossaryIndex(slugs=frozenset({"cheap-shot"}))
        with pytest.raises(KBOrphanAbilityError, match="nonexistent-spell"):
            load_kb_doc(p, glossary=glossary)

    def test_resolved_ability_ok(self, tmp_path: Path) -> None:
        p = tmp_path / "ok.md"
        p.write_text(
            "---\nslug: rm-vs-x\ncomposition: rogue+mage\nvs: warrior+druid\n"
            "difficulty: easy\nkill_target:\n  primary: druid\n"
            "sources:\n- type: file\n  path: x.md\nlast_reviewed: '2026-05-12'\n---\n\n"
            "## Opener\n\nOpen with [[ability:cheap-shot]].\n",
            encoding="utf-8",
        )
        glossary = GlossaryIndex(slugs=frozenset({"cheap-shot"}))
        doc = load_kb_doc(p, glossary=glossary)
        assert doc.slug == "rm-vs-x"


class TestValidateDirectory:
    """Контракт: validate_directory(kb/drafts/) валидирует все 22 сгенерированных draft'а."""

    def test_all_drafts_valid(self, drafts_dir: Path) -> None:
        if not drafts_dir.is_dir():
            pytest.skip("kb/drafts/ ещё не сгенерирован — запусти arena-ingest paste")
        ok, errors = validate_directory(drafts_dir)
        assert errors == [], f"Schema-валидация упала на: {errors}"
        # Phase 1 эталон: 12 RM + 10 RP = 22
        assert ok == 22, f"Ожидалось 22 валидных draft'а, получено {ok}"

    def test_all_drafts_have_resolved_abilities(
        self, drafts_dir: Path, glossary_path: Path
    ) -> None:
        if not drafts_dir.is_dir() or not glossary_path.is_file():
            pytest.skip("kb/drafts/ или kb/glossary/ не сгенерированы")
        ok, errors = validate_directory(drafts_dir, glossary_path=glossary_path)
        orphan_errs = [(p, e) for p, e in errors if "Способности не найдены" in e]
        assert orphan_errs == [], f"Orphan ability-slugs: {orphan_errs}"
