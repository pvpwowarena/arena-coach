"""Короткие голосовые фразы для TTS (Phase 4.5).

В арене читать некогда — голосовая реплика должна быть ≤8 слов и на игровом
RU-сленге («айсблок», «бабл», «клок»), а не «Ice Block activated». Текстовые
DM это НЕ заменяет: phrase builder генерит ОТДЕЛЬНЫЙ короткий текст, а не
режет текстовый hint (см. docs/phase-4.5-voice.md, раздел Risks).

Модуль чистый (без discord/edge-tts) — используется api-процессом (pipeline)
и покрыт юнит-тестами.
"""

from __future__ import annotations

# Классы врагов (UPPERCASE из bridge) → короткий RU-сленг
_CLASS_RU: dict[str, str] = {
    "WARRIOR": "вар",
    "MAGE": "маг",
    "ROGUE": "рога",
    "PRIEST": "прист",
    "WARLOCK": "лок",
    "PALADIN": "пала",
    "DRUID": "дру",
    "HUNTER": "хант",
    "SHAMAN": "шам",
}

# kill_target из KB (class-level, lowercase) → RU
_TARGET_RU: dict[str, str] = {k.lower(): v for k, v in _CLASS_RU.items()}

# spell_key (TRACKED_SPELLS бриджа) → как это называют в войсе
_SPELL_RU: dict[str, str] = {
    "evasion": "эвижн",
    "cloak_of_shadows": "клок",
    "vanish": "ваниш",
    "preparation": "преп",
    "blind": "блайнд",
    "ice_block": "айсблок",
    "divine_shield": "бабл",
    "shield_wall": "стенка",
    "retaliation": "ретка",
    "pain_suppression": "саппрешн",
    "power_infusion": "инфьюжн",
    "bloodlust": "ласт",
    "elemental_mastery": "элем мастери",
    "innervate": "иннервейт",
    "barkskin": "кора",
}


def _class_ru(wow_class: str) -> str:
    return _CLASS_RU.get(wow_class.upper(), wow_class.lower())


def class_ru(wow_class: str) -> str:
    """'ROGUE' → 'рога'. Публичная обёртка для `state_advice` (Phase 4.14)."""
    return _class_ru(wow_class)


def spell_ru(spell_key: str) -> str:
    """'ice_block' → 'айсблок'; неизвестный ключ — как есть, без подчёркиваний."""
    return _SPELL_RU.get(spell_key, spell_key.replace("_", " "))


def _target_ru(target: str) -> str:
    """'mage' → 'маг'; спек-слаг 'resto-druid' → 'дру' (по последнему слову)."""
    low = target.lower().strip()
    if low in _TARGET_RU:
        return _TARGET_RU[low]
    tail = low.rsplit("-", 1)[-1]
    return _TARGET_RU.get(tail, low)


#: Как игроки называют дубли: «дабл рога», «трипл маг» (Phase 4.14).
_MULTIPLIER_RU: dict[int, str] = {2: "дабл", 3: "трипл"}


def _enemy_names(enemy_classes: list[str]) -> list[str]:
    """Классы врагов → как их произносить, со схлопыванием дублей.

    «рога и рога» звучало как сбой синтезатора и, главное, ничего не сообщало:
    игрок и так видит двоих. «Дабл рога» — то, как этот состав называют сами
    игроки, и это сразу задаёт режим боя.
    """
    counts: dict[str, int] = {}
    order: list[str] = []
    for cls in enemy_classes:
        if not cls:
            continue
        name = _class_ru(cls)
        if name not in counts:
            order.append(name)
        counts[name] = counts.get(name, 0) + 1
    out: list[str] = []
    for name in order:
        n = counts[name]
        prefix = _MULTIPLIER_RU.get(n)
        out.append(f"{prefix} {name}" if prefix else name)
    return out


def arena_start_phrase(enemy_classes: list[str], kill_target: str | None) -> str:
    """'Арена. Против вар и дру. Килл таргет — дру.'

    3v3 — через запятую («вар, прист и рога»), чтобы фраза оставалась короткой.
    Дубли схлопываются в «дабл рога» (Phase 4.14).
    """
    names = _enemy_names(enemy_classes)
    enemies = ", ".join(names[:-1]) + f" и {names[-1]}" if len(names) > 1 else "".join(names)
    parts = ["Арена."]
    if enemies:
        parts.append(f"Против {enemies}.")
    if kill_target:
        parts.append(f"Килл таргет — {_target_ru(kill_target)}.")
    return " ".join(parts)


def stealth_opener_phrase() -> str:
    """'Арена. Никого не видно — стелс опенер. Кучкуйтесь.'"""
    return "Арена. Никого не видно — стелс опенер. Кучкуйтесь."


def arena_delta_phrase(new_classes: list[str], kill_target: str | None) -> str:
    """'Плюс рога. Килл таргет — прист.' — доуточнение уже озвученного состава.

    Аддон переотправляет ARENA_START, когда состав дорисовывается (враг вышел из
    стелса, поздний зум). Полная стартовая фраза во второй раз звучит как заевшая
    пластинка, поэтому во второй и последующие разы озвучиваем только дельту.
    """
    names = [_class_ru(c) for c in new_classes if c]
    parts: list[str] = []
    if names:
        parts.append(f"Плюс {' и '.join(names)}.")
    if kill_target:
        parts.append(f"Килл таргет — {_target_ru(kill_target)}.")
    return " ".join(parts) or "Состав уточнён."


def trinket_phrase(source: str) -> str:
    """'Тринкет у Секрадж!' — легаси-анонс факта.

    С Phase 4.10 голос озвучивает РЕАКЦИЮ (`orchestrator.reactions`), а не факт;
    функция оставлена для совместимости и тестов.
    """
    return f"Тринкет у {source}!" if source else "Тринкет врага!"


def ability_phrase(source: str, spell_key: str) -> str:
    """'Айсблок у Фрости!' — легаси-анонс факта (см. `trinket_phrase`)."""
    name = _SPELL_RU.get(spell_key, spell_key.replace("_", " "))
    capitalized = name[:1].upper() + name[1:]
    return f"{capitalized} у {source}!" if source else f"{capitalized}!"
