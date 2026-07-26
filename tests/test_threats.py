"""Тесты предупреждений по врагам (orchestrator/threats.py, Phase 4.7)."""

from __future__ import annotations

from arena_coach.orchestrator.threats import threat_for, threat_lines, threat_voice


def test_class_threat_basic() -> None:
    lines = threat_lines(["SHAMAN", "WARRIOR"])
    assert len(lines) == 2
    assert any("тотемы огня" in ln for ln in lines)
    assert any("mortal strike" in ln.lower() for ln in lines)


def test_spec_overrides_class() -> None:
    # ret-paladin даёт другую угрозу, чем generic paladin (бабл vs бурст)
    generic = threat_for("PALADIN", None)
    ret = threat_for("PALADIN", "ret-paladin")
    holy = threat_for("PALADIN", "holy-paladin")
    assert generic is not None and ret is not None and holy is not None
    assert ret.dm != generic.dm
    assert "бурст" in ret.dm
    assert "бабл" in holy.dm


def test_unknown_class_no_line() -> None:
    assert threat_lines(["DEMONHUNTER"]) == []
    # частично известный сетап — только известные классы
    lines = threat_lines(["MAGE", "DEMONHUNTER"])
    assert len(lines) == 1
    assert "шаттер" in lines[0]


def test_combo_double_mage_first() -> None:
    lines = threat_lines(["MAGE", "MAGE", "PRIEST"])
    assert lines[0].startswith("⚠️")
    assert "шаттер" in lines[0]
    # классовые угрозы не дублируются (два мага → одна mage-строка)
    mage_lines = [ln for ln in lines if ln.startswith("•") and "овца" in ln]
    assert len(mage_lines) == 1


def test_combo_pair_in_3v3() -> None:
    # paladin+warrior пара внутри тройки должна подниматься
    lines = threat_lines(["PALADIN", "WARRIOR", "MAGE"])
    assert any("бабл" in ln and ln.startswith("⚠️") for ln in lines)


def test_threat_voice_short_and_limited() -> None:
    v = threat_voice(["SHAMAN", "WARLOCK", "MAGE"], limit=2)
    assert v is not None
    assert v.startswith("Осторожно:")
    # не более 2 угроз в голосе (+ комбо не сработало здесь)
    assert v.count(",") <= 2


def test_threat_voice_none_when_unknown() -> None:
    assert threat_voice(["DEMONHUNTER"]) is None


def test_specs_shorter_than_classes_ok() -> None:
    # спеков меньше, чем классов — не падаем, добиваем None
    lines = threat_lines(["MAGE", "DRUID"], ["fire-mage"])
    assert any("помпиро" in ln.lower() or "pom" in ln.lower() for ln in lines)
