"""RU-сленг на ВЫХОДЕ бота (Phase 4.10): `[[ability:slug]]` → как это называет команда.

Раньше `pipeline._clean` разворачивал `[[ability:shadowstep]]` в «shadowstep» —
английское слово внутри русской фразы («Рог shadowstep → cheap shot на ханта»),
и живой тест 2026-07-30 справедливо назвал это «кривоватым переводом». Здесь —
рендер по `kb/glossary/slang.json` (владельческий лексикон) с фоллбэком на
`kb/glossary/abilities.json`:

  • `register: standard`  → форма команды («кидни», «блайнд», «преп») — её и пишем;
  • `register: colloquial` → по схеме slang.json такие формы мы только ПОНИМАЕМ на
    входе и не генерим сами, поэтому берём корректное `en_name` из abilities.json
    («Cloak of Shadows»), а не «клоак»;
  • записи нет вовсе → тоже `en_name` из abilities.json; и только если и его нет —
    слаг с пробелами вместо дефисов (прежнее поведение).

Резолв слага в запись сленга — по ДАННЫМ, без хардкод-таблицы соответствий:
прямое совпадение слага → алиасы из abilities.json (`kidney` ∈ aliases
`kidney-shot`) → сверка `en_name` ↔ `slang.en`. На текущем KB это покрывает
~2.3к из 3.5к вхождений русской формой, остальное — аккуратным английским
именем вместо lowercase-мусора (отчёт: `python tools/slang_coverage.py`).

Модуль чистый (json + pathlib), без сети и Discord; всё загружается один раз и
кэшируется в экземпляре. Отсутствие файлов глоссария — не ошибка: рендерер
деградирует до прежнего поведения, чтобы pipeline не падал на пустом KB.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

#: Ссылка на способность в KB-тексте: `[[ability:kidney-shot]]`.
ABILITY_REF_RE = re.compile(r"\[\[ability:([a-z0-9-]+)\]\]")

#: Только эти регистры уходят в вывод бота (см. схему slang.json).
_EMITTABLE_REGISTERS = frozenset({"standard"})


def _load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        log.warning("Глоссарий %s не прочитан (%s) — сленг-рендер деградирует", path, exc)
        return {}
    return data if isinstance(data, dict) else {}


class SlangRenderer:
    """Слаг способности → имя для вывода. Иммутабелен после создания."""

    def __init__(
        self,
        slang: dict[str, Any] | None = None,
        abilities: dict[str, Any] | None = None,
    ) -> None:
        self._slang = slang or {}
        self._abilities = abilities or {}
        self._cache: dict[str, str] = {}

    @classmethod
    def from_kb_path(cls, kb_path: Path | str) -> SlangRenderer:
        """Собрать рендерер из `<kb>/glossary/{slang,abilities}.json` (best-effort)."""
        root = Path(kb_path) / "glossary"
        return cls(_load_json(root / "slang.json"), _load_json(root / "abilities.json"))

    # ── Резолв ────────────────────────────────────────────────────────────────

    def _slang_entry(self, slug: str) -> dict[str, Any] | None:
        """Запись сленга для слага способности: слаг → алиасы → en_name."""
        direct = self._slang.get(slug)
        if isinstance(direct, dict):
            return direct

        ability = self._abilities.get(slug)
        ability = ability if isinstance(ability, dict) else {}
        aliases = {str(a).lower() for a in (ability.get("aliases") or [])}
        if aliases:
            for key, entry in self._slang.items():
                if not isinstance(entry, dict):
                    continue
                if key in aliases or str(entry.get("en", "")).lower() in aliases:
                    return entry

        en_name = str(ability.get("en_name", "")).lower()
        if en_name:
            for entry in self._slang.values():
                if isinstance(entry, dict) and str(entry.get("en", "")).lower() == en_name:
                    return entry
        return None

    def name(self, slug: str) -> str:
        """Имя способности для вывода: русская форма команды или корректное EN-имя."""
        cached = self._cache.get(slug)
        if cached is not None:
            return cached

        entry = self._slang_entry(slug)
        voice = str((entry or {}).get("voice", "")).strip()
        register = str((entry or {}).get("register", "")).strip()
        if voice and register in _EMITTABLE_REGISTERS:
            name = voice
        else:
            ability = self._abilities.get(slug)
            en_name = str(ability.get("en_name", "")).strip() if isinstance(ability, dict) else ""
            name = en_name or slug.replace("-", " ")

        self._cache[slug] = name
        return name

    def render_refs(self, text: str) -> str:
        """Заменить все `[[ability:slug]]` в тексте на выводимые имена."""
        return ABILITY_REF_RE.sub(lambda m: self.name(m.group(1)), text)
