#!/usr/bin/env python3
"""Render canonical KB drafts into the team's natural slang ("voice" layer).

Phase 1.5 / Phase 4.5 prototype. Reads the lexicon (`kb/glossary/slang.json`)
and produces *derived*, non-canonical copies in `kb/rendered/slang/`. The
canonical `kb/drafts/` files are NEVER modified — this is a separate render
layer, exactly as the glossary README describes it.

Rules (driven by the lexicon's own schema, nothing hardcoded):
  * `[[ability:slug]]` tokens and standalone EN jargon are replaced with the
    entry's `voice` form, but ONLY for `register: standard` entries. Per the
    schema, `colloquial` forms are understood on INPUT and must NOT be emitted
    into speech/output — those fall back to the readable EN ability name.
  * Ability-slug aliases are resolved automatically via shared spell `id` /
    `en_name` in `abilities.json` (kidney-shot→kidney, cloak-of-shadows→cloak,
    shadowstep→step), so the renderer needs no per-slug special-casing.
  * Frontmatter is copied verbatim (slug / vs / sources stay traceable).

Stdlib only. Run from anywhere:

    python tools/render_slang.py --all      # render every kb/drafts/*.md
    python tools/render_slang.py --slug rp-vs-warlock-rogue
    python tools/render_slang.py --check     # dry-run + coverage report, no write

Exit code 1 on a hard error (missing lexicon, unreadable draft).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GLOSSARY = REPO / "kb" / "glossary"
SLANG_JSON = GLOSSARY / "slang.json"
ABILITIES_JSON = GLOSSARY / "abilities.json"
DRAFTS = REPO / "kb" / "drafts"
OUT_DIR = REPO / "kb" / "rendered" / "slang"

_FRONTMATTER_RE = re.compile(r"^(---\s*\n.*?\n---\s*\n)(.*)$", re.DOTALL)
_ABILITY_REF_RE = re.compile(r"\[\[ability:([a-z0-9-]+)\]\]")


def _load_json(path: Path) -> dict:
    if not path.is_file():
        print(f"ERROR: не найден {path}", file=sys.stderr)
        raise SystemExit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def build_maps(slang: dict, abilities: dict) -> tuple[dict, list, set]:
    """Return (ability_slug→output, prose_pairs, no_slang_gaps).

    * ability_slug→output: для каждого ability-slug (вкл. алиасы) — что писать.
    * prose_pairs: [(regex, voice)] для standalone EN-замен (только standard).
    * no_slang_gaps: ability-slug'и, у которых нет НИ одной slang-записи.
    """
    # Группируем abilities по общему id / en_name → находим slang-сиблинга.
    sibling: dict[str, list[str]] = {}
    for slug, a in abilities.items():
        key = f"id:{a['id']}" if a.get("id") is not None else f"en:{a.get('en_name', slug)}"
        sibling.setdefault(key, []).append(slug)

    def slang_entry_for(slug: str) -> dict | None:
        if slug in slang:
            return slang[slug]
        a = abilities.get(slug)
        if a is not None:
            key = f"id:{a['id']}" if a.get("id") is not None else f"en:{a.get('en_name', slug)}"
            for sib in sibling.get(key, []):
                if sib in slang:
                    return slang[sib]
        return None

    ability_out: dict[str, str] = {}
    gaps: set[str] = set()
    for slug in abilities:
        entry = slang_entry_for(slug)
        if entry and entry.get("register") == "standard" and entry.get("voice"):
            ability_out[slug] = entry["voice"]
        else:
            # colloquial / отсутствует → читаемое EN-имя (в речь не суём colloquial)
            ability_out[slug] = abilities[slug].get("en_name", slug)
            if entry is None:
                gaps.add(slug)

    # Standalone EN-замены: только standard-записи, длинные сначала.
    prose_pairs: list = []
    for entry in slang.values():
        if entry.get("register") != "standard" or not entry.get("voice"):
            continue
        en = (entry.get("en") or "").strip()
        if not en:
            continue
        rx = re.compile(rf"\b{re.escape(en)}\b", re.IGNORECASE)
        prose_pairs.append((len(en), rx, entry["voice"]))
    prose_pairs.sort(key=lambda t: t[0], reverse=True)
    return ability_out, [(rx, v) for _, rx, v in prose_pairs], gaps


def render_body(body: str, ability_out: dict, prose_pairs: list) -> tuple[str, int]:
    used = 0

    def _ability(m: re.Match) -> str:
        nonlocal used
        used += 1
        return ability_out.get(m.group(1), m.group(1))

    body = _ABILITY_REF_RE.sub(_ability, body)
    for rx, voice in prose_pairs:
        body, n = rx.subn(voice, body)
        used += n
    return body, used


def render_file(path: Path, ability_out: dict, prose_pairs: list) -> tuple[str, int, list[str]]:
    text = path.read_text(encoding="utf-8")
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return text, 0, []
    fm, body = m.group(1), m.group(2)
    used_slugs = _ABILITY_REF_RE.findall(body)
    new_body, n = render_body(body, ability_out, prose_pairs)
    note = (
        f"<!-- АВТО-РЕНДЕР слоя slang (prototype). Источник правды: "
        f"kb/drafts/{path.name}. Сгенерировано tools/render_slang.py — не редактировать вручную. -->\n\n"
    )
    return fm + note + new_body, n, used_slugs


def main() -> int:
    ap = argparse.ArgumentParser(description="Render KB drafts into slang voice layer.")
    ap.add_argument("--slug", help="отрендерить один draft по slug")
    ap.add_argument("--all", action="store_true", help="отрендерить все kb/drafts/*.md")
    ap.add_argument("--check", action="store_true", help="dry-run + отчёт покрытия, без записи")
    args = ap.parse_args()

    slang = _load_json(SLANG_JSON)
    abilities = _load_json(ABILITIES_JSON)
    ability_out, prose_pairs, gaps = build_maps(slang, abilities)

    if args.slug:
        targets = [DRAFTS / f"{args.slug}.md"]
    else:
        targets = sorted(DRAFTS.glob("*.md"))
    targets = [t for t in targets if t.is_file()]
    if not targets:
        print("Нет драфтов для рендера.", file=sys.stderr)
        return 1

    used_gaps: set[str] = set()
    total = 0
    for path in targets:
        rendered, n, used_slugs = render_file(path, ability_out, prose_pairs)
        used_gaps |= {s for s in used_slugs if s in gaps}
        total += n
        if not args.check:
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            (OUT_DIR / path.name).write_text(rendered, encoding="utf-8")
        print(f"  {path.name}: {n} замен{' (dry-run)' if args.check else ''}")

    print(f"\n{'DRY-RUN: ' if args.check else ''}файлов: {len(targets)}, всего замен: {total}")
    if not args.check:
        print(f"Записано в: {OUT_DIR.relative_to(REPO)}/")
    if used_gaps:
        print(
            "\n⚠ Используются в драфтах, но НЕТ slang-записи (остались EN-именем) — "
            "кандидаты в slang.json:\n  " + ", ".join(sorted(used_gaps))
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
