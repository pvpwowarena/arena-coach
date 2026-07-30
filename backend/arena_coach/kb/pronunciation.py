"""Произношение для TTS (Phase 4.12): правим ударения, не трогая текст DM.

Живой тест 30.07: «некоторые ударения и произношения некорректные». Это не баг
кода — системный синтезатор читает игровой сленг как обычные русские слова:
«ро́га» (rogue) превращается в «рога́» (то, что у оленя), аббревиатуры вроде «кс»
читаются вразнобой. Правится это только подсказкой синтезатору.

Слой намеренно сделан ДАННЫМИ (`kb/glossary/voice_pronunciation.json`), а не
кодом: поймал кривое слово в бою — вписал замену, задеплоил, без релиза моста.
Замены применяются ТОЛЬКО к голосовой фразе; текст в Discord DM остаётся
человеческим.

Формат файла:

```json
{
  "replacements": {
    "рога": "ро́га",
    "кс": "контру"
  }
}
```

Ключ — слово целиком (сравнение без учёта регистра, по границам слова), значение
— как это должно звучать: с ударением (U+0301 после гласной, macOS Milena его
понимает) или просто другим словом, которое синтезатор не коверкает.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

log = logging.getLogger(__name__)


class Pronouncer:
    """Пословные замены для TTS. Иммутабелен после создания."""

    def __init__(self, replacements: dict[str, str] | None = None) -> None:
        self._map = {str(k).lower(): str(v) for k, v in (replacements or {}).items() if k}
        self._re = (
            re.compile(
                r"\b("
                + "|".join(sorted(map(re.escape, self._map), key=len, reverse=True))
                + r")\b",
                flags=re.IGNORECASE,
            )
            if self._map
            else None
        )

    @classmethod
    def from_kb_path(cls, kb_path: Path | str) -> Pronouncer:
        """Загрузить `<kb>/glossary/voice_pronunciation.json` (best-effort)."""
        path = Path(kb_path) / "glossary" / "voice_pronunciation.json"
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            log.debug("Словарь произношения %s не прочитан (%s) — говорим как есть", path, exc)
            return cls()
        repl = data.get("replacements") if isinstance(data, dict) else None
        return cls(repl if isinstance(repl, dict) else None)

    def __len__(self) -> int:
        return len(self._map)

    def apply(self, text: str) -> str:
        """Заменить проблемные слова на их «звучащие» варианты."""
        if self._re is None or not text:
            return text
        return self._re.sub(lambda m: self._map[m.group(0).lower()], text)
