#!/usr/bin/env python3
"""Сгенерировать полную матрицу покрытия матчапов → docs/COVERAGE.md.

Перечисляет ВСЕ комбинации врагов на уровне классов (включая зеркала: 2 rogue,
2 mage и т.д.) для наших составов и помечает статус каждой ячейки:
  ✅ sourced draft (kb/drafts/)   🟡 AI-hypothesis (kb/hypotheses/)   ⬜ todo

Уровень классов (не спеков): спек-варианты добавляются точечно там, где спек
меняет тактику (frost/fire mage, arms/prot warrior и т.п.) — это отмечается вручную.

Stdlib only:  python tools/coverage_matrix.py
"""
from __future__ import annotations

import itertools
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DRAFTS = REPO / "kb" / "drafts"
HYPO = REPO / "kb" / "hypotheses"
OUT = REPO / "docs" / "COVERAGE.md"

CLASSES = ["warrior", "paladin", "hunter", "rogue", "priest", "shaman", "mage", "warlock", "druid"]
OUR_2V2 = [
    ("rogue+mage", "RM"),
    ("rogue+priest", "RP"),
    ("rogue+warlock", "RL"),
    ("rogue+resto-druid", "RD"),
    ("rogue+rogue", "RR"),
]
OUR_3V3 = [("rogue+mage+priest", "RMP"), ("rogue+rogue+resto-druid", "RRD")]

# Спек-варианты: ячейки, где спек врага меняет тактику настолько, что класс-уровень
# недостаточен. Перечисляются ЯВНО и матчатся по ТОЧНОМУ vs-составу (без сведения к
# классам). Класс-уровневая ячейка при этом может быть уже ✅ (напр. rogue+priest).
# Формат: (vs_spec_comp, человекочитаемый label, примечание).
SPEC_VARIANTS_2V2 = [
    (
        "rogue+shadow-priest",
        "Rogue / Shadow Priest",
        "Shadow≠Disc: оффенс-прийст (fear/silence/dispel), без хила, immobile",
    ),
]

_FM = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def _base(token: str) -> str:
    """resto-druid→druid, holy-paladin→paladin, shadow-priest→priest, warrior→warrior."""
    return token.split("-")[-1]


def _classkey(comp: str) -> tuple[str, ...]:
    return tuple(sorted(_base(p) for p in comp.split("+")))


def _scan(folder: Path) -> set[tuple[tuple[str, ...], tuple[str, ...]]]:
    """{(our_classkey, enemy_classkey)} из frontmatter файлов папки."""
    out: set[tuple[tuple[str, ...], tuple[str, ...]]] = set()
    if not folder.is_dir():
        return out
    for p in folder.glob("*.md"):
        m = _FM.match(p.read_text(encoding="utf-8"))
        if not m:
            continue
        fm = m.group(1)
        comp = re.search(r"^composition:\s*(.+)$", fm, re.MULTILINE)
        vs = re.search(r"^vs:\s*(.+)$", fm, re.MULTILINE)
        if comp and vs:
            out.add((_classkey(comp.group(1).strip()), _classkey(vs.group(1).strip())))
    return out


def _scan_exact(folder: Path) -> set[tuple[str, str]]:
    """{(composition, vs)} verbatim (lower) — для точного матча спек-вариантов."""
    out: set[tuple[str, str]] = set()
    if not folder.is_dir():
        return out
    for p in folder.glob("*.md"):
        m = _FM.match(p.read_text(encoding="utf-8"))
        if not m:
            continue
        fm = m.group(1)
        comp = re.search(r"^composition:\s*(.+)$", fm, re.MULTILINE)
        vs = re.search(r"^vs:\s*(.+)$", fm, re.MULTILINE)
        if comp and vs:
            out.add((comp.group(1).strip().lower(), vs.group(1).strip().lower()))
    return out


def _cell(our: tuple[str, ...], enemy: tuple[str, ...], sourced, hypo) -> str:
    if (our, enemy) in sourced:
        return "✅"
    if (our, enemy) in hypo:
        return "🟡"
    return "⬜"


def _section(title: str, size: int, ours, sourced, hypo) -> tuple[str, dict[str, int]]:
    enemies = list(itertools.combinations_with_replacement(CLASSES, size))
    lines = [f"## {title} — {len(enemies)} вражеских комбинаций × {len(ours)} наших\n"]
    header = "| Enemy \\ Our | " + " | ".join(lbl for _, lbl in ours) + " |"
    lines.append(header)
    lines.append("|" + "---|" * (len(ours) + 1))
    counts = {"✅": 0, "🟡": 0, "⬜": 0}
    for enemy in enemies:
        cells = []
        for comp, _ in ours:
            c = _cell(_classkey(comp), tuple(sorted(enemy)), sourced, hypo)
            counts[c] += 1
            cells.append(c)
        lines.append("| " + "+".join(enemy) + " | " + " | ".join(cells) + " |")
    lines.append("")
    return "\n".join(lines), counts


def _section_spec(ours, sourced_exact, hypo_exact) -> tuple[str, dict[str, int]]:
    """Секция спек-вариантов: матч по точному vs-составу (не сводя к классам)."""
    lines = [
        f"## 2v2 спек-варианты — {len(SPEC_VARIANTS_2V2)} (матч по точному составу врага)\n",
        "Класс-уровень такой пары может быть уже ✅ — здесь отслеживаются спек-вариации, "
        "где тактика реально иная. Считаются отдельно, сверх 255 класс-ячеек.\n",
    ]
    lines.append("| Enemy spec \\ Our | " + " | ".join(lbl for _, lbl in ours) + " | Примечание |")
    lines.append("|" + "---|" * (len(ours) + 2))
    counts = {"✅": 0, "🟡": 0, "⬜": 0}
    for vs_spec, label, note in SPEC_VARIANTS_2V2:
        cells = []
        for comp, _ in ours:
            key = (comp, vs_spec)
            c = "✅" if key in sourced_exact else "🟡" if key in hypo_exact else "⬜"
            counts[c] += 1
            cells.append(c)
        lines.append(f"| {label} | " + " | ".join(cells) + f" | {note} |")
    lines.append("")
    return "\n".join(lines), counts


def main() -> int:
    sourced = _scan(DRAFTS)
    hypo = _scan(HYPO)
    body = [
        "# Матрица покрытия матчапов (auto-generated)",
        "",
        "`python tools/coverage_matrix.py` — перегенерировать. Уровень классов; ✅ sourced draft · "
        "🟡 AI-hypothesis (kb/hypotheses/, непроверено) · ⬜ todo.",
        "",
    ]
    total = {"✅": 0, "🟡": 0, "⬜": 0}
    for title, size, ours in [("2v2", 2, OUR_2V2), ("3v3", 3, OUR_3V3)]:
        sec, counts = _section(title, size, ours, sourced, hypo)
        for k in total:
            total[k] += counts[k]
        body.append(sec)

    # Спек-варианты — отдельная секция, матч по точному составу (не входит в 255).
    sourced_exact = _scan_exact(DRAFTS)
    hypo_exact = _scan_exact(HYPO)
    spec_sec, spec_counts = _section_spec(OUR_2V2, sourced_exact, hypo_exact)
    body.append(spec_sec)

    body.insert(
        3,
        f"**Итого (класс-уровень):** ✅ {total['✅']} sourced · 🟡 {total['🟡']} hypotheses · "
        f"⬜ {total['⬜']} todo (всего ячеек {sum(total.values())}).\n\n"
        f"**Спек-варианты (сверх 255):** ✅ {spec_counts['✅']} · 🟡 {spec_counts['🟡']} · "
        f"⬜ {spec_counts['⬜']}.\n",
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(body), encoding="utf-8")
    print(f"Записано: {OUT.relative_to(REPO)}")
    print(f"✅ {total['✅']}  🟡 {total['🟡']}  ⬜ {total['⬜']}  (всего {sum(total.values())})")
    print(f"spec: ✅ {spec_counts['✅']}  🟡 {spec_counts['🟡']}  ⬜ {spec_counts['⬜']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
