#!/usr/bin/env python3
"""Проставить `cooldown_s` в realtime_spells.json из sourced-слоя abilities.json.

Зачем скриптом, а не руками: `cooldown_s` — это механика 2.4.3, и по канону
проекта её нельзя экстраполировать. Единственный проверенный источник кулдаунов в
репозитории — `kb/glossary/abilities.json` (поле `cd`, строкой: «60с», «5 мин»).
Скрипт переносит ровно эти значения и печатает, чего не хватает, — так значение
всегда можно проследить до источника, а не до чьей-то памяти.

Запуск:  python tools/derive_cooldowns.py [--write]
Без `--write` — только отчёт (dry-run).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

KB = Path(__file__).resolve().parent.parent / "kb" / "glossary"

#: Ключ realtime → слаг abilities.json, если простая замена `_`→`-` не совпала.
ALIASES: dict[str, str] = {
    "frost_nova": "nova",
    "cloak_of_shadows": "cloak-of-shadows",
    "shadowstep": "shadowstep",
}

_NUM = re.compile(r"(\d+(?:[.,]\d+)?)\s*(мин|min|с|s|sec|сек)", re.IGNORECASE)


def parse_cd(raw: str) -> float | None:
    """'60с' → 60.0; '5 мин' → 300.0; '24с (пета)' → 24.0; мусор → None."""
    m = _NUM.search(raw or "")
    if not m:
        return None
    value = float(m.group(1).replace(",", "."))
    unit = m.group(2).lower()
    return value * 60.0 if unit in ("мин", "min") else value


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="записать изменения в файл")
    args = ap.parse_args()

    abilities = json.loads((KB / "abilities.json").read_text(encoding="utf-8"))
    rt_path = KB / "realtime_spells.json"
    rt = json.loads(rt_path.read_text(encoding="utf-8"))
    spells = rt["spells"]

    filled: list[tuple[str, str, float]] = []
    missing: list[str] = []
    for key, entry in spells.items():
        slug = ALIASES.get(key, key.replace("_", "-"))
        src = abilities.get(slug)
        raw = str(src.get("cd") or "") if isinstance(src, dict) else ""
        seconds = parse_cd(raw)
        if seconds is None:
            entry.pop("cooldown_s", None)
            missing.append(key)
            continue
        entry["cooldown_s"] = int(seconds) if seconds.is_integer() else seconds
        filled.append((key, raw, seconds))

    filled.sort()
    print(f"cooldown_s проставлен: {len(filled)} / {len(spells)}")
    for key, raw, sec in filled:
        print(f"  {key:24} {raw:14} → {sec:g}s")
    print(f"\nбез подтверждённого КД (говорим без секунд): {len(missing)}")
    print("  " + ", ".join(sorted(missing)))

    if args.write:
        rt_path.write_text(
            json.dumps(rt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"\nзаписано: {rt_path}")
    else:
        print("\n(dry-run; повторить с --write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
