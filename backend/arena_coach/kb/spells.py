"""Каталог боевых способностей (Phase 4.12) — решает БЭКЕНД, а не бинарь моста.

Почему появился. До 4.12 список «на что реагируем» был зашит в мост
(`TRACKED_SPELLS`, 27 id, семь классов из девяти — ханта и шамана не было вовсе).
Любое расширение требовало новой сборки и скачивания. Теперь мост форвардит
ВСЕ касты врагов (id + slug имени способности), а что с этим делать — решает
этот каталог, обычный data-файл `kb/glossary/realtime_spells.json`. Добавить
класс, спелл или целую категорию = правка данных и деплой, без релизов.

Резолв идёт в трёх шагах, от надёжного к запасному:
  1. по `spell_id` — не зависит от локали клиента;
  2. по ключу/слагу имени («Scatter Shot» → `scatter_shot`) — покрывает всё, чему
     id ещё не прописан (у enUS-клиента это работает сразу);
  3. по категории — если способность неизвестна, но её имя совпало с одним из
     шаблонов категорий, ответ всё равно будет общий, а не тишина.

Формат `realtime_spells.json`:

```json
{
  "spells": {
    "scatter_shot": {"category": "disorient", "class": "HUNTER",
                     "ids": [19503], "names": ["Scatter Shot"]}
  }
}
```

Ключ записи = `spell_key`, который дальше ищется в таблице реакций
(`orchestrator.reactions`). `category` — запасной путь: на неизвестный спелл
известной категории даётся общая реакция («Стан — тринкет только под добивание»).

Модуль чистый (json + pathlib), грузится один раз, деградирует до пустого
каталога, если файла нет: тогда работает старое поведение по ключам моста.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(name: str) -> str:
    """'Scatter Shot' → 'scatter_shot'; пустая строка остаётся пустой."""
    return _SLUG_RE.sub("_", name.strip().lower()).strip("_")


@dataclass(frozen=True)
class SpellInfo:
    """Разрешённая способность: канонический ключ + категория + класс."""

    key: str
    category: str = ""
    wow_class: str = ""
    #: True — реагируем на НАЧАЛО каста (пока его ещё можно прервать).
    cast_alert: bool = False
    #: Категория для фазы каста (если отличается от основной).
    cast_category: str = ""


class SpellCatalog:
    """Каталог `id | slug → SpellInfo`. Иммутабелен после создания."""

    def __init__(self, spells: dict[str, Any] | None = None) -> None:
        self._by_id: dict[int, SpellInfo] = {}
        self._by_key: dict[str, SpellInfo] = {}
        for key, raw in (spells or {}).items():
            if not isinstance(raw, dict):
                continue
            info = SpellInfo(
                key=key,
                category=str(raw.get("category", "")),
                wow_class=str(raw.get("class", "")).upper(),
                cast_alert=bool(raw.get("cast_alert", False)),
                cast_category=str(raw.get("cast_category", "")),
            )
            self._by_key[key] = info
            for name in raw.get("names", []) or []:
                self._by_key.setdefault(slugify(str(name)), info)
            for spell_id in raw.get("ids", []) or []:
                try:
                    self._by_id[int(spell_id)] = info
                except (TypeError, ValueError):
                    log.warning("realtime_spells: некорректный id %r у %s", spell_id, key)

    @classmethod
    def from_kb_path(cls, kb_path: Path | str) -> SpellCatalog:
        """Загрузить `<kb>/glossary/realtime_spells.json` (best-effort)."""
        path = Path(kb_path) / "glossary" / "realtime_spells.json"
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            log.warning("Каталог спеллов %s не прочитан (%s) — резолв по ключам моста", path, exc)
            return cls()
        spells = data.get("spells") if isinstance(data, dict) else None
        return cls(spells if isinstance(spells, dict) else None)

    def __len__(self) -> int:
        return len(self._by_key)

    def resolve(self, spell_id: int = 0, spell_key: str = "", spell_name: str = "") -> SpellInfo:
        """Определить способность. Пустой `SpellInfo.key` = неизвестна."""
        info = self._by_id.get(spell_id) if spell_id else None
        if info is not None:
            return info
        for candidate in (spell_key, slugify(spell_name)):
            if not candidate:
                continue
            info = self._by_key.get(candidate)
            if info is not None:
                return info
        # Ключ моста мог прийти уже нормализованным (старые версии) — отдаём как есть,
        # чтобы таблица реакций всё равно могла по нему сработать.
        return SpellInfo(key=spell_key or slugify(spell_name))
