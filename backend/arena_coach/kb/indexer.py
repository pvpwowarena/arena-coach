"""KB in-memory индекс. Загружает все .md из kb/matchups/ и kb/drafts/ на старте.

Phase 2: pure in-memory (dict-based), без SQLite FTS5.
Phase 4: заменить на SQLite FTS5 для семантического поиска.

Нормализация ключа: sorted(parts.split("+")) → join("+")
Это позволяет находить «rogue+mage» по запросу «mage+rogue».
"""

from __future__ import annotations

import logging
from pathlib import Path

from arena_coach.kb.loader import KBLoadError, load_kb_doc
from arena_coach.kb.schema import KBDoc

logger = logging.getLogger(__name__)


def _normalize_comp(comp: str) -> str:
    """Нормализация состава: 'mage+rogue' → 'mage+rogue' (sorted, lowercase)."""
    parts = [p.strip().lower() for p in comp.split("+") if p.strip()]
    return "+".join(sorted(parts))


class KBIndex:
    """In-memory индекс KB-документов.

    Основные словари:
    - _by_matchup: (norm_comp, norm_vs) → KBDoc
    - _by_slug:    slug → KBDoc
    - _all:        список всех документов

    Матчап ищется в обоих направлениях: (A vs B) и (B vs A) указывают на
    один документ — потому что стратегия нашего состава vs их.
    Обратный матчап добавляется только если точного обратного документа нет.
    """

    def __init__(self) -> None:
        self._by_matchup: dict[tuple[str, str], KBDoc] = {}
        self._by_slug: dict[str, KBDoc] = {}
        self._all: list[KBDoc] = []
        self._loaded = False

    def load(self, kb_path: Path) -> int:
        """Загрузить все .md файлы из kb_path/matchups/ и kb_path/drafts/.

        Возвращает количество успешно загруженных документов.
        """
        self._by_matchup.clear()
        self._by_slug.clear()
        self._all.clear()

        loaded = 0
        dirs_to_scan = []

        # Основные матчапы (одобренные)
        matchups_dir = kb_path / "matchups"
        if matchups_dir.exists():
            dirs_to_scan.append(matchups_dir)

        # Черновики (drafts) — тоже доступны в Phase 2
        drafts_dir = kb_path / "drafts"
        if drafts_dir.exists():
            dirs_to_scan.append(drafts_dir)

        # Если нет подпапок — сканируем корень
        if not dirs_to_scan:
            dirs_to_scan.append(kb_path)

        for scan_dir in dirs_to_scan:
            for md_file in sorted(scan_dir.glob("*.md")):
                try:
                    doc = load_kb_doc(md_file, glossary=None)
                    self._index_doc(doc)
                    loaded += 1
                except KBLoadError as exc:
                    logger.warning("KB load error %s: %s", md_file.name, exc)
                except Exception as exc:
                    logger.warning("Unexpected error loading %s: %s", md_file.name, exc)

        self._loaded = True
        logger.info("KBIndex loaded %d documents from %s", loaded, kb_path)
        return loaded

    def _index_doc(self, doc: KBDoc) -> None:
        """Добавить документ в индекс."""
        if doc.slug in self._by_slug:
            # Дубликат slug — пропускаем (первый файл приоритетен)
            return

        key = (_normalize_comp(doc.composition), _normalize_comp(doc.vs))
        self._by_matchup[key] = doc

        # Обратный ключ (если нет отдельного документа в другом направлении)
        rev_key = (key[1], key[0])
        if rev_key not in self._by_matchup:
            self._by_matchup[rev_key] = doc

        self._by_slug[doc.slug] = doc
        self._all.append(doc)

    # ── Query API ─────────────────────────────────────────────────────────

    def get_by_matchup(self, comp: str, vs: str) -> KBDoc | None:
        """Найти документ по (наш состав, их состав). Нормализует ввод."""
        key = (_normalize_comp(comp), _normalize_comp(vs))
        return self._by_matchup.get(key)

    def get_by_slug(self, slug: str) -> KBDoc | None:
        """Найти документ по slug."""
        return self._by_slug.get(slug.lower())

    @property
    def all_docs(self) -> list[KBDoc]:
        """Список всех загруженных документов (копия)."""
        return list(self._all)

    def list_compositions(self) -> list[str]:
        """Список уникальных составов нашей стороны."""
        return sorted({doc.composition for doc in self._all})

    def list_all_matchups(self) -> list[tuple[str, str]]:
        """Список (comp, vs) для всех документов."""
        return [(doc.composition, doc.vs) for doc in self._all]

    def __len__(self) -> int:
        return len(self._all)

    def __bool__(self) -> bool:
        return bool(self._all)


__all__ = ["KBIndex", "normalize_comp"]


def normalize_comp(comp: str) -> str:
    """Публичный алиас для нормализации состава (используется в cog'ах)."""
    return _normalize_comp(comp)
