"""KB retriever: высокоуровневый поиск по KB индексу.

Обёртка над KBIndex с дополнительной логикой:
- fuzzy-matching алиасов (rdruid → resto-druid, rsham → resto-shaman, и т.д.)
- поиск «близких» матчапов если точного нет
- список всех доступных матчапов для подсказок
"""

from __future__ import annotations

from collections.abc import Sequence

from arena_coach.kb.indexer import KBIndex, _normalize_comp, comp_to_classes
from arena_coach.kb.schema import KBDoc

# Таблица алиасов для нормализации ввода пользователя
_ALIASES: dict[str, str] = {
    # Resto Druid
    "rdruid": "resto-druid",
    "restodru": "resto-druid",
    "restod": "resto-druid",
    "rdru": "resto-druid",
    # Resto Shaman
    "rsham": "resto-shaman",
    "restosham": "resto-shaman",
    "rshaman": "resto-shaman",
    "rshammy": "resto-shaman",
    # Holy Paladin
    "hpala": "holy-paladin",
    "holypal": "holy-paladin",
    "hpal": "holy-paladin",
    # Holy Priest
    "hpriest": "holy-priest",
    "holypriest": "holy-priest",
    # Discipline Priest
    "disc": "discipline-priest",
    "discpriest": "discipline-priest",
    "dpriest": "discipline-priest",
    # Shadow Priest
    "spriest": "shadow-priest",
    "shadowp": "shadow-priest",
    # Ret Paladin
    "ret": "ret-paladin",
    "retpala": "ret-paladin",
    "retpal": "ret-paladin",
    # Warlock
    "lock": "warlock",
    "aff": "aff-warlock",
    "demo": "demo-warlock",
    "destro": "destro-warlock",
    # Mage
    "fmage": "frost-mage",
    "arcane": "arcane-mage",
    # Rogue
    "sub": "sub-rogue",
    "mutilate": "mut-rogue",
    "mut": "mut-rogue",
    # Druid
    "feral": "feral-druid",
    "balance": "boomkin",
    # Warrior
    "arms": "arms-warrior",
    "fury": "fury-warrior",
    # Hunter
    "bm": "bm-hunter",
    "mm": "mm-hunter",
    "surv": "surv-hunter",
    # Shaman
    "ele": "ele-shaman",
    "elesham": "ele-shaman",
    # Priest — общий
    "priest": "priest",
    # Common abbreviations
    "war": "warrior",
    "warr": "warrior",
    "rog": "rogue",
    "dru": "druid",
    "pal": "paladin",
    "sham": "shaman",
    "hun": "hunter",
}


def _resolve_alias(part: str) -> str:
    """Заменить алиас на канонический slug если найден."""
    return _ALIASES.get(part.lower(), part.lower())


def normalize_user_comp(comp: str) -> str:
    """Нормализовать состав из ввода пользователя, применяя алиасы.

    Пример: 'RM' → 'rogue+mage' (если пользователь пишет через +).
    Пример: 'rogue+rsham' → 'resto-shaman+rogue' (sorted, алиасы).
    """
    parts = [_resolve_alias(p.strip()) for p in comp.replace(" ", "").split("+") if p.strip()]
    return "+".join(sorted(parts))


class KBRetriever:
    """Поиск документов в KBIndex с нормализацией пользовательского ввода."""

    def __init__(self, index: KBIndex) -> None:
        self._index = index

    def find_matchup(self, our_comp: str, vs_comp: str) -> KBDoc | None:
        """Найти матчап по пользовательскому вводу (с нормализацией алиасов).

        Стратегия поиска:
        1. Точный матч после нормализации.
        2. Матч с нормализованным нашим составом vs. любой vs (если 1 не нашёл).
        """
        norm_ours = normalize_user_comp(our_comp)
        norm_vs = normalize_user_comp(vs_comp)
        return self._index.get_by_matchup(norm_ours, norm_vs)

    def find_by_slug(self, slug: str) -> KBDoc | None:
        return self._index.get_by_slug(slug)

    def find_realtime_candidates(
        self,
        enemy_classes: Sequence[str],
        our_comp_hint: str | None = None,
    ) -> list[KBDoc]:
        """Кандидаты матчапа для real-time pipeline (Phase 4.1).

        Аддон присылает только КЛАССЫ врагов (спек с ворот не виден), поэтому
        матчим по базовым классам: враги WARRIOR+PALADIN найдут и
        'vs: warrior+holy-paladin', и 'vs: warrior+ret-paladin' — все кандидаты
        возвращаются, вызывающий код решает как показать неоднозначность.

        Args:
            enemy_classes: классы врагов из ARENA_START (напр. ["WARRIOR", "PALADIN"])
            our_comp_hint: наш состав из allies или $BRIDGE_OUR_COMP (напр. "rogue+mage");
                None → ищем по любому нашему составу.

        Returns:
            Отсортированный по slug список кандидатов ([] если матчапа нет).
        """
        enemy = tuple(sorted(c.strip().lower() for c in enemy_classes if c and c.strip()))
        if not enemy:
            return []

        our: tuple[str, ...] | None = None
        if our_comp_hint:
            our = comp_to_classes(normalize_user_comp(our_comp_hint))

        docs = self._index.find_by_classes(our, enemy)
        if not docs and our is not None:
            # Наш состав не совпал ни с одним документом — покажем хоть что-то
            # по этим врагам (совет соседнего состава лучше, чем тишина).
            docs = self._index.find_by_classes(None, enemy)
        return sorted(docs, key=lambda d: d.slug)

    def list_compositions(self) -> list[str]:
        return self._index.list_compositions()

    def list_all_matchups(self) -> list[tuple[str, str]]:
        return self._index.list_all_matchups()

    def suggest_similar(self, our_comp: str, vs_comp: str) -> list[str]:
        """Предложить похожие матчапы если точного нет.

        Возвращает список slug'ов документов с тем же нашим составом.
        """
        norm_ours = normalize_user_comp(our_comp)
        suggestions = []
        for doc in self._index.all_docs:
            if _normalize_comp(doc.composition) == norm_ours:
                suggestions.append(f"`{doc.composition} vs {doc.vs}`")
        return suggestions[:5]  # Не более 5 подсказок


__all__ = ["KBRetriever", "normalize_user_comp"]
