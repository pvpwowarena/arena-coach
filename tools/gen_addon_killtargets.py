#!/usr/bin/env python3
"""Компилятор KB → `addon/ArenaCoach/KillTargets.lua` (Phase 4.18).

Зачем: аддон должен решать килл-таргет ЛОКАЛЬНО и мгновенно. На воротах
`UnitClass("arena1")` уже отдаёт классы врагов — без кастов, без combat-лога,
без сети. Всё, чего аддону не хватает, — знание KB, а оно статично. Значит его
можно скомпилировать в Lua-таблицу и положить рядом с аддоном.

Ключ таблицы: `<bracket>|<наши классы>|<классы врагов>`, классы отсортированы
и в нижнем регистре — ровно то, что аддон может собрать сам из UnitClass.
Значение: класс килл-таргета (UPPER) + пометка `sure`.

Схлопывание спеков в классы неизбежно теряет различия (KB знает
«ret-paladin+resto-shaman», аддон видит «paladin+shaman»). Если у схлопнутого
ключа документы расходятся в цели — пишем `sure = false`: аддон покажет цель
как предположение (или отдаст решение эвристике), а не соврёт уверенно.

Запуск:
    python tools/gen_addon_killtargets.py            # перегенерировать файл
    python tools/gen_addon_killtargets.py --check    # только проверить свежесть
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "backend"))

from arena_coach.kb.indexer import comp_part_to_class, comp_to_classes  # noqa: E402
from arena_coach.kb.loader import KBLoadError, load_kb_doc  # noqa: E402

OUT = REPO / "addon" / "ArenaCoach" / "KillTargets.lua"
KB_DIRS = ("kb/drafts", "kb/matchups")

HEADER = """-- ArenaCoach/KillTargets.lua
-- СГЕНЕРИРОВАНО tools/gen_addon_killtargets.py — не редактировать руками.
-- Источник: kb/drafts + kb/matchups (frontmatter kill_target.primary).
--
-- Ключ: "<bracket>|<наши классы>|<классы врагов>", классы sorted+lowercase —
-- ровно то, что аддон собирает сам из UnitClass на воротах.
-- Значение: { t = "КЛАСС ЦЕЛИ", sure = true|false }.
-- sure = false — KB-документы под этим ключом расходятся (схлопывание спеков
-- в классы), цель показываем как предположение.

local AC = ArenaCoach

AC.KB_KILL_TARGETS = {
"""

FOOTER = """}

-- Сколько матчапов скомпилировано (для /ac status и диагностики).
AC.KB_KILL_TARGETS_COUNT = %d
"""


def _docs() -> list[object]:
    out = []
    for rel in KB_DIRS:
        d = REPO / rel
        if not d.exists():
            continue
        for path in sorted(d.glob("*.md")):
            try:
                out.append(load_kb_doc(path))
            except KBLoadError as exc:
                print(f"⚠️  пропускаю {path.name}: {exc}", file=sys.stderr)
    return out


def build_table() -> tuple[dict[str, tuple[str, bool]], int]:
    """(ключ → (класс цели, уверенно ли), сколько документов учтено)."""
    votes: dict[str, set[str]] = defaultdict(set)
    used = 0
    for doc in _docs():
        primary = getattr(doc.kill_target, "primary", None)
        if not primary:
            continue
        target = comp_part_to_class(str(primary)).upper()
        if not target:
            continue
        ours = "+".join(comp_to_classes(doc.composition))
        theirs = "+".join(comp_to_classes(doc.vs))
        if not ours or not theirs:
            continue
        # doc.bracket — Enum: в ключ идёт его значение («2v2»), а не repr.
        bracket = getattr(doc.bracket, "value", str(doc.bracket))
        votes[f"{bracket}|{ours}|{theirs}"].add(target)
        used += 1

    table: dict[str, tuple[str, bool]] = {}
    for key, targets in sorted(votes.items()):
        # При расхождении берём алфавитно первый, но честно помечаем неуверенность.
        table[key] = (sorted(targets)[0], len(targets) == 1)
    return table, used


def render(table: dict[str, tuple[str, bool]]) -> str:
    lines = [HEADER]
    for key, (target, sure) in table.items():
        sure_lua = "true" if sure else "false"
        lines.append(f'    ["{key}"] = {{ t = "{target}", sure = {sure_lua} }},\n')
    lines.append(FOOTER % len(table))
    return "".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="не писать, только сверить с файлом")
    args = ap.parse_args()

    table, used = build_table()
    content = render(table)
    unsure = sum(1 for _, sure in table.values() if not sure)

    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != content:
            print(f"❌ {OUT.relative_to(REPO)} устарел — перегенерируй генератором", file=sys.stderr)
            return 1
        print(f"✅ {OUT.relative_to(REPO)} актуален ({len(table)} ключей)")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(content, encoding="utf-8")
    print(
        f"✅ {OUT.relative_to(REPO)}: {len(table)} ключей из {used} документов "
        f"(неуверенных после схлопывания спеков: {unsure})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
