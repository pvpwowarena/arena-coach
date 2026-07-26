"""Предупреждения по врагам (Phase 4.7): короткие тактические угрозы по классам.

Работают для ЛЮБОГО сетапа, даже если матчапа НЕТ в KB (нестандартные комбо
вроде mage+mage+mage): угрозы строятся из классов/спеков врагов, а не из
KB-документа. Показываются на ARENA_START в DM и озвучиваются короткой фразой.

Стиль — как игрок кричит тиммейту: «осторожно, тотемы огня, не лезь в мили».

Модуль чистый (без сети/discord/LLM), детерминированный, покрыт юнит-тестами.
Приоритет спека над классом: если спек известен (bridge раскрыл по сигнатурному
спеллу), берём более точную формулировку.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class Threat:
    """Одна угроза: подробная строка для текста + короткая для голоса."""

    dm: str  # для текстового DM — можно с деталями
    voice: str  # ≤ ~5 слов, для TTS


# Класс врага (UPPERCASE, как шлёт bridge) → угроза.
_CLASS_THREAT: dict[str, Threat] = {
    "SHAMAN": Threat(
        "тотемы огня (searing/fire nova) — не стой в мили; grounding съедает каст, tremor снимает страх/сон",
        "тотемы огня, не лезь в мили",
    ),
    "WARLOCK": Threat(
        "фел (Spell Lock/Devour снимает овцу и нову), fear + death coil — трапни собаку, рвись из LoS",
        "лок с фелом и страхом",
    ),
    "MAGE": Threat(
        "овца + шаттер (nova→добив), айсблок, бли́нк — ломай нову, дизармни/добей до блока",
        "маг: овца и шаттер",
    ),
    "ROGUE": Threat(
        "стелс-опен, kidney/blind, клок+ваниш — держи трап/нову на реопен, тринкет под первый стан",
        "рога: стелс и стан-лок",
    ),
    "HUNTER": Threat(
        "трапы и scatter, deterrence, петовый спелл-лок — не стой в один сектор, ломай каст",
        "хант: трапы и скаттер",
    ),
    "PRIEST": Threat(
        "fear, mana burn, дисперс + щит — дизармни страх, дави сквозь щит",
        "прист: страх и щит",
    ),
    "PALADIN": Threat(
        "бабл (divine shield) и freedom сбрасывают контроль; под баблом не killable — жди/дизармни/mana burn",
        "пала: бабл и фридом",
    ),
    "DRUID": Threat(
        "циклон рвёт добив, кайт travel/HoT, тринкет+NS — свяжи druid'а перед killom",
        "дру: циклон и кайт",
    ),
    "WARRIOR": Threat(
        "чардж/интерцепт, hamstring, retaliation, mortal strike режет хил — кайти, снимай раны",
        "вар: чардж и раны",
    ),
}

# Спек-уточнения (перекрывают класс, если спек раскрыт мостом).
_SPEC_THREAT: dict[str, Threat] = {
    "resto-shaman": Threat(
        "grounding/tremor/earthshock, тотемы огня — не стой в мили, ломай хил-каст",
        "рсшам: тотемы, ломай хил",
    ),
    "ele-shaman": Threat(
        "бурст молний + grounding, tremor — интеррапти каст, не стой в LoS",
        "элешам: бурст и граунд",
    ),
    "resto-druid": Threat(
        "циклон рвёт добив, кайт travel/HoT, тринкет+NS — свяжи druid'а перед killom",
        "рдру: циклон, свяжи",
    ),
    "feral-druid": Threat(
        "bleed + bash + ravage, стан-лок — не подставляй спину, снимай кровотечения",
        "ферал: станы и бли́ды",
    ),
    "holy-paladin": Threat(
        "бесконечный хил + бабл/freedom; под баблом не killable — mana burn/дизарм/дави в притеснение",
        "хпал: бабл, дави в мана",
    ),
    "ret-paladin": Threat(
        "бурст (репентанс, HoJ, wings), freedom — не стой под wings, кайти бурст",
        "ретри: бурст под крыльями",
    ),
    "shadow-priest": Threat(
        "fear + silence, вампиризм-хил, дисперс — трейни через щит, дизармни страх",
        "сприст: страх и сайленс",
    ),
    "fire-mage": Threat(
        "PoM-Pyro бурст, комбусшн — прячься за LoS на PoM, ломай каст",
        "файр: помпиро бурст",
    ),
    "frost-mage": Threat(
        "овца + шаттер, айсблок, water elemental nova — ломай нову, дизармни до блока",
        "фрост: шаттер и блок",
    ),
    "arms-warrior": Threat(
        "mortal strike режет хил вдвое, чардж/свип — кайти, снимай раны, не хилься под MS",
        "армс: MS режет хил",
    ),
}

# Комбо-угрозы: специфические опасные пары (ключ — отсортированные классы).
# Показываются ПЕРВОЙ строкой поверх классовых угроз.
_COMBO_THREAT: dict[tuple[str, ...], Threat] = {
    ("MAGE", "MAGE"): Threat(
        "двойной шаттер — не группируйся, держи нову/диспелл, рвись из nova-сетапа",
        "двойной шаттер, не группируйся",
    ),
    ("ROGUE", "ROGUE"): Threat(
        "двойной стелс-опен и стан-лок — трап/AoE на реопен, тринкет под первый kidney",
        "два стелса, тринкет под стан",
    ),
    ("PALADIN", "WARRIOR"): Threat(
        "MS + бабл: под баблом варра не сдержать — киль варра до бабла или mana burn палу",
        "MS и бабл, киль до бабла",
    ),
}


def _norm_classes(classes: Sequence[str]) -> list[str]:
    return [c.strip().upper() for c in classes if c and c.strip()]


def _spec_key(spec: str | None) -> str | None:
    if not spec:
        return None
    s = spec.strip().lower()
    return s or None


def threat_for(wow_class: str, spec: str | None = None) -> Threat | None:
    """Угроза для одного врага: спек приоритетнее класса."""
    sk = _spec_key(spec)
    if sk and sk in _SPEC_THREAT:
        return _SPEC_THREAT[sk]
    return _CLASS_THREAT.get(wow_class.strip().upper())


def _combo(classes: list[str]) -> Threat | None:
    key = tuple(sorted(classes))
    if key in _COMBO_THREAT:
        return _COMBO_THREAT[key]
    # Пара внутри 3v3: ищем любую известную комбо-пару среди классов.
    uniq = sorted(set(classes))
    for i in range(len(uniq)):
        for j in range(i + 1, len(uniq)):
            pair = (uniq[i], uniq[j])
            if pair in _COMBO_THREAT:
                return _COMBO_THREAT[pair]
    # Дубль одного класса (mage+mage в 3v3 с третьим).
    for c in set(classes):
        if classes.count(c) >= 2 and (c, c) in _COMBO_THREAT:
            return _COMBO_THREAT[(c, c)]
    return None


def threat_lines(
    enemy_classes: Sequence[str],
    enemy_specs: Sequence[str | None] | None = None,
) -> list[str]:
    """Список строк-предупреждений для DM (комбо первым, затем по врагам, без дублей).

    Args:
        enemy_classes: классы врагов (UPPERCASE), напр. ["SHAMAN", "WARRIOR"].
        enemy_specs: спеки в том же порядке (None где неизвестно). Может быть None.

    Returns:
        Список коротких предупреждений (может быть пустым, если классы неизвестны).
    """
    classes = _norm_classes(enemy_classes)
    specs = list(enemy_specs) if enemy_specs is not None else [None] * len(classes)
    # выравниваем длину
    if len(specs) < len(classes):
        specs = specs + [None] * (len(classes) - len(specs))

    lines: list[str] = []
    seen: set[str] = set()

    combo = _combo(classes)
    if combo is not None and combo.dm not in seen:
        lines.append(f"⚠️ {combo.dm}")
        seen.add(combo.dm)

    for cls, spec in zip(classes, specs, strict=False):
        t = threat_for(cls, spec)
        if t is None or t.dm in seen:
            continue
        seen.add(t.dm)
        lines.append(f"• {t.dm}")
    return lines


def threat_voice(
    enemy_classes: Sequence[str],
    enemy_specs: Sequence[str | None] | None = None,
    limit: int = 2,
) -> str | None:
    """Короткая голосовая сводка угроз: «Осторожно: тотемы огня, лок с фелом».

    Берём до `limit` самых характерных (комбо приоритетно), чтобы фраза
    оставалась ≤ ~8 слов. None — если угроз нет.
    """
    classes = _norm_classes(enemy_classes)
    specs = list(enemy_specs) if enemy_specs is not None else [None] * len(classes)
    if len(specs) < len(classes):
        specs = specs + [None] * (len(classes) - len(specs))

    picks: list[str] = []
    seen: set[str] = set()

    combo = _combo(classes)
    if combo is not None:
        picks.append(combo.voice)
        seen.add(combo.voice)

    for cls, spec in zip(classes, specs, strict=False):
        if len(picks) >= limit:
            break
        t = threat_for(cls, spec)
        if t is None or t.voice in seen:
            continue
        seen.add(t.voice)
        picks.append(t.voice)

    if not picks:
        return None
    return "Осторожно: " + ", ".join(picks[:limit]) + "."


__all__ = ["Threat", "threat_for", "threat_lines", "threat_voice"]
