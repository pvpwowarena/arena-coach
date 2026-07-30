"""Состояние врагов в матче: реестр кулдаунов + карта «ник → класс» (Phase 4.14).

## Зачем это появилось

Аудит 30.07.2026 (`docs/audit-2026-07-30-value.md`): бот озвучивал то, что игрок и
так видит («Овца — ломай уроном»), и не озвучивал то, чего игрок видеть НЕ может.
Ценность подсказки = (информация, недоступная глазом) × (успела до решения).

В расшифровке живых комментариев R1-игроков (Aphane/Jino, RM 2v2) самая частая
реплика — «he has no trinket», повторённая трижды: на ней строится решение боя.
Именно этого класса подсказок в системе не было вовсе, хотя все данные уже
доезжают до бэкенда: мост форвардит каждый каст врага с именем источника.

## Что модуль умеет

1. **Реестр КД.** Враг использовал способность с известным кулдауном → мы знаем,
   когда она вернётся, и знаем, что до тех пор её НЕТ. Обратный отсчёт берётся из
   данных (`kb/glossary/realtime_spells.json:cooldown_s`, выведено из
   sourced-слоя `abilities.json`). Где кулдаун не подтверждён источником —
   храним только факт «потрачено», без выдуманных секунд (тот же принцип, что
   `GLOSSARY_GAPS` в `reactions`).

2. **Карта «ник → класс».** Ростер в `ARENA_START` несёт только классы (имён в
   `EnemyInfo` нет), но каждый каст несёт и ник, и — через каталог спеллов —
   класс кастера. То есть бэкенд может построить карту сам, без релиза моста.
   Это ключ к разрешению **дублей классов**: «бей рогу» неоднозначно, когда рог
   двое, а «бей ту, что без тринкета» — однозначно.

3. **Производные состояния** (то, ради чего всё): «окно» — у врага потрачен и
   тринкет, и защитный КД, значит его можно дожимать; «КД вернулся» — момент,
   когда окно закрылось. Оба состояния меняются БЕЗ нового события от врага,
   поэтому детектор рёберный (`poll_*`): один раз на переход, а не на каждый тик.

Состояние живёт в памяти по `player_name` (как `MatchRecorder`): матч короткий,
переживать рестарт незачем. Часы инъектируются — тесты не спят.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field

log = logging.getLogger(__name__)

#: Ключ события тринкета (`TRINKET_IDS` моста шлёт три варианта — все они «тринкет»).
TRINKET_KEYS = frozenset({"pvp_trinket", "every_man", "wotf"})

#: Канонический ключ, под которым тринкет лежит в реестре независимо от варианта.
TRINKET = "trinket"

#: Категории каталога, которые считаются «защитой» для расчёта окна.
DEFENSIVE_CATEGORIES = frozenset({"defensive", "immunity", "reset"})

#: Сколько держим состояние матча без событий (страховка от утечки при потере ARENA_END).
MATCH_TTL_S = 2 * 3600.0

#: Максимум одновременно открытых матчей (как у MatchRecorder).
MAX_OPEN_MATCHES = 32


@dataclass
class EnemyRecord:
    """Один враг матча: ник, класс (если раскрылся) и его кулдауны."""

    name: str
    wow_class: str = ""
    #: `spell_key → момент готовности`. `None` = кулдаун не подтверждён источником,
    #: знаем только «потрачено» (секунды не выдумываем).
    ready_at: dict[str, float | None] = field(default_factory=dict)
    #: Длина кулдауна (нужна, чтобы не объявлять возврат мелких КД вроде кика).
    cd_len: dict[str, float] = field(default_factory=dict)
    #: Что считается защитой — нужно для расчёта «окна» (заполняется из каталога).
    defensives_spent: set[str] = field(default_factory=set)

    def note(self, key: str, cooldown_s: float | None, now: float) -> None:
        self.ready_at[key] = (now + cooldown_s) if cooldown_s else None
        if cooldown_s:
            self.cd_len[key] = float(cooldown_s)

    def is_spent(self, key: str, now: float) -> bool:
        """Способность потрачена и ещё не вернулась."""
        if key not in self.ready_at:
            return False
        ready = self.ready_at[key]
        return True if ready is None else now < ready

    def remaining_s(self, key: str, now: float) -> float | None:
        """Сколько секунд до возврата. `None` — кулдаун неизвестен."""
        ready = self.ready_at.get(key)
        if ready is None:
            return None
        return max(0.0, ready - now)


@dataclass
class _MatchState:
    session_id: str
    started_at: float
    touched_at: float
    enemies: dict[str, EnemyRecord] = field(default_factory=dict)
    #: Про какие «окна» уже сказали (ник) — чтобы не повторять каждое событие.
    announced_windows: set[str] = field(default_factory=set)
    #: Про какие возвраты КД уже сказали (`ник|ключ`).
    announced_returns: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class ReadyAgain:
    """Кулдаун врага вернулся — окно закрылось."""

    enemy: str
    key: str
    #: Длина кулдауна — по ней решаем, стоит ли объявлять возврат (кик каждые 24с — шум).
    cooldown_s: float = 0.0


@dataclass(frozen=True)
class OpenWindow:
    """У врага потрачены и тринкет, и защита — его можно дожимать."""

    enemy: str
    wow_class: str
    spent: tuple[str, ...]


class EnemyTracker:
    """Состояние врагов по игроку. Иммутабельных гарантий нет — это живой матч."""

    def __init__(
        self,
        clock: Callable[[], float] | None = None,
        ttl_s: float = MATCH_TTL_S,
        max_matches: int = MAX_OPEN_MATCHES,
    ) -> None:
        self._clock = clock
        self._ttl_s = ttl_s
        self._max = max_matches
        self._matches: dict[str, _MatchState] = {}

    # ── жизненный цикл матча ────────────────────────────────────────────

    def start(self, player_name: str, session_id: str, now: float | None = None) -> None:
        """Начать матч. Повторный `ARENA_START` (доуточнение состава) состояние НЕ сбрасывает."""
        key = self._pkey(player_name)
        t = self._now(now)
        existing = self._matches.get(key)
        if existing is not None and existing.session_id == session_id:
            existing.touched_at = t
            return
        self._evict(t)
        self._matches[key] = _MatchState(session_id=session_id, started_at=t, touched_at=t)

    def end(self, player_name: str) -> None:
        self._matches.pop(self._pkey(player_name), None)

    # ── запись событий ──────────────────────────────────────────────────

    def note(
        self,
        player_name: str,
        enemy: str,
        key: str,
        wow_class: str = "",
        cooldown_s: float | None = None,
        category: str = "",
        now: float | None = None,
    ) -> None:
        """Враг применил способность. `cooldown_s=None` → пишем только «потрачено»."""
        state = self._matches.get(self._pkey(player_name))
        if state is None or not enemy or not key:
            return
        t = self._now(now)
        state.touched_at = t
        rec = state.enemies.get(enemy.lower())
        if rec is None:
            rec = EnemyRecord(name=enemy, wow_class=wow_class.upper())
            state.enemies[enemy.lower()] = rec
        elif wow_class and not rec.wow_class:
            # Класс раскрывается первым же сигнатурным кастом — дальше не перетираем.
            rec.wow_class = wow_class.upper()
        rec.note(key, cooldown_s, t)
        if category in DEFENSIVE_CATEGORIES:
            rec.defensives_spent.add(key)

    def note_trinket(
        self,
        player_name: str,
        enemy: str,
        cooldown_s: float | None = None,
        now: float | None = None,
    ) -> None:
        """Враг тринкетнул. Кулдаун тринкета в sourced-слое не подтверждён →
        по умолчанию храним факт без секунд (см. модульный docstring)."""
        self.note(player_name, enemy, TRINKET, cooldown_s=cooldown_s, now=now)

    # ── запросы ─────────────────────────────────────────────────────────

    def known(self, player_name: str) -> list[EnemyRecord]:
        state = self._matches.get(self._pkey(player_name))
        return list(state.enemies.values()) if state else []

    def duplicated_classes(self, player_name: str) -> set[str]:
        """Классы, которые среди РАСКРЫТЫХ врагов встречаются больше одного раза."""
        seen: dict[str, int] = {}
        for rec in self.known(player_name):
            if rec.wow_class:
                seen[rec.wow_class] = seen.get(rec.wow_class, 0) + 1
        return {cls for cls, n in seen.items() if n > 1}

    def needs_name(self, player_name: str, enemy: str) -> bool:
        """True — этого врага без имени не отличить (его класс продублирован)."""
        rec = self._find(player_name, enemy)
        if rec is None or not rec.wow_class:
            return False
        return rec.wow_class in self.duplicated_classes(player_name)

    def names_of_class(self, player_name: str, wow_class: str) -> list[str]:
        cls = (wow_class or "").upper()
        return [rec.name for rec in self.known(player_name) if rec.wow_class == cls]

    def without_trinket(
        self, player_name: str, wow_class: str = "", now: float | None = None
    ) -> list[str]:
        """Ники врагов, у которых тринкет потрачен и не вернулся."""
        t = self._now(now)
        cls = (wow_class or "").upper()
        return [
            rec.name
            for rec in self.known(player_name)
            if (not cls or rec.wow_class == cls) and rec.is_spent(TRINKET, t)
        ]

    def remaining_s(
        self, player_name: str, enemy: str, key: str, now: float | None = None
    ) -> float | None:
        rec = self._find(player_name, enemy)
        return rec.remaining_s(key, self._now(now)) if rec is not None else None

    # ── производные состояния (рёберные детекторы) ──────────────────────

    def poll_ready_again(self, player_name: str, now: float | None = None) -> list[ReadyAgain]:
        """Кулдауны, которые вернулись с прошлой проверки. Каждый — один раз."""
        state = self._matches.get(self._pkey(player_name))
        if state is None:
            return []
        t = self._now(now)
        out: list[ReadyAgain] = []
        for rec in state.enemies.values():
            for key, ready in rec.ready_at.items():
                if ready is None or t < ready:
                    continue
                mark = f"{rec.name.lower()}|{key}"
                if mark in state.announced_returns:
                    continue
                state.announced_returns.add(mark)
                out.append(ReadyAgain(enemy=rec.name, key=key, cooldown_s=rec.cd_len.get(key, 0.0)))
        return out

    def poll_open_window(self, player_name: str, now: float | None = None) -> OpenWindow | None:
        """Первый враг, у которого потрачены и тринкет, и защитный КД.

        Это и есть «вау»-момент: игрок не может знать, что у противника не
        осталось ни тринкета, ни дефа. Про каждого врага говорим один раз за матч.
        """
        state = self._matches.get(self._pkey(player_name))
        if state is None:
            return None
        t = self._now(now)
        for rec in state.enemies.values():
            if rec.name.lower() in state.announced_windows:
                continue
            if not rec.is_spent(TRINKET, t):
                continue
            defs_spent = tuple(k for k in sorted(rec.defensives_spent) if rec.is_spent(k, t))
            if not defs_spent:
                continue
            state.announced_windows.add(rec.name.lower())
            return OpenWindow(enemy=rec.name, wow_class=rec.wow_class, spent=(TRINKET, *defs_spent))
        return None

    # ── внутреннее ──────────────────────────────────────────────────────

    def _find(self, player_name: str, enemy: str) -> EnemyRecord | None:
        state = self._matches.get(self._pkey(player_name))
        return state.enemies.get(enemy.lower()) if state else None

    def _now(self, now: float | None) -> float:
        if now is not None:
            return now
        if self._clock is not None:
            return self._clock()
        import time

        return time.monotonic()

    @staticmethod
    def _pkey(player_name: str) -> str:
        return player_name.lower()

    def _evict(self, now: float) -> None:
        stale = [k for k, v in self._matches.items() if now - v.touched_at > self._ttl_s]
        for k in stale:
            self._matches.pop(k, None)
        while len(self._matches) >= self._max:
            oldest = min(self._matches, key=lambda k: self._matches[k].touched_at)
            self._matches.pop(oldest, None)
            log.debug("EnemyTracker: вытеснен старый матч %s", oldest)
