"""Парсер «paste»: импорт Markdown-документов с гайдами по матчапам.

Входной формат — `Mirlol-стиль`:

```
# Matchup Guides
Composition
Rogue / Mage

vs
Warrior/Resto Druid
Easy
![druid](https://render.worldofwarcraft.com/icons/56/classicon_druid.jpg)

### Opener
<prose>

### Alternative Openers
<prose>

vs
Rogue/Mage
Mirror
...
```

Выход — `kb/drafts/<slug>.md` (по одному файлу на матчап) со схемой KBDoc.

Парсер консервативен: ничего не выдумывает, секции переносятся as-is, inline-ability
конвертируются в `[[ability:<slug>]]`, остальное оставлено для human review.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Final

import yaml

from arena_ingest.glossary_extract import _ABILITY_INLINE_RE, _is_class_icon, derive_ability_slug

# ───────────────────────── Constants ─────────────────────────

# Если "vs" — единственное содержимое строки (после strip), это потенциальный сепаратор матчапа
_VS_LINE_RE = re.compile(r"^\s*vs\s*$", re.MULTILINE)

_DIFFICULTY_CANON: Final[dict[str, str]] = {
    "easy": "easy",
    "moderate": "moderate",
    "hard": "hard",
    "very hard": "very-hard",
    "mirror": "mirror",
}

_CLASS_ICON_RE = re.compile(
    r"!\[(?P<label>[a-zA-Z ]+)\]\("
    r"https?://render\.worldofwarcraft\.com/icons/\d+/classicon_(?P<class>[a-z]+)\.jpg"
    r"\)"
)

_H3_RE = re.compile(r"^###\s+(.+?)\s*$", re.MULTILINE)

# Mapping ### <heading> → canonical KB-секция (см. PHASE_0_DESIGN §7)
_SECTION_MAPPING: Final[dict[str, str]] = {
    "opener": "Opener",
    "general": "Opener",
    "strategy": "Opener",
    "stealth game": "Opener",
    "alternative openers": "Alternative opener",
    "alternative opener": "Alternative opener",
    "opening on the mage": "Alternative opener",
    "if they open on you": "If enemy opens first",
    "if the enemy rogue opens first": "If enemy opens first",
    "if they get the opener": "If enemy opens first",
    "when you don't get the opener": "If enemy opens first",
    "if you sap priest but don't find rogue": "If enemy opens first",
    "mid-game": "Mid-fight rotation",
    "midgame": "Mid-fight rotation",
    "pet goes & pillar play": "Mid-fight rotation",
    "pet goes and pillar play": "Mid-fight rotation",
    "win conditions": "Win conditions",
    "things to watch out for": "Notes",
    "additional notes": "Notes",
    "notes": "Notes",
}

# Опции / Plan B → Alternative opener (concat); Option 1/2/3/Plan A/B/C распознаём по регексу
_OPTION_RE = re.compile(r"^(option\s+\d+|plan\s+[a-z])\b", re.IGNORECASE)

# ───────────────────────── Composition slugs ─────────────────────────

_OUR_COMP_SHORT: Final[dict[str, str]] = {
    "rogue+mage": "rm",
    "rogue+priest": "rp",
    "rogue+druid": "rd",
    "warrior+druid": "wd",
}


def _comp_short(slug: str) -> str:
    """rogue+mage → rm; иначе — компактный hyphen."""
    return _OUR_COMP_SHORT.get(slug, slug.replace("+", "-"))


_ENEMY_COMP_ABBREV: Final[dict[str, str]] = {
    "warrior/resto druid": "warrior-rdruid",
    "warrior/resto shaman": "warrior-rsham",
    "ret paladin/resto shaman": "retpala-rsham",
    "warlock/resto druid": "warlock-rdruid",
    "rogue/resto druid": "rogue-rdruid",
    "hunter/resto druid": "hunter-rdruid",
    "rogue/mage": "rogue-mage",
    "rogue/priest": "rogue-priest",
    "rogue/rogue": "rogue-rogue",
    "warlock/priest": "warlock-priest",
    "warlock/rogue": "warlock-rogue",
    "mage/priest": "mage-priest",
}


def _enemy_comp_slug(raw: str) -> str:
    """`Warrior/Resto Druid` → `warrior-rdruid`."""
    key = raw.strip().lower()
    if key in _ENEMY_COMP_ABBREV:
        return _ENEMY_COMP_ABBREV[key]
    # Fallback: автоматический slug из текста (lowercase, slash → hyphen)
    return re.sub(r"\s+", "-", key.replace("/", "-")).strip("-")


def _enemy_comp_canonical(raw: str) -> str:
    """`Warrior/Resto Druid` → `warrior+resto-druid` (для frontmatter `vs`)."""
    parts = [re.sub(r"\s+", "-", p.strip().lower()) for p in raw.split("/")]
    return "+".join(parts)


# ───────────────────────── Data structures ─────────────────────────


@dataclass
class ParsedSection:
    """Одна `### H3` секция в источнике."""

    raw_title: str
    body: str  # Markdown, с inline ![ability](...) ещё не конвертированными


@dataclass
class ParsedMatchup:
    """Один матчап после первичного разбора."""

    enemy_comp_raw: str  # "Warrior/Resto Druid"
    difficulty_raw: str  # "Easy" / "Moderate" / ...
    kill_target_hint: str | None = None  # из class-icon: "druid"
    sections: list[ParsedSection] = field(default_factory=list)
    source_lines: tuple[int, int] = (0, 0)  # (start, end) в исходном файле


# ───────────────────────── Parser ─────────────────────────


def _convert_inline_abilities(text: str) -> str:
    """`![cheap shot](https://...ability_cheapshot.jpg)cheap shot` → `[[ability:cheap-shot]]`.

    Class-иконки (`classicon_*`) **не конвертируются** — это визуальные маркеры в шапке,
    а не упоминания способностей. Они либо удаляются, либо остаются как есть.
    """

    def replace(m: re.Match[str]) -> str:
        icon = m.group("icon")
        if _is_class_icon(icon):
            # Сохраняем визуальный маркер «класса» в скобочной форме для читаемости;
            # они обычно встречаются в шапках и игнорируются при KB-валидации.
            return ""
        label = m.group("label")
        trailing = m.group("trailing")
        slug = derive_ability_slug(label, trailing, icon)
        return f"[[ability:{slug}]]"

    return _ABILITY_INLINE_RE.sub(replace, text)


def _split_matchups_raw(text: str) -> list[tuple[int, int]]:
    """Найти границы матчапов в тексте по строкам-сепараторам `vs`.

    Возвращает список (start_idx, end_idx) — байтовые индексы в `text` для каждого матчапа.
    Первый матчап начинается *после* preamble (заголовок "# Matchup Guides", "Composition" и т.д.).
    """
    vs_positions = [m.start() for m in _VS_LINE_RE.finditer(text)]
    if not vs_positions:
        return []

    boundaries: list[tuple[int, int]] = []
    for i, pos in enumerate(vs_positions):
        end = vs_positions[i + 1] if i + 1 < len(vs_positions) else len(text)
        boundaries.append((pos, end))
    return boundaries


def _parse_matchup_header(block: str) -> tuple[str, str, str | None] | None:
    """Распарсить «шапку» матчапа: enemy comp, difficulty, опциональный kill-target hint.

    Ожидаемый формат блока (с учётом ведущих пустых строк):
        <leading whitespace>
        vs
        <enemy comp>
        <difficulty>
        ![<class>](classicon_X.jpg) ...

    Возвращает (enemy_comp_raw, difficulty_raw, kill_target_hint) или None если парс не удался.
    """
    # Собираем все non-empty строки блока, в порядке появления
    non_empty = [ln.strip() for ln in block.split("\n") if ln.strip()]
    # Ожидаем: ["vs", "<enemy>", "<difficulty>", "![class](...)", "### Opener", ...]
    if len(non_empty) < 3:
        return None
    if non_empty[0].lower() != "vs":
        return None

    enemy_comp = non_empty[1]
    difficulty_raw = non_empty[2].lower()
    if difficulty_raw not in _DIFFICULTY_CANON:
        return None

    kill_target: str | None = None
    # Идём дальше и ищем первую class-icon (обычно строка 3-5)
    for line in non_empty[3:7]:
        m = _CLASS_ICON_RE.search(line)
        if m:
            kill_target = m.group("class").lower()
            break

    return enemy_comp, difficulty_raw, kill_target


def _strip_matchup_header(block: str) -> str:
    """Удалить «шапку» матчапа (vs / enemy comp / difficulty / class-icon) и вернуть тело.

    Возвращает текст от первой строки после class-icon (или после difficulty, если иконки нет).
    """
    # Сначала ищем class-icon — самый надёжный sentinel
    icon_match = _CLASS_ICON_RE.search(block)
    if icon_match:
        # Берём текст после конца строки с class-icon
        after_icon = block[icon_match.end() :]
        # Пропускаем оставшийся хвост строки и переходим к следующей строке
        newline_pos = after_icon.find("\n")
        if newline_pos >= 0:
            return after_icon[newline_pos + 1 :].strip()
        return after_icon.strip()
    # Fallback: возвращаем весь блок (без отрезания шапки)
    return block.strip()


def _extract_sections(block: str) -> list[ParsedSection]:
    """Разбить блок матчапа на `### H3` секции.

    Если `### H3` секций не найдено (некоторые матчапы используют bold-headers типа
    `Option 1 — Most Solid` без `###`) — возвращаем одну неявную секцию `Opener`
    с **полным телом матчапа после шапки**. Reviewer потом разрежет руками.
    """
    h3_matches = list(_H3_RE.finditer(block))
    if not h3_matches:
        body = _strip_matchup_header(block)
        if not body:
            return []
        return [ParsedSection(raw_title="Opener", body=body)]
    sections: list[ParsedSection] = []
    for i, m in enumerate(h3_matches):
        title = m.group(1).strip()
        start = m.end()
        end = h3_matches[i + 1].start() if i + 1 < len(h3_matches) else len(block)
        body = block[start:end].strip()
        sections.append(ParsedSection(raw_title=title, body=body))
    return sections


def _line_number(text: str, byte_offset: int) -> int:
    """1-based номер строки для байтового offset'а."""
    return text.count("\n", 0, byte_offset) + 1


def parse_matchups(source_text: str) -> list[ParsedMatchup]:
    """Главный entry-point: текст всего Mirlol-документа → список ParsedMatchup."""
    result: list[ParsedMatchup] = []
    for start, end in _split_matchups_raw(source_text):
        block = source_text[start:end]
        header = _parse_matchup_header(block)
        if header is None:
            continue
        enemy_comp_raw, difficulty_raw, kill_target = header
        sections = _extract_sections(block)
        if not sections:
            continue  # без секций матчап не имеет смысла
        result.append(
            ParsedMatchup(
                enemy_comp_raw=enemy_comp_raw,
                difficulty_raw=difficulty_raw,
                kill_target_hint=kill_target,
                sections=sections,
                source_lines=(_line_number(source_text, start), _line_number(source_text, end)),
            )
        )
    return result


# ───────────────────────── Render to KB-draft ─────────────────────────


def _canonicalize_section_title(raw_title: str) -> str:
    """Раскрутить `### Foo` → каноничный KB-section title по таблице маппинга.

    Если заголовок — option/plan-вариант → Alternative opener.
    Если незнакомый → Notes (с пометкой TODO для re-classification).
    """
    norm = raw_title.strip().lower()
    if norm in _SECTION_MAPPING:
        return _SECTION_MAPPING[norm]
    if _OPTION_RE.match(norm):
        return "Alternative opener"
    # Незнакомое — складываем в Notes
    return "Notes"


def _merge_sections_into_canonical(parsed: list[ParsedSection]) -> dict[str, list[str]]:
    """Сгруппировать parsed-секции по canonical title'ам.

    Несколько secondary-секций под одним canonical title (например, Option 1 + Option 2 + Plan B
    все идут в Alternative opener) — конкатенируются с сохранением исходного `### Raw` маркера.
    """
    merged: dict[str, list[str]] = {}
    for sec in parsed:
        canonical = _canonicalize_section_title(sec.raw_title)
        # Сохраняем оригинальный заголовок как inline-маркер для traceability
        marker = f"### {sec.raw_title}\n\n"
        chunk = marker + sec.body if sec.raw_title.lower() != canonical.lower() else sec.body
        merged.setdefault(canonical, []).append(chunk)
    return merged


def _build_frontmatter(
    *,
    matchup: ParsedMatchup,
    our_composition: str,
    source_file_path: Path,
    today: date,
) -> dict[str, object]:
    enemy_slug = _enemy_comp_slug(matchup.enemy_comp_raw)
    slug = f"{_comp_short(our_composition)}-vs-{enemy_slug}"
    difficulty = _DIFFICULTY_CANON[matchup.difficulty_raw]

    kill_target: dict[str, str] = {}
    if matchup.kill_target_hint:
        kill_target["primary"] = matchup.kill_target_hint
    else:
        # Fallback: возьмём первый класс из enemy_comp_canonical (heuristic)
        kill_target["primary"] = matchup.enemy_comp_raw.split("/")[0].strip().lower()

    return {
        "slug": slug,
        "schema_version": 1,
        "expansion": "tbc",
        "composition": our_composition,
        "vs": _enemy_comp_canonical(matchup.enemy_comp_raw),
        "bracket": "2v2",
        "difficulty": difficulty,
        "kill_target": kill_target,
        "maps_notes": {},
        "sources": [
            {
                "type": "file",
                "path": source_file_path.name,
                "lines": f"{matchup.source_lines[0]}-{matchup.source_lines[1]}",
                "author": "Mirlol (transcribed)",
                "retrieved": today.isoformat(),
            }
        ],
        "last_reviewed": today.isoformat(),
        "reviewer": None,
        "confidence": "draft",
        "tags": [],
    }


def render_kb_draft(
    *,
    matchup: ParsedMatchup,
    our_composition: str,
    source_file_path: Path,
    today: date | None = None,
) -> tuple[str, str]:
    """Сгенерировать .md draft. Возвращает (slug, full_md_content)."""
    today = today or date.today()
    frontmatter = _build_frontmatter(
        matchup=matchup,
        our_composition=our_composition,
        source_file_path=source_file_path,
        today=today,
    )

    fm_yaml = yaml.safe_dump(
        frontmatter, sort_keys=False, allow_unicode=True, default_flow_style=False
    ).strip()

    merged_sections = _merge_sections_into_canonical(matchup.sections)

    # Канонический порядок секций в выводе
    canonical_order = [
        "Opener",
        "Alternative opener",
        "If enemy opens first",
        "Mid-fight rotation",
        "Win conditions",
        "Notes",
    ]

    body_parts: list[str] = []
    for canonical_title in canonical_order:
        if canonical_title not in merged_sections:
            continue
        body_parts.append(f"## {canonical_title}\n")
        body_parts.append("\n\n".join(merged_sections[canonical_title]))
        body_parts.append("")  # пустая строка-разделитель

    # Конвертация inline-ability работает на тексте целиком, после сборки
    body_md = "\n".join(body_parts).strip() + "\n"
    body_md = _convert_inline_abilities(body_md)

    full = f"---\n{fm_yaml}\n---\n\n{body_md}"
    return str(frontmatter["slug"]), full


def parse_and_write_drafts(
    *,
    source_file: Path,
    our_composition: str,
    output_dir: Path,
    dry_run: bool = False,
) -> list[tuple[str, Path]]:
    """Прочитать Mirlol-файл, распарсить, записать draft'ы.

    Возвращает [(slug, draft_path), ...]. Если `dry_run` — путь возвращается, но файл не пишется.
    """
    text = source_file.read_text(encoding="utf-8")
    matchups = parse_matchups(text)

    results: list[tuple[str, Path]] = []
    for matchup in matchups:
        slug, content = render_kb_draft(
            matchup=matchup,
            our_composition=our_composition,
            source_file_path=source_file,
        )
        out_path = output_dir / f"{slug}.md"
        if not dry_run:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(content, encoding="utf-8")
        results.append((slug, out_path))
    return results
