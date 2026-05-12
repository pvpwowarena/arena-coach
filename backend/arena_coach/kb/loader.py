"""Загрузчик KB-документов из Markdown-файлов с YAML frontmatter.

Парсит:
- YAML frontmatter (между двумя `---`-маркерами) → поля `KBDoc`
- Тело: каждая `## H2` секция → `Section(title, body_md)`

Резолвит:
- Inline-ссылки `[[ability:<slug>]]` — проверяет, что slug есть в глоссарии
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import yaml
from pydantic import ValidationError

from arena_coach.kb.schema import KBDoc, Section

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)
_H2_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_ABILITY_REF_RE = re.compile(r"\[\[ability:([a-z0-9-]+)\]\]")


class KBLoadError(Exception):
    """Базовый класс ошибок загрузки KB."""


class KBFrontmatterError(KBLoadError):
    pass


class KBSchemaError(KBLoadError):
    pass


class KBOrphanAbilityError(KBLoadError):
    """Inline-ссылка [[ability:X]] не найдена в глоссарии."""


@dataclass(frozen=True)
class GlossaryIndex:
    """Минимальный интерфейс к глоссарию: проверка существования slug'а."""

    slugs: frozenset[str]

    @classmethod
    def from_file(cls, path: Path) -> GlossaryIndex:
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(slugs=frozenset(data.keys()))

    @classmethod
    def empty(cls) -> GlossaryIndex:
        return cls(slugs=frozenset())


def _split_frontmatter(text: str) -> tuple[dict[str, object], str]:
    """Разделить .md на frontmatter (dict) и тело (str)."""
    match = _FRONTMATTER_RE.match(text)
    if not match:
        raise KBFrontmatterError(
            "Frontmatter не найден. Файл обязан начинаться с '---' блока с YAML."
        )
    fm_raw, body = match.group(1), match.group(2)
    try:
        fm = yaml.safe_load(fm_raw)
    except yaml.YAMLError as e:
        raise KBFrontmatterError(f"YAML парсинг упал: {e}") from e
    if not isinstance(fm, dict):
        raise KBFrontmatterError(f"Frontmatter должен быть YAML-mapping, получено: {type(fm).__name__}")
    return fm, body


def _parse_sections(body: str) -> list[Section]:
    """Разбить тело на секции по `## H2` заголовкам."""
    # Находим все H2-заголовки и их позиции
    h2_matches = list(_H2_RE.finditer(body))
    if not h2_matches:
        return []

    sections: list[Section] = []
    for i, m in enumerate(h2_matches):
        title = m.group(1).strip()
        start = m.end()
        end = h2_matches[i + 1].start() if i + 1 < len(h2_matches) else len(body)
        section_body = body[start:end].strip()
        if section_body:
            sections.append(Section(title=title, body_md=section_body))
    return sections


def _validate_ability_refs(sections: list[Section], glossary: GlossaryIndex) -> None:
    """Все [[ability:<slug>]] должны существовать в глоссарии."""
    orphans: set[str] = set()
    for sec in sections:
        for m in _ABILITY_REF_RE.finditer(sec.body_md):
            slug = m.group(1)
            if slug not in glossary.slugs:
                orphans.add(slug)
    if orphans:
        raise KBOrphanAbilityError(
            "Способности не найдены в глоссарии: " + ", ".join(sorted(orphans))
        )


def load_kb_doc(path: Path, glossary: GlossaryIndex | None = None) -> KBDoc:
    """Прочитать .md файл и вернуть валидный `KBDoc`.

    Аргументы:
        path: путь к .md файлу.
        glossary: индекс глоссария; если передан — проверяется orphan-резолюция
            inline [[ability:X]]-ссылок. Если None — проверка пропускается
            (полезно для CI smoke-тестов до того, как глоссарий заполнен).

    Исключения:
        KBFrontmatterError, KBSchemaError, KBOrphanAbilityError.
    """
    text = path.read_text(encoding="utf-8")
    fm, body = _split_frontmatter(text)
    sections = _parse_sections(body)

    # Frontmatter получает sections отдельным полем, не из YAML
    fm["sections"] = [s.model_dump() for s in sections]

    try:
        doc = KBDoc.model_validate(fm)
    except ValidationError as e:
        raise KBSchemaError(f"Pydantic-валидация упала для {path}: {e}") from e

    if glossary is not None:
        _validate_ability_refs(sections, glossary)

    return doc


def validate_directory(
    directory: Path, glossary_path: Path | None = None
) -> tuple[int, list[tuple[Path, str]]]:
    """Прогнать все .md в директории через схему. Используется в CI.

    Возвращает (ok_count, [(path, error_msg), ...]).
    """
    glossary = (
        GlossaryIndex.from_file(glossary_path) if glossary_path else GlossaryIndex.empty()
    )

    ok = 0
    errors: list[tuple[Path, str]] = []
    for path in sorted(directory.glob("*.md")):
        try:
            load_kb_doc(path, glossary=glossary if glossary_path else None)
            ok += 1
        except KBLoadError as e:
            errors.append((path, str(e)))
    return ok, errors
