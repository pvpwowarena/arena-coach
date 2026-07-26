"""Эвристический килл-таргет для сетапов ВНЕ KB (Phase 4.7).

Когда матчапа в KB нет (нестандартный комбо: mage+mage+mage, hpal+ret+rogue),
килл-таргет из frontmatter недоступен. Здесь — грубая эвристика приоритета цели
по классам/спекам. Она ЯВНО провизорная (помечается «≈» в DM): основной разбор
незнакомого сетапа даёт LLM, а эвристика — мгновенный floor и фолбэк, если LLM
недоступен.

Логика приоритета (TBC 2.4.3, взгляд melee-cleave вроде rogue+X):
  1. Не-хилеры-клоти (mage/warlock/spriest) — умирают быстрее всего под трейном.
  2. Кожа/мейл-дпс (hunter, ele-shaman, feral-druid, ret-pala, rogue).
  3. Хилеры (resto/holy/disc) — киллятся тяжело, обычно только в размен/притеснение,
     поэтому по умолчанию НЕ основная цель (кроме случая, когда враги — все хилеры).

Чистый модуль, детерминированный, покрыт тестами.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

# Спеки-хилеры: по умолчанию НЕ основная цель добива (кроме all-healer).
_HEALER_SPECS: frozenset[str] = frozenset(
    {
        "resto-druid",
        "resto-shaman",
        "holy-paladin",
        "holy-priest",
        "discipline-priest",
    }
)

# Класс, который «обычно хилер», если спек неизвестен, — понижаем в приоритете,
# т.к. в наших брекетах paladin/чаще всего holy, druid/чаще resto.
_LIKELY_HEALER_CLASS: frozenset[str] = frozenset({"paladin"})

# Приоритет добива по классу: меньше индекс — выше приоритет. Не в списке → низкий.
_CLASS_RANK: dict[str, int] = {
    "warlock": 0,
    "mage": 1,
    "priest": 2,  # spriest — топ; healer-priest понизим отдельно по спеку
    "shaman": 3,
    "hunter": 4,
    "druid": 5,
    "rogue": 6,
    "warrior": 7,
    "paladin": 8,
}

_HEALER_PENALTY = 100  # сдвигает хилера в самый низ, но оставляет детерминизм


@dataclass(frozen=True)
class KillPick:
    """Результат эвристики: цель + флаг уверенности (всегда провизорно для unknown)."""

    target: str  # спек-slug если известен, иначе class-slug (lowercase)
    provisional: bool = True


def _class_of(part: str) -> str:
    """'resto-druid' → 'druid'; 'holy-paladin' → 'paladin'; 'mage' → 'mage'."""
    p = part.strip().lower()
    return p.rsplit("-", 1)[-1] if "-" in p else p


def _is_healer(cls: str, spec: str | None) -> bool:
    if spec and spec.strip().lower() in _HEALER_SPECS:
        return True
    return spec is None and cls in _LIKELY_HEALER_CLASS


def _rank(cls: str, spec: str | None) -> int:
    base = _CLASS_RANK.get(cls, 50)
    if _is_healer(cls, spec):
        base += _HEALER_PENALTY
    return base


def heuristic_kill_target(
    enemy_classes: Sequence[str],
    enemy_specs: Sequence[str | None] | None = None,
) -> KillPick | None:
    """Выбрать провизорный килл-таргет из классов/спеков врагов.

    Возвращает более точный спек-slug, если он известен, иначе класс-slug.
    None — если список врагов пуст. Хилеры выбираются только когда все враги —
    хилеры (иначе цель — самый «убиваемый» дпс).
    """
    classes = [c.strip().lower() for c in enemy_classes if c and c.strip()]
    if not classes:
        return None
    specs_raw = list(enemy_specs) if enemy_specs is not None else []
    specs: list[str | None] = []
    for i in range(len(classes)):
        raw = specs_raw[i] if i < len(specs_raw) else None
        specs.append(raw.strip().lower() if raw else None)

    # индекс лучшего (минимальный ранг; при равенстве — левее = стабильно)
    best_i = min(range(len(classes)), key=lambda i: (_rank(classes[i], specs[i]), i))
    spec = specs[best_i]
    target = spec if spec else classes[best_i]
    return KillPick(target=target, provisional=True)


__all__ = ["KillPick", "heuristic_kill_target"]
