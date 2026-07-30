"""Подсказки по СОСТОЯНИЮ врага, а не по факту события (Phase 4.14).

`reactions.py` — статическая таблица «способность → что делать». Она ничего не
знает о ситуации, поэтому её реплики в лучшем случае пересказывают видимое
(«Овца — ломай уроном»). Здесь — второй тир: фразы, которые опираются на
`EnemyTracker` и потому сообщают то, чего на экране НЕТ:

* **Окно** — у врага потрачены и тринкет, и защитный кулдаун. Это главный
  «вау»-момент: сам игрок такой учёт в бою не ведёт.
* **Возврат КД** — окно закрылось, тринкет/ваниш снова есть.
* **Разрешение дублей** — «бей ту рогу, что без тринкета» вместо неоднозначного
  «бей рогу». Ровно то, чего не хватало по фидбэку 30.07: при двух одинаковых
  классах class-level килл-таргет не указывает ни на кого.

Тир — advice (как `reactions` и офлайн-сиды): цифры берём только там, где они
подтверждены sourced-слоем, иначе говорим без секунд.
"""

from __future__ import annotations

from dataclasses import dataclass

from arena_coach.orchestrator.enemy_state import TRINKET, OpenWindow, ReadyAgain
from arena_coach.orchestrator.reactions import HIGH, NORMAL
from arena_coach.orchestrator.voice_phrases import class_ru, spell_ru

#: Возврат кулдауна объявляем только для тяжёлых КД. Кик откатывается каждые 24с —
#: объявлять его возврат означало бы вернуть ту самую «заевшую пластинку».
MIN_RETURN_CD_S = 60.0


@dataclass(frozen=True)
class StateHint:
    """Подсказка по состоянию: та же форма, что у `Reaction`, плюс ключ троттлинга."""

    voice: str
    dm: str
    throttle_key: str
    priority: str = HIGH
    repeat_s: float = 120.0


def _ability_ru(key: str) -> str:
    """Человеческое имя способности для фразы; тринкет — отдельный случай."""
    return "тринкет" if key == TRINKET else spell_ru(key)


def window_hint(window: OpenWindow) -> StateHint:
    """«У Секраджа ни тринкета, ни дефа — дожимайте.»

    Формулировка намеренно императивная и без цифр: важен не остаток секунд, а то,
    что окно открыто ПРЯМО СЕЙЧАС.
    """
    spent_ru = ", ".join(_ability_ru(k) for k in window.spent)
    who = window.enemy
    cls = f" ({class_ru(window.wow_class)})" if window.wow_class else ""
    return StateHint(
        voice=f"У {who} ни тринкета, ни дефа — дожимайте.",
        dm=(
            f"🎯 **Окно на {who}**{cls} — потрачено: {spent_ru}. "
            "Защиты и тринкета нет: вкладывайте бурст и контроль сейчас, "
            "второго такого окна за матч может не быть."
        ),
        throttle_key=f"window:{who.lower()}",
        priority=HIGH,
        repeat_s=300.0,
    )


def ready_again_hint(event: ReadyAgain) -> StateHint | None:
    """«У Секраджа снова есть ваниш.» None — кулдаун слишком мелкий, чтобы говорить."""
    if event.cooldown_s < MIN_RETURN_CD_S:
        return None
    name = _ability_ru(event.key)
    return StateHint(
        voice=f"У {event.enemy} снова есть {name}.",
        dm=(
            f"⏱ **{name.capitalize()} у {event.enemy} откатился** — окно закрылось, "
            "рассчитывай размен заново."
        ),
        throttle_key=f"back:{event.enemy.lower()}:{event.key}",
        priority=NORMAL,
        repeat_s=event.cooldown_s,
    )


def trinket_voice(enemy: str, duplicated: bool) -> str | None:
    """Голос для события тринкета, когда имя врага решает дело.

    Возвращает None, если имя не нужно: тогда работает статическая реплика из
    `reactions.TRINKET_REACTION`. Имя добавляем только при дублях классов —
    в остальных случаях ник в голосе только удлиняет фразу (TTS их и так ломает).
    """
    if not duplicated or not enemy:
        return None
    return f"Тринкета нет у {enemy} — всё на него."


def kill_target_voice(
    wow_class: str,
    candidates: list[str],
    without_trinket: list[str],
) -> str | None:
    """Голос килл-таргета, когда у врагов ДУБЛЬ класса.

    Три случая:
      * ровно один из дублей без тринкета → называем его: выбор объективен;
      * никто/все без тринкета → называем КРИТЕРИЙ, а не ник: ник без причины
        игрок всё равно не запомнит, а критерий работает весь бой;
      * дубля нет → None, отвечает обычная class-level фраза.
    """
    if len(candidates) < 2:
        return None
    exposed = [n for n in without_trinket if n in candidates]
    cls = class_ru(wow_class)
    if len(exposed) == 1:
        return f"Килл таргет — {exposed[0]}, тринкета нет."
    return f"Две {cls} — бей ту, что без тринкета."


def kill_target_dm(
    wow_class: str,
    candidates: list[str],
    without_trinket: list[str],
) -> str | None:
    """Строка в DM с разбором дубля: кто есть и по какому признаку выбирать."""
    if len(candidates) < 2:
        return None
    exposed = [n for n in without_trinket if n in candidates]
    cls = class_ru(wow_class)
    roster = ", ".join(candidates)
    if len(exposed) == 1:
        return (
            f"🎯 Дубль {cls} ({roster}): бей **{exposed[0]}** — тринкет он уже потратил, "
            "контроль на нём держится полную длительность."
        )
    return (
        f"🎯 Дубль {cls} ({roster}): class-level цель неоднозначна. "
        "Держи на прицеле того, кто первым потратит тринкет — я назову ник."
    )
