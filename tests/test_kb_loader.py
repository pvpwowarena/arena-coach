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
    """Контракт: validate_directory(kb/drafts/) валидирует все 68 сгенерированных draft'ов."""

    def test_all_drafts_valid(self, drafts_dir: Path) -> None:
        if not drafts_dir.is_dir():
            pytest.skip("kb/drafts/ ещё не сгенерирован — запусти arena-ingest paste")
        ok, errors = validate_directory(drafts_dir)
        assert errors == [], f"Schema-валидация упала на: {errors}"
        # Эталон: 32×2v2 (15 RM + 15 RP + 2 spriest spec) + 9×3v3
        # (WLD, mirror, RLP, RLD, MLP, Shadowplay, double-heal, WMP, Hunter/Disc/Druid) = 41
        # +2 (2026-06-24): rm/rp-vs-warrior-rogue засорсены из гипотез (AOEAH tier-list anchor).
        # +3 (2026-06-25): rm/rp-vs-warlock-hpala + rp-vs-hunter-hpala засорсены из гипотез
        # (Warcraft Tavern 2v2 tier-list + RM/DPR strategies anchors).
        # +2 (2026-06-27): rm/rp-vs-warrior-mage засорсены из гипотез
        # (AOEAH D-tier anchor; RM + Icy Veins; RP + Gog123456/OwnedCore TBC 2008).
        # +1 (2026-06-28): rp-vs-mage-rdruid засорсен из гипотезы
        # (Deadlycoward in-depth DP/R guide, Warcraft Tavern — «DPR vs. Druid / Frost Mage» 5/10).
        # +2 (2026-07-02): rm/rp-vs-rogue-hpala засорсены из гипотез
        # (Wowhead hpala arena guide 2.5.5: «Paladin / Warrior or Rogue» = named 2v2 comp
        # + посвящённая секция; Deadlycoward mana-burn план; Hesback hpala-vs-rogue-teams).
        # +2 (2026-07-07): rm/rp-vs-mage-hpala засорсены из гипотез
        # (Skill Capped comps-страницы S2/2.5.5: пара названа «C Tier: Holy Paladin +
        # Frost Mage» с обеих сторон — hpala-comps и fmage-comps; RP + Deadlycoward
        # class-handling как помеченная обвязка).
        # +8 (2026-07-23): rl-vs-* — новый состав Rogue/Warlock 2v2 (RL), топ-мета
        # матчапы (RM, Warr/RDruid, SL/Druid, Rogue/Druid, Mage/Priest, SL/Disc,
        # Warr/RSham, Rogue/Disc) засорсены из Icy Veins 2v2 rankings (SL/SL
        # Warlock/Rogue best-tier) + Wowhead Warlock arena guide (Rogue/Warlock
        # «premier pairing»); execution синтезировано (теги synthesized-execution/new-comp-rl).
        # +5 (2026-07-23): rrd-vs-* — новый состав Rogue/Rogue/Resto Druid 3v3 (RRD,
        # off-meta: не тирится в 3v3 tier-листах). Каркас — OwnedCore Double Rogue
        # Guide (эпоха TBC 2.x подтверждена) + Icy Veins Rogue/Druid синергия + Skill
        # Capped/Icy Veins 3v3 enemy-тир; execution синтезирован (off-meta-comp/new-comp-rrd).
        # +12 (2026-07-26): rd-vs-* — новый состав Rogue/Resto Druid 2v2 (RD),
        # топ-мета 2v2 поле (зеркалит набор rl-vs-*): RM, Warr/RDruid, SL/RDruid,
        # RD-mirror, Rogue/Disc, Mage/Disc, SL/Disc, Warr/Hpala, Warr/RSham,
        # Hunter/RDruid, double-rogue, Ret/RSham. Anchor — Icy Veins Resto Druid PvP
        # guide («Druid + Rogue ... are your best compositions»; Cyclone/Lifebloom/
        # Barkskin/NS/Roots toolkit) + Icy Veins 2v2 rankings (per-matchup тир-строки);
        # execution синтезирован (synthesized-execution/new-comp-rd; off-meta-comp для
        # double-rogue и Ret/RSham, которых нет в явном тир-листе).
        assert ok == 80, f"Ожидалось 80 валидных draft'ов, получено {ok}"

    def test_all_drafts_have_resolved_abilities(
        self, drafts_dir: Path, glossary_path: Path
    ) -> None:
        if not drafts_dir.is_dir() or not glossary_path.is_file():
            pytest.skip("kb/drafts/ или kb/glossary/ не сгенерированы")
        _ok, errors = validate_directory(drafts_dir, glossary_path=glossary_path)
        orphan_errs = [(p, e) for p, e in errors if "Способности не найдены" in e]
        assert orphan_errs == [], f"Orphan ability-slugs: {orphan_errs}"
