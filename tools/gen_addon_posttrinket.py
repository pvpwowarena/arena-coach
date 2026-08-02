#!/usr/bin/env python3
"""Компилятор KB → пост-тринкет колауты (Phase 4.22).

Тринкет врага — главная развилка боя: KB в секциях «If enemy trinkets» знает,
что делать ДАЛЬШЕ, но до 4.22 это знание жило только в Markdown и постматче.
Аддон видит тринкет мгновенно (свой CLEU, `Overlay:NoteTrinket`) — значит план
можно сказать в ту же секунду, без сети (канон: log-buffer-48kb).

Устройство — как у `gen_addon_openers.py` (Phase 4.20): ЧТО сказать — факты из
KB-документов, КАК сказать — вычитанные таблицы. Прозу секций «If enemy
trinkets» надёжно парсить нельзя (там варианты и условия), поэтому факты
закреплены явной таблицей `FACTS` со ссылкой на документ-источник; генератор
ВАЛИДИРУЕТ каждую строку против KB: ключ матчапа обязан существовать, класс —
быть у врага, slug — среди документов ключа. Опечатка = ошибка генерации,
а не тихий мусор в аддоне.

Слоты с КОНФЛИКТОМ источников (например, priest в ключе priest+rogue: disc-док
и spriest-док расходятся) в таблицу не вносятся: молчание честнее спорного
совета — правило «Нет в KB → нет совета».

    python tools/gen_addon_posttrinket.py            # PostTrinket.lua + манифест
    python tools/gen_addon_posttrinket.py --dry-run  # таблица на вычитку
    python tools/gen_addon_posttrinket.py --check    # свежесть сгенерированного
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import NamedTuple

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "backend"))

from arena_coach.kb.indexer import comp_to_classes  # noqa: E402
from arena_coach.kb.loader import KBLoadError, load_kb_doc  # noqa: E402

KB_DIRS = ("kb/drafts", "kb/matchups")
OUT_LUA = REPO / "addon" / "ArenaCoach" / "PostTrinket.lua"
OUT_MANIFEST = REPO / "addon" / "ArenaCoach" / "sfx" / "posttrinket.json"

_VOWELS = "аеёиоуыэюя"
SYLLABLES_PER_SEC = 2.8


def syllables(text: str) -> int:
    return sum(1 for ch in text.lower() if ch in _VOWELS)


#: Фраза-ключ → как сказать. ВЫЧИТЫВАЕТСЯ ВЛАДОМ. Класс срочности «state»
#: (r85): решение принимается в секунду тринкета. Потолок — 8 слогов (4.17).
PHRASES: dict[str, str] = {
    "blind_vanish":  "Блайнд, ваниш!",
    "blind":         "Блайнд его!",
    "blind_war":     "Блайнд вара!",
    "blind_mage":    "Блайнд мага!",
    "blind_priest":  "Блайнд приста!",
    "full_kidney":   "Полный кидни!",
    "trade_stun":    "Тринкеть его стан!",
    "cloak_coil":    "Клоак — коил!",
    "vanish_reopen": "Ваниш, реоткрытие!",
    "vanish_garrote": "Ваниш, гарота!",
    "wait_dr":       "Пережди, рестан!",
}

#: (ключ матчапа, класс тринкетнувшего, фраза, slug документа-источника).
#: Факт = «документ slug в секции "If enemy trinkets"/"Alternative opener"
#: говорит, что после тринкета ЭТОГО класса делаем ЭТО».
FACTS: list[tuple[str, str, str, str]] = [
    # druid тринкетит kidney → блайнд+ваниш, победа закреплена (DLEZ 7:03 / 37:36)
    ("2v2|mage+rogue|druid+warrior",  "DRUID",   "blind_vanish",  "rm-vs-warrior-rdruid"),
    ("2v2|mage+rogue|druid+warlock",  "DRUID",   "blind_vanish",  "rm-vs-warlock-rdruid"),
    # их рог тринкетит наш кидни → мгновенный блайнд на его тринкет (DLEZ 24:19)
    ("2v2|mage+rogue|druid+rogue",    "ROGUE",   "blind",         "rm-vs-rogue-rdruid"),
    # пала тринкетит чип — «огромная ошибка» → полный кидни→эвис (DLEZ 28:08)
    ("2v2|mage+rogue|paladin+warrior", "PALADIN", "full_kidney",  "rm-vs-warrior-hpala"),
    # прист тринкетит чип — «ужасный ход» → полный кидни (DLEZ 43:58)
    ("2v2|mage+rogue|priest+warrior", "PRIEST",  "full_kidney",   "rm-vs-warrior-priest"),
    # вар тринкетит овцу → блайнд вара, остаёмся на присте (DLEZ 43:25)
    ("2v2|mage+rogue|priest+warrior", "WARRIOR", "blind_war",     "rm-vs-warrior-priest"),
    # маг тринкетит сап → чип приста + блайнд мага (DLEZ 44:38)
    ("2v2|mage+rogue|mage+priest",    "MAGE",    "blind_mage",    "rm-vs-mage-priest"),
    # прист тринкетит → рекомендация «блайнд в приста» (DLEZ 41:01)
    ("2v2|mage+rogue|priest+warlock", "PRIEST",  "blind_priest",  "rm-vs-warlock-priest"),
    # варлок тринкетит → жди коил, клоак (DLEZ 46:44)
    ("2v2|mage+rogue|rogue+warlock",  "WARLOCK", "cloak_coil",    "rm-vs-warlock-rogue"),
    # миррор: рог тринкетит чип → размен, тринкетим его ответный стан (DLEZ 1:13)
    ("2v2|mage+rogue|mage+rogue",     "ROGUE",   "trade_stun",    "rm-vs-rogue-mage"),
    # хантер тринкетит кидни → пережидаем stun-DR, рестан добивает (DLEZ 20:58)
    ("2v2|mage+rogue|hunter+priest",  "HUNTER",  "wait_dr",       "rm-vs-hunter-priest"),
    # шаман тринкетит → vanish → garrote (DLEZ 30:09)
    ("2v2|mage+rogue|paladin+shaman", "SHAMAN",  "vanish_garrote", "rm-vs-retpala-rsham"),
    # их рог тринкетит → мгновенный vanish, мы впереди по КД (DLEZ 13:52)
    ("2v2|mage+rogue|priest+rogue",   "ROGUE",   "vanish_reopen", "rm-vs-rogue-priest"),
]


class _KeyInfo(NamedTuple):
    classes: set[str]
    slugs: set[str]


def _kb_keys() -> dict[str, _KeyInfo]:
    """ключ матчапа → (классы врага, slug'и документов) по всем документам KB."""
    out: dict[str, _KeyInfo] = {}
    for rel in KB_DIRS:
        d = REPO / rel
        if not d.exists():
            continue
        for path in sorted(d.glob("*.md")):
            try:
                doc = load_kb_doc(path)
            except KBLoadError:
                continue
            ours = "+".join(comp_to_classes(doc.composition))
            theirs = "+".join(comp_to_classes(doc.vs))
            if not ours or not theirs:
                continue
            bracket = getattr(doc.bracket, "value", str(doc.bracket))
            key = f"{bracket}|{ours}|{theirs}"
            info = out.setdefault(key, _KeyInfo(set(), set()))
            info.classes.update(c.upper() for c in comp_to_classes(doc.vs))
            info.slugs.add(doc.slug)
    return out


def build_table() -> tuple[dict[str, dict[str, str]], list[str]]:
    kb = _kb_keys()
    table: dict[str, dict[str, str]] = {}
    errors: list[str] = []
    for key, cls, phrase_key, slug in FACTS:
        if phrase_key not in PHRASES:
            errors.append(f"{key}|{cls}: нет фразы {phrase_key}")
            continue
        info = kb.get(key)
        if info is None:
            errors.append(f"{key}: ключа нет в KB")
            continue
        if cls not in info.classes:
            errors.append(f"{key}: класса {cls} нет у врага")
            continue
        if slug not in info.slugs:
            errors.append(f"{key}: slug {slug} не среди документов ключа {sorted(info.slugs)}")
            continue
        text = PHRASES[phrase_key]
        if syllables(text) > 8:
            errors.append(f"{phrase_key}: «{text}» длиннее 8 слогов (бюджет state, 4.17)")
            continue
        table[f"{key}|{cls}"] = {"c": f"pt_{phrase_key}", "t": text, "kb": slug}
    return table, errors


LUA_HEADER = """-- ArenaCoach/PostTrinket.lua
-- СГЕНЕРИРОВАНО tools/gen_addon_posttrinket.py — не редактировать руками.
-- Источник: kb/drafts + kb/matchups, секции «If enemy trinkets».
--
-- Ключ: "<ключ матчапа как в KillTargets.lua>|<КЛАСС тринкетнувшего>".
-- Значение: { c = "клип без .ogg", t = "текст (панель и чат)" }.
-- Нет ключа → молчание: «Нет в KB → нет совета».

local AC = ArenaCoach

AC.KB_POST_TRINKET = {
"""

LUA_FOOTER = """}

AC.KB_POST_TRINKET_COUNT = %d
"""


def render_lua(table: dict[str, dict[str, str]]) -> str:
    parts = [LUA_HEADER]
    for key in sorted(table):
        row = table[key]
        parts.append(f'    ["{key}"] = {{ c = "{row["c"]}", t = "{row["t"]}" }},\n')
    parts.append(LUA_FOOTER % len(table))
    return "".join(parts)


def render_manifest(table: dict[str, dict[str, str]]) -> str:
    used: dict[str, list[str]] = defaultdict(list)
    for key, row in table.items():
        used[row["c"]].append(key)
    payload = {
        "_comment": (
            "СГЕНЕРИРОВАНО tools/gen_addon_posttrinket.py. Клипы синтезирует "
            "gen_addon_voice.py (класс срочности state, RHVoice elena)."
        ),
        "syllables_per_sec": SYLLABLES_PER_SEC,
        "clips": {
            f"pt_{pk}": {
                "clip": f"pt_{pk}",
                "text": text,
                "syllables": syllables(text),
                "seconds": round(syllables(text) / SYLLABLES_PER_SEC, 1),
                "used_by": sorted(used.get(f"pt_{pk}", [])),
            }
            for pk, text in PHRASES.items()
            if used.get(f"pt_{pk}")
        },
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    table, errors = build_table()
    for e in errors:
        print(f"❌ {e}", file=sys.stderr)
    if errors:
        return 1

    if args.dry_run:
        for key in sorted(table):
            row = table[key]
            print(f"{key:55s} «{row['t']}»  [{row['kb']}]")
        print(f"\n{len(table)} правил, {len({r['c'] for r in table.values()})} клипов", file=sys.stderr)
        return 0

    lua, manifest = render_lua(table), render_manifest(table)
    if args.check:
        stale = [
            p.relative_to(REPO)
            for p, content in ((OUT_LUA, lua), (OUT_MANIFEST, manifest))
            if not p.exists() or p.read_text(encoding="utf-8") != content
        ]
        if stale:
            print(f"❌ устарело: {', '.join(map(str, stale))}", file=sys.stderr)
            return 1
        print(f"✅ PostTrinket.lua и манифест актуальны ({len(table)} правил)")
        return 0

    OUT_LUA.write_text(lua, encoding="utf-8")
    OUT_MANIFEST.write_text(manifest, encoding="utf-8")
    print(f"✅ {len(table)} правил → {OUT_LUA.relative_to(REPO)} + {OUT_MANIFEST.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
