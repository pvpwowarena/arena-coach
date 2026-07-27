"""Мета-приоры вражеских составов (стелс-предугадывание v1, детерминированное).

Идея из бэклога «стелс-предугадывание»: пока состав раскрыт частично (или не
раскрыт вовсе — полный инвиз), подсказать игроку, ЧТО это вероятнее всего по
мете TBC 2.4.3, а не молчать до полного раскрытия. Никакого LLM и внешних
данных: статическая таблица весов, курированная из тех же tier-листов
(Warcraft Tavern / Skill Capped / Icy Veins), на которых построена KB.

Веса — грубый приор популярности на ладдере (S≈90 … C≈20), не «сила компа».
Матчинг мультисетовый: известные классы (с повторами!) должны входить в состав.
Когда добавится источник живой статистики рейтинга (data-acquisition из
бэклога), таблица заменится на генерируемую — интерфейс модуля не изменится.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence

# (классы состава, вес 0-100, короткое имя для DM)
_META_2V2: list[tuple[tuple[str, ...], int, str]] = [
    (("mage", "rogue"), 90, "Роге/Маг"),
    (("druid", "warlock"), 85, "Лок/Друид"),
    (("druid", "warrior"), 85, "Варр/Друид"),
    (("priest", "rogue"), 75, "Роге/Прист"),
    (("druid", "rogue"), 72, "Роге/Друид"),
    (("priest", "warlock"), 70, "Лок/Прист"),
    (("mage", "priest"), 65, "Маг/Прист"),
    (("paladin", "warrior"), 65, "Варр/Пала"),
    (("shaman", "warrior"), 55, "Варр/Шаман"),
    (("rogue", "rogue"), 50, "Дабл-роге"),
    (("druid", "hunter"), 45, "Хант/Друид"),
    (("paladin", "shaman"), 42, "Рет/Шаман"),
    (("shaman", "warlock"), 40, "Лок/Шаман"),
    (("paladin", "rogue"), 35, "Роге/Пала"),
    (("druid", "druid"), 22, "Дабл-друид"),
]

_META_3V3: list[tuple[tuple[str, ...], int, str]] = [
    (("mage", "priest", "rogue"), 90, "RMP"),
    (("priest", "rogue", "warlock"), 85, "RLP"),
    (("mage", "priest", "warlock"), 80, "MLP"),
    (("druid", "rogue", "warlock"), 75, "RLD"),
    (("druid", "mage", "rogue"), 70, "RMD"),
    (("priest", "shaman", "warlock"), 65, "Shadowplay"),
    (("druid", "warlock", "warrior"), 60, "WLD"),
    (("mage", "priest", "warrior"), 55, "WMP"),
    (("mage", "priest", "shaman"), 50, "Маг/Прист/Шаман"),
    (("druid", "hunter", "priest"), 45, "Хант/Прист/Друид"),
    (("priest", "warrior", "warrior"), 35, "Дабл-варр/Прист"),
    (("druid", "rogue", "rogue"), 30, "Дабл-роге/Друид"),
    (("druid", "druid", "warrior"), 25, "Варр/Дабл-друид"),
    (("rogue", "rogue", "rogue"), 15, "Трипл-роге"),
]

# Классы, умеющие сидеть в стелсе на воротах (полный инвиз = только они).
_STEALTH_CLASSES = {"rogue", "druid"}


def _table(bracket: str) -> list[tuple[tuple[str, ...], int, str]]:
    if bracket == "2v2":
        return _META_2V2
    if bracket == "3v3":
        return _META_3V3
    return []


def likely_comps(
    known_enemy_classes: Sequence[str], bracket: str, top: int = 2
) -> list[tuple[tuple[str, ...], str]]:
    """Топ мета-составов, содержащих уже известные классы (мультисет-вхождение).

    Возвращает [(классы, короткое имя)] по убыванию веса; пусто, если известные
    классы не вписываются ни в один мета-состав (экзотика — пусть работает
    обычный partial/advice-путь без гаданий).
    """
    known = Counter(c.strip().lower() for c in known_enemy_classes if c and c.strip())
    out: list[tuple[int, tuple[str, ...], str]] = []
    for comp, weight, label in _table(bracket):
        if not known:
            continue
        comp_count = Counter(comp)
        if all(comp_count[cls] >= n for cls, n in known.items()):
            out.append((weight, comp, label))
    out.sort(key=lambda t: (-t[0], t[1]))
    return [(comp, label) for _, comp, label in out[:top]]


def stealth_comps(bracket: str, top: int = 2) -> list[tuple[tuple[str, ...], str]]:
    """Топ мета-составов, способных выйти на ворота в ПОЛНОМ инвизе.

    Полный инвиз возможен, только если ВСЕ классы состава умеют стелс
    (rogue/druid) — остальные мета-составы выдали бы себя кастом/бафом.
    """
    out = [
        (weight, comp, label)
        for comp, weight, label in _table(bracket)
        if set(comp) <= _STEALTH_CLASSES
    ]
    out.sort(key=lambda t: (-t[0], t[1]))
    return [(comp, label) for _, comp, label in out[:top]]


def guess_line(guesses: list[tuple[tuple[str, ...], str]]) -> str | None:
    """Строка для DM: «🕵 По мете это чаще всего: RMP или RLP»."""
    if not guesses:
        return None
    labels = [label for _, label in guesses]
    joined = " или ".join(labels) if len(labels) <= 2 else ", ".join(labels)
    return f"🕵 По мете это чаще всего: **{joined}**"


__all__ = ["guess_line", "likely_comps", "stealth_comps"]
