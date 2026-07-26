"""KB retriever: высокоуровневый поиск по KB индексу.

Обёртка над KBIndex с дополнительной логикой:
- fuzzy-matching алиасов (rdruid → resto-druid, rsham → resto-shaman, и т.д.)
- поиск «близких» матчапов если точного нет
- список всех доступных матчапов для подсказок
"""

from __future__ import annotations

from collections.abc import Sequence

from arena_coach.kb.indexer import KBIndex, _normalize_comp, comp_part_to_class, comp_to_classes
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


def _doc_consistent_with_specs(vs: str, known_specs: Sequence[str]) -> bool:
    """Документ vs совместим с известными спеками врагов (Phase 4.7).

    Для каждого известного спека S (базовый класс B): среди частей vs того же
    класса B должна быть часть == B (без спека) или == S. Если у vs есть ДРУГОЙ
    спек того же класса (holy-paladin при известном ret-paladin) — противоречие.
    Документ с базовым классом ('vs: warrior+mage') совместим с любым спеком
    этого класса (frost-mage подходит под 'mage').
    """
    parts = [p.strip().lower() for p in vs.split("+") if p.strip()]
    for spec in known_specs:
        base = comp_part_to_class(spec)
        same_class = [p for p in parts if comp_part_to_class(p) == base]
        if same_class and not any(p in (base, spec) for p in same_class):
            return False
    return True


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
        enemy_specs: Sequence[str | None] | None = None,
    ) -> list[KBDoc]:
        """Кандидаты матчапа для real-time pipeline (Phase 4.1 + спеки 4.7).

        Аддон/мост присылает классы врагов, а по мере боя — и спеки (по
        сигнатурным кастам). Базовый матч идёт по классам: враги WARRIOR+PALADIN
        находят и 'vs: warrior+holy-paladin', и 'vs: warrior+ret-paladin'. Если
        спеки известны — сужаем до совместимых: знаем ret → holy-документ
        отбрасывается (чужой спек = неверный план). Если спек противоречит ВСЕМ
        документам класс-уровня, возвращаем [] — вызывающий уходит на
        LLM-разбор незнакомого сетапа (лучше, чем совет под чужой спек).

        Args:
            enemy_classes: классы врагов (напр. ["WARRIOR", "PALADIN"]).
            our_comp_hint: наш состав (напр. "rogue+mage"); None → любой.
            enemy_specs: спеки в том же порядке (None где неизвестно); None → без
                сужения (обратная совместимость с Phase 4.1).

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
        candidates = sorted(docs, key=lambda d: d.slug)

        if enemy_specs:
            known = [s.strip().lower() for s in enemy_specs if s and s.strip()]
            if known:
                return [d for d in candidates if _doc_consistent_with_specs(d.vs, known)]
        return candidates

    def find_partial_candidates(
        self,
        known_enemy_classes: Sequence[str],
        our_comp_hint: str | None = None,
    ) -> list[KBDoc]:
        """Кандидаты по ЧАСТИЧНО раскрытому составу врагов (Phase 4.7).

        Пока не все враги опознаны (в 2v2 виден только друид) — возвращаем
        документы, чьи vs-классы включают уже известные, с фильтром по нашему
        составу. Нужно для мгновенного провизорного килл-таргета в первые секунды,
        пока полный матч ещё не сложился.
        """
        known = tuple(sorted(c.strip().lower() for c in known_enemy_classes if c and c.strip()))
        if not known:
            return []
        our: tuple[str, ...] | None = None
        if our_comp_hint:
            our = comp_to_classes(normalize_user_comp(our_comp_hint))
        known_set = set(known)
        result: list[KBDoc] = []
        for doc in self._index.all_docs:
            if not known_set.issubset(set(comp_to_classes(doc.vs))):
                continue
            if our is not None and comp_to_classes(doc.composition) != our:
                continue
            result.append(doc)
        return sorted(result, key=lambda d: d.slug)

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
