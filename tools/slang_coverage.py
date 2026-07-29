#!/usr/bin/env python3
"""Отчёт покрытия KB-ссылок `[[ability:x]]` русским лексиконом (Phase 4.10).

Показывает, что именно услышит/прочитает игрок вместо английских вставок:
сколько ссылок рендерится формой команды (`register: standard`), сколько
падает на аккуратное `en_name` из abilities.json, и какие слаги стоит завести
в `kb/glossary/slang.json` в первую очередь (сортировка по частоте в KB).

    python tools/slang_coverage.py [--kb kb] [--top 30]

Dev-скрипт: не под гейтами CI (tools/ исключён из ruff), сети не трогает.
"""

from __future__ import annotations

import argparse
import collections
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))

from arena_coach.kb.slang import ABILITY_REF_RE, SlangRenderer  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kb", default=str(REPO_ROOT / "kb"), help="путь к KB")
    parser.add_argument("--top", type=int, default=30, help="сколько непокрытых показать")
    args = parser.parse_args()

    kb = Path(args.kb)
    renderer = SlangRenderer.from_kb_path(kb)

    used: collections.Counter[str] = collections.Counter()
    for path in kb.rglob("*.md"):
        used.update(ABILITY_REF_RE.findall(path.read_text(encoding="utf-8", errors="replace")))

    if not used:
        print(f"В {kb} не найдено ни одной ссылки [[ability:...]]")
        return 1

    russian: list[tuple[int, str, str]] = []
    english: list[tuple[int, str, str]] = []
    for slug, count in used.items():
        name = renderer.name(slug)
        # Русская форма команды — по кириллице в результате рендера.
        bucket = russian if any("а" <= ch.lower() <= "я" for ch in name) else english
        bucket.append((count, slug, name))

    total = sum(used.values())
    ru_hits = sum(c for c, _, _ in russian)
    print(f"Ссылок на способности в KB: {total} ({len(used)} уникальных слагов)")
    print(f"  русская форма команды : {ru_hits:5d} ({ru_hits * 100 // total}%), слагов {len(russian)}")
    print(f"  английское имя        : {total - ru_hits:5d}, слагов {len(english)}")
    print(f"\nТоп непокрытых (кандидаты в slang.json), до {args.top}:")
    for count, slug, name in sorted(english, reverse=True)[: args.top]:
        print(f"  {count:5d}  {slug:<28} → «{name}»")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
