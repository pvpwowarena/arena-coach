#!/usr/bin/env python3
"""Generate kb/glossary/slang.md from slang.json (single source of truth).

Also validates the lexicon:
  * every ref=abilities.json slug exists in abilities.json
  * every ref=terms.md slug exists in terms.md (heading, normalized)
  * no RU slang token maps to more than one canonical slug (input-ambiguity)
  * every `voice` form is present in that entry's `slang[]`

Stdlib only. Run from anywhere:

    python tools/gen_slang_md.py            # writes slang.md, prints report
    python tools/gen_slang_md.py --check    # validate only, do not write

Exit code 1 if any hard validation error is found.
"""
from __future__ import annotations

import datetime as _dt
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GLOSSARY = REPO / "kb" / "glossary"
SLANG_JSON = GLOSSARY / "slang.json"
ABILITIES_JSON = GLOSSARY / "abilities.json"
TERMS_MD = GLOSSARY / "terms.md"
SLANG_MD = GLOSSARY / "slang.md"

CATEGORY_ORDER = ["ability", "tactic", "status", "role", "target", "class"]
CATEGORY_TITLE = {
    "ability": "Способности",
    "tactic": "Тактика",
    "status": "Статусы / механики",
    "role": "Роли",
    "target": "Объекты",
    "class": "Классы",
}
REGISTER_SHORT = {"standard": "std", "colloquial": "colloq"}


def _norm(s: str) -> str:
    return s.strip().lower().replace(" ", "-")


def _load() -> tuple[dict, set[str], set[str]]:
    slang = json.loads(SLANG_JSON.read_text(encoding="utf-8"))
    abilities = set(json.loads(ABILITIES_JSON.read_text(encoding="utf-8")).keys())
    terms = {
        _norm(line[3:])
        for line in TERMS_MD.read_text(encoding="utf-8").splitlines()
        if line.startswith("## ")
    }
    return slang, abilities, terms


def validate(slang: dict, abilities: set[str], terms: set[str]) -> list[str]:
    errors: list[str] = []

    # ref integrity
    for slug, e in slang.items():
        ref = e.get("ref")
        if ref == "abilities.json" and slug not in abilities:
            errors.append(f"[ref] {slug}: ref=abilities.json но slug отсутствует в abilities.json")
        elif ref == "terms.md" and slug not in terms:
            errors.append(f"[ref] {slug}: ref=terms.md но '{slug}' отсутствует среди заголовков terms.md")
        elif ref not in {"abilities.json", "terms.md", "new"}:
            errors.append(f"[ref] {slug}: неизвестный ref={ref!r}")

    # alias collisions (input ambiguity)
    token_owner: dict[str, str] = {}
    for slug, e in slang.items():
        for form in e.get("slang", []):
            tok = form.strip().lower()
            if tok in token_owner and token_owner[tok] != slug:
                errors.append(
                    f"[collision] токен «{form}» принадлежит и '{token_owner[tok]}', и '{slug}'"
                )
            else:
                token_owner[tok] = slug

    # voice must be a recognized form
    for slug, e in slang.items():
        voice = e.get("voice", "")
        forms = {f.strip().lower() for f in e.get("slang", [])}
        if voice and voice.strip().lower() not in forms:
            errors.append(f"[voice] {slug}: voice «{voice}» нет в slang[]")

    return errors


def _table(rows: list[dict]) -> str:
    out = ["| slug | EN | RU | сленг (формы) | voice | reg | conf | ref |",
           "|---|---|---|---|---|---|---|---|"]
    for e in rows:
        forms = ", ".join(e.get("slang", []))
        reg = REGISTER_SHORT.get(e.get("register", ""), e.get("register", ""))
        out.append(
            f"| `{e['slug']}` | {e['en']} | {e.get('ru', '')} | {forms} "
            f"| **{e.get('voice', '')}** | {reg} | {e.get('confidence', '')} | {e['ref']} |"
        )
    return "\n".join(out)


def render(slang: dict) -> str:
    by_cat: dict[str, list[dict]] = {c: [] for c in CATEGORY_ORDER}
    for e in slang.values():
        by_cat.setdefault(e["category"], []).append(e)

    new_slugs = sorted(s for s, e in slang.items() if e.get("ref") == "new")
    protected_en = sorted({e["en"] for e in slang.values()})
    today = _dt.date.today().isoformat()

    parts: list[str] = []
    parts.append("# Arena Slang Glossary (RU ⇄ canonical)\n")
    parts.append(
        "> ⚠ **Авто-генерируется** из `slang.json` через `tools/gen_slang_md.py`. "
        "Не редактировать руками — правь `slang.json` и перегенери.\n"
        f"> Сгенерировано: {today} · Записей: {len(slang)} · "
        f"Новых canonical slug'ов: {len(new_slugs)}\n"
    )
    parts.append(
        "**Назначение:** маппинг русского задрот-сленга команды ⇄ canonical slug ⇄ "
        "защищённый EN-термин (Phase 1.5).\n\n"
        "- `slang[]` — все распознаваемые формы (вход: понять игрока, паста стрима, голосовая команда).\n"
        "- `voice` / `register` — что бот/TTS отдаёт на **выход** (Phase 4.5): `std` = безопасно для генерации, "
        "`colloq` = понимаем на входе, в речь без нужды не суём.\n"
        "- `ref` — где живёт canonical-определение: `abilities.json` (спелл-дата), `terms.md` (жаргон), "
        "`new` (концепт пока без отдельного canonical — домик в slang.json).\n"
    )

    for cat in CATEGORY_ORDER:
        rows = sorted(by_cat.get(cat, []), key=lambda e: e["slug"])
        if not rows:
            continue
        parts.append(f"\n## {CATEGORY_TITLE[cat]} ({len(rows)})\n")
        parts.append(_table(rows))
        notes = [(e["slug"], e["note"]) for e in rows if e.get("note")]
        if notes:
            parts.append("\n**Заметки:**\n")
            parts.append("\n".join(f"- `{s}` — {n}" for s, n in notes))
        parts.append("")

    parts.append("\n## Новые canonical slug'и (нет в abilities.json / terms.md)\n")
    parts.append(
        "Эти концепты получили canonical-домик прямо в `slang.json`. При желании поднять "
        "в `abilities.json` (`trinket`, `blink`) или оставить как есть (роли/классы/механики):\n"
    )
    parts.append(", ".join(f"`{s}`" for s in new_slugs))

    parts.append("\n\n## Защищённые EN-термины (для sync с Phase 1.5)\n")
    parts.append(
        "Список EN-форм, которые остаются на английском в прозе (свести с "
        "«защищённым списком» в `docs/phase-1.5-translation-plan.md`):\n"
    )
    parts.append(", ".join(f"`{t}`" for t in protected_en))
    parts.append("")
    return "\n".join(parts)


def main() -> int:
    check_only = "--check" in sys.argv
    slang, abilities, terms = _load()
    errors = validate(slang, abilities, terms)

    from collections import Counter

    print(f"slang.json: {len(slang)} записей")
    print(f"  по категориям: {dict(Counter(e['category'] for e in slang.values()))}")
    print(f"  по ref:        {dict(Counter(e['ref'] for e in slang.values()))}")
    print(f"  по confidence: {dict(Counter(e['confidence'] for e in slang.values()))}")

    dup_warnings = []
    for _slug, _e in slang.items():
        _forms = [f.strip().lower() for f in _e.get("slang", [])]
        _dups = sorted({f for f in _forms if _forms.count(f) > 1})
        if _dups:
            dup_warnings.append(f"[dup] {_slug}: повтор формы внутри slang[]: {', '.join(_dups)}")
    if dup_warnings:
        print(f"\n⚠ Предупреждения: {len(dup_warnings)}")
        for _w in dup_warnings:
            print("   " + _w)

    if errors:
        print(f"\n❌ Валидация: {len(errors)} ошибок:")
        for er in errors:
            print("   " + er)
        return 1
    print("\n✅ Валидация: ok (привязка slug'ов, коллизии алиасов, voice-формы, дубли)")

    if check_only:
        return 0

    SLANG_MD.write_text(render(slang), encoding="utf-8")
    print(f"✅ Записан {SLANG_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
