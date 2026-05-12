"""Извлечение справочника способностей из Mirlol-стиля Markdown.

Mirlol-формат inline-способности:

    ![<display name>](https://render.worldofwarcraft.com/icons/<size>/<icon>.jpg)<text>

Где `<icon>` — имя файла в WoW media (например, `ability_cheapshot`).
Используется как стабильный slug-источник: один icon ↔ одна способность.

Этот модуль:
1. Сканирует Markdown-файл, извлекает все inline-ability ссылки.
2. Группирует по icon → собирает все варианты display-name'ов (для авто-дедупа: 'cheap shot', 'cheapshot', 'Cheap Shot' указывают на один и тот же ability).
3. Генерирует `abilities.json` skeleton: slug + en_name + icon, остальные поля (spell_id, dr_category, duration, ru_name) — пусты, заполняются вручную.

Это **не делает LLM-нормализации** — это чистый regex-extract. Стабильно, повторяемо.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import TypedDict

# ![label](https://render.worldofwarcraft.com/icons/<size>/<icon>.jpg)<trailing-name>
_ABILITY_INLINE_RE = re.compile(
    r"!\[(?P<label>[^\]]+)\]"
    r"\(https?://render\.worldofwarcraft\.com/icons/(?P<size>\d+)/(?P<icon>[a-zA-Z0-9_]+)\.jpg\)"
    r"(?P<trailing>[A-Za-z][A-Za-z0-9 \-']*)?"
)


class AbilityEntry(TypedDict, total=False):
    """Запись в abilities.json. spell_id/dr_category/duration/ru_name — заполняются вручную."""

    slug: str
    en_name: str
    icon: str
    spell_id: int | None
    dr_category: str | None
    duration: float | None
    school: str | None
    ru_name: str | None
    class_: str | None  # class hint (rogue/mage/etc.) — заполнить вручную, мы не угадываем
    aliases: list[str]  # все встретившиеся написания (cheap shot / cheapshot / Cheap Shot)


def _icon_to_slug(icon: str) -> str:
    """Fallback: вывести slug из имени icon'а, когда другого нет.

    Используется только когда ни trailing, ни label не дают пригодного текста.
    `ability_cheapshot` → `cheap-shot`; `spell_shadow_mindsteal` → `mindsteal`.

    **Не идеально**, поэтому всегда предпочитаем `_derive_slug`, который смотрит на
    человеческий label/trailing из текста.
    """
    s = icon.lower()
    for prefix in ("ability_", "inv_"):
        if s.startswith(prefix):
            s = s[len(prefix) :]
    s = re.sub(r"^spell_[a-z]+_", "", s)
    s = s.replace("_", "-")
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", "-", s).lower()
    return s


def _is_class_icon(icon: str) -> bool:
    """`classicon_*` — это иконки классов, не способности."""
    return icon.lower().startswith("classicon_")


_SLUG_NORMALIZE_RE = re.compile(r"[^a-z0-9]+")


def derive_ability_slug(label: str, trailing: str | None, icon: str) -> str:
    """Главный slug-resolver. Приоритет: **label** > trailing > _icon_to_slug(icon).

    `label` — текст внутри `![...]`, выбран автором как канонический ярлык способности.
    `trailing` — что идёт после URL; в Mirlol-тексте это обычно повтор label'а, но может
    «перетечь» в продолжение предложения, поэтому полагаться на trailing для slug'а нельзя.

    Примеры (из Mirlol):
        `![cheap shot](ability_cheapshot.jpg)cheap shot to stall hots` → 'cheap-shot'
        `![premed](spell_shadow_possession.jpg)Premed`                  → 'premed'
        `![blind](spell_shadow_mindsteal.jpg)blind him`                 → 'blind'
        `![sap](ability_sap.jpg)Sap the priest`                         → 'sap'
        `![kidney](ability_rogue_kidneyshot.jpg)kidney shots with big burst` → 'kidney'

    Замечание: label="kidney" и label="kidney shot" для одной и той же иконки
    `ability_rogue_kidneyshot.jpg` дают разные slug'и ('kidney' vs 'kidney-shot').
    Дедупликация — задача reviewer'а при first-pass review глоссария: открыть
    `abilities.json`, схлопнуть дубли вручную (см. поле `aliases` каждой записи).
    """
    source = (label or "").strip()
    if not source or not re.search(r"[a-zA-Z]", source):
        source = (trailing or "").strip()
    if not source or not re.search(r"[a-zA-Z]", source):
        return _icon_to_slug(icon)
    slug = _SLUG_NORMALIZE_RE.sub("-", source.lower()).strip("-")
    return slug or _icon_to_slug(icon)


def _normalize_display(label: str, trailing: str | None) -> str:
    """Получить «человеческое» имя способности."""
    cleaned = (trailing or label).strip()
    return cleaned if cleaned else label.strip()


def extract_abilities(text: str) -> dict[str, AbilityEntry]:
    """Прогнать Markdown через regex и собрать словарь {slug: AbilityEntry}.

    Slug определяется через `derive_ability_slug` — приоритет за trailing-текстом.
    Class-иконки (`classicon_*`) пропускаются — это не способности.
    """
    by_slug: dict[str, AbilityEntry] = {}
    aliases_by_slug: dict[str, set[str]] = defaultdict(set)
    icons_by_slug: dict[str, set[str]] = defaultdict(set)

    for m in _ABILITY_INLINE_RE.finditer(text):
        icon = m.group("icon")
        if _is_class_icon(icon):
            continue
        label = m.group("label")
        trailing = m.group("trailing")
        slug = derive_ability_slug(label, trailing, icon)
        display = _normalize_display(label, trailing)

        aliases_by_slug[slug].add(label.strip())
        if trailing:
            aliases_by_slug[slug].add(trailing.strip())
        icons_by_slug[slug].add(icon)

        if slug not in by_slug:
            by_slug[slug] = {
                "slug": slug,
                "en_name": display.title(),
                "icon": icon,
                "spell_id": None,
                "dr_category": None,
                "duration": None,
                "school": None,
                "ru_name": None,
                "class_": None,
                "aliases": [],
            }

    # Финализируем aliases и фиксируем icon
    for slug, entry in by_slug.items():
        entry["aliases"] = sorted(aliases_by_slug[slug])
    return by_slug


def extract_from_files(paths: list[Path]) -> dict[str, AbilityEntry]:
    """Слить экстракты нескольких файлов в один словарь."""
    merged: dict[str, AbilityEntry] = {}
    aliases_merged: dict[str, set[str]] = defaultdict(set)
    for path in paths:
        partial = extract_abilities(path.read_text(encoding="utf-8"))
        for slug, entry in partial.items():
            aliases_merged[slug].update(entry["aliases"])
            if slug not in merged:
                merged[slug] = entry
    # Финализируем aliases
    for slug, aliases in aliases_merged.items():
        merged[slug]["aliases"] = sorted(aliases)
    return dict(sorted(merged.items()))


def write_glossary_skeleton(abilities: dict[str, AbilityEntry], output_path: Path) -> None:
    """Записать abilities.json. Если файл уже существует — **мерджит**, сохраняя ручные правки.

    Стратегия мерджа: для каждого slug, если он уже в файле — оставляем
    существующие непустые значения spell_id/dr_category/duration/ru_name/class_/school,
    но обновляем aliases (поскольку extract может найти новые написания).
    """
    existing: dict[str, AbilityEntry] = {}
    if output_path.exists():
        existing = json.loads(output_path.read_text(encoding="utf-8"))

    merged: dict[str, AbilityEntry] = {}
    for slug, new_entry in abilities.items():
        if slug in existing:
            old = existing[slug]
            merged[slug] = {
                "slug": slug,
                "en_name": old.get("en_name") or new_entry["en_name"],
                "icon": new_entry["icon"],
                "spell_id": old.get("spell_id"),
                "dr_category": old.get("dr_category"),
                "duration": old.get("duration"),
                "school": old.get("school"),
                "ru_name": old.get("ru_name"),
                "class_": old.get("class_"),
                "aliases": new_entry["aliases"],
            }
        else:
            merged[slug] = new_entry

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
