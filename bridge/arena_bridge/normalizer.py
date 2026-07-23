"""Нормализация raw addon-событий в canonical schema для backend.

Формат AC-сообщений из Tracker.lua (addon >= 0.2.0 шлёт и союзников;
разделитель «#» с addon 0.2.1 — «|» запрещён клиентом в SendChatMessage,
легаси «|»-формат по-прежнему принимается, см. chat_tail._AC_RE):
  [AC#ARENA_START#2v2#WARRIOR/ORC,PALADIN/BLOODELF#ROGUE/HUMAN,MAGE/GNOME]
  [AC#ARENA_START#2v2#WARRIOR/ORC,PALADIN/BLOODELF]      # addon 0.1.x — без союзников
  [AC#TRINKET#EnemyName#42292#pvp_trinket]
  [AC#ABILITY#EnemyName#33786#cyclone]
  [AC#ARENA_END#42]

В allies игрок ВСЕГДА первый — backend таргетирует советы под его класс.

Нормализатор парсит поля → pydantic-модели → JSON envelope для backend.

Envelope schema (v1, additive-совместимо расширен в Phase 4.1):
{
  "schema_version": 1,
  "bridge_ts": "2026-05-14T12:34:56Z",
  "session_id": "<uuid>",          # генерируется bridge при ARENA_START
  "player_name": "<wow_name>",      # из конфига bridge
  "event": {
    "type": "TRINKET" | "ABILITY" | "ARENA_START" | "ARENA_END",
    ...type-specific fields...
  },
  "match": {
    "bracket": "2v2" | "3v3",
    "enemies": [{"wow_class": "ROGUE", "race": "HUMAN"}, ...],
    "allies":  [{"wow_class": "ROGUE", "race": "HUMAN"}, ...],   # игрок первый
    "our_comp_hint": "mage+rogue",       # из allies или $BRIDGE_OUR_COMP
    "player_class": "ROGUE",             # класс игрока (allies[0])
    "matchup_slug_hint": "mage-rogue"    # классы врагов, sorted; или null
  }
}
"""

from __future__ import annotations

import logging
import uuid
from typing import Literal

from pydantic import BaseModel, Field

from .chat_tail import get_bridge_timestamp, parse_ac_line

log = logging.getLogger(__name__)


# ── Pydantic event-модели ────────────────────────────────────────────────────


class EnemyInfo(BaseModel):
    """Один враг: класс + раса."""

    wow_class: str
    race: str

    @classmethod
    def from_str(cls, s: str) -> EnemyInfo:
        """Парсит 'ROGUE/HUMAN' → EnemyInfo(wow_class='ROGUE', race='HUMAN')."""
        parts = s.split("/", 1)
        return cls(
            wow_class=parts[0].strip().upper() if parts else "UNKNOWN",
            race=parts[1].strip().upper() if len(parts) > 1 else "UNKNOWN",
        )


class ArenaStartEvent(BaseModel):
    type: Literal["ARENA_START"] = "ARENA_START"
    bracket: str
    enemies: list[EnemyInfo]
    allies: list[EnemyInfo] = Field(default_factory=list)  # игрок первый (addon >= 0.2.0)


class TrinketEvent(BaseModel):
    type: Literal["TRINKET"] = "TRINKET"
    source_name: str
    spell_id: int
    trinket_key: str


class AbilityEvent(BaseModel):
    type: Literal["ABILITY"] = "ABILITY"
    source_name: str
    spell_id: int
    spell_key: str


class ArenaEndEvent(BaseModel):
    type: Literal["ARENA_END"] = "ARENA_END"
    event_count: int


AnyEvent = ArenaStartEvent | TrinketEvent | AbilityEvent | ArenaEndEvent


class MatchInfo(BaseModel):
    """Данные о текущем матче — обновляются при ARENA_START."""

    bracket: str = "unknown"
    enemies: list[EnemyInfo] = Field(default_factory=list)
    allies: list[EnemyInfo] = Field(default_factory=list)
    our_comp_hint: str | None = None
    player_class: str | None = None
    matchup_slug_hint: str | None = None


class CanonicalEnvelope(BaseModel):
    """Полный envelope, который bridge отправляет на backend."""

    schema_version: int = 1
    bridge_ts: str
    session_id: str
    player_name: str
    event: AnyEvent
    match: MatchInfo


# ── Состояние текущей сессии ─────────────────────────────────────────────────


class SessionState:
    """Трекер текущей арена-сессии в рамках bridge-процесса.

    Args:
        default_our_comp: fallback-состав из $BRIDGE_OUR_COMP (напр. "rogue+mage")
            на случай, если аддон старый и не шлёт союзников.
    """

    def __init__(self, default_our_comp: str | None = None) -> None:
        self._session_id: str = ""
        self._match: MatchInfo = MatchInfo()
        self._default_our_comp = default_our_comp or None

    def start_session(self, event: ArenaStartEvent) -> None:
        # Повторный ARENA_START той же сессии (враг вышел из стелса, аддон
        # дослал уточнённый состав) — session_id сохраняем.
        if not self._session_id:
            self._session_id = str(uuid.uuid4())
        our_comp = _build_comp_hint(event.allies) or self._default_our_comp
        player_class = event.allies[0].wow_class if event.allies else None
        self._match = MatchInfo(
            bracket=event.bracket,
            enemies=event.enemies,
            allies=event.allies,
            our_comp_hint=our_comp,
            player_class=player_class,
            matchup_slug_hint=_build_slug_hint(event.enemies),
        )
        log.info(
            "Сессия начата %s: %s, matchup=%s, our_comp=%s, player_class=%s",
            self._session_id,
            event.bracket,
            self._match.matchup_slug_hint,
            our_comp,
            player_class,
        )

    def end_session(self) -> None:
        log.info("Сессия завершена: %s", self._session_id)
        self._session_id = ""
        self._match = MatchInfo()

    @property
    def session_id(self) -> str:
        return self._session_id or str(uuid.uuid4())  # fallback для событий до ARENA_START

    @property
    def match(self) -> MatchInfo:
        return self._match


def _build_slug_hint(enemies: list[EnemyInfo]) -> str | None:
    """Строим matchup_slug_hint из классов врагов в алфавитном порядке.

    Формат: 'mage-rogue' (сортируем, приводим к lowercase).
    Backend сопоставляет с KB-документами по vs-полю (class-level match).
    """
    if not enemies:
        return None
    classes = sorted(e.wow_class.lower() for e in enemies)
    return "-".join(classes)


def _build_comp_hint(allies: list[EnemyInfo]) -> str | None:
    """Наш состав из классов союзников: 'mage+rogue' (sorted, lowercase).

    Совпадает с форматом composition в KB (после нормализации на бэке).
    """
    if not allies:
        return None
    classes = sorted(a.wow_class.lower() for a in allies)
    return "+".join(classes)


# ── Парсер AC-строк → pydantic событий ──────────────────────────────────────


def _parse_units(units_str: str) -> list[EnemyInfo]:
    """'ROGUE/HUMAN,MAGE/GNOME' → [EnemyInfo, ...]. Пустая строка → []."""
    units: list[EnemyInfo] = []
    for u in units_str.split(","):
        u = u.strip()
        if u:
            units.append(EnemyInfo.from_str(u))
    return units


def parse_event(raw: str) -> AnyEvent | None:
    """Разобрать payload [AC#...] в typed event.

    Args:
        raw: payload без обрамляющих [AC# и ] — например «TRINKET#EnemyName#42292#pvp_trinket»
             (легаси-разделитель «|» тоже принимается)

    Returns:
        Typed event или None при ошибке парсинга.
    """
    parts = parse_ac_line(raw)
    if not parts:
        return None

    event_type = parts[0].upper()

    try:
        if event_type == "ARENA_START":
            # [ARENA_START|2v2|WARRIOR/ORC,PALADIN/BLOODELF|ROGUE/HUMAN,MAGE/GNOME]
            # 4-е поле (союзники, игрок первый) — опционально (addon >= 0.2.0)
            bracket = parts[1] if len(parts) > 1 else "unknown"
            enemies = _parse_units(parts[2] if len(parts) > 2 else "")
            allies = _parse_units(parts[3] if len(parts) > 3 else "")
            return ArenaStartEvent(bracket=bracket, enemies=enemies, allies=allies)

        elif event_type == "TRINKET":
            # [TRINKET|EnemyName|42292|pvp_trinket]
            return TrinketEvent(
                source_name=parts[1] if len(parts) > 1 else "",
                spell_id=int(parts[2]) if len(parts) > 2 else 0,
                trinket_key=parts[3] if len(parts) > 3 else "pvp_trinket",
            )

        elif event_type == "ABILITY":
            # [ABILITY|EnemyName|33786|cyclone]
            return AbilityEvent(
                source_name=parts[1] if len(parts) > 1 else "",
                spell_id=int(parts[2]) if len(parts) > 2 else 0,
                spell_key=parts[3] if len(parts) > 3 else "",
            )

        elif event_type == "ARENA_END":
            # [ARENA_END|42]
            return ArenaEndEvent(
                event_count=int(parts[1]) if len(parts) > 1 else 0,
            )

        else:
            log.debug("Неизвестный тип события: %s", event_type)
            return None

    except (ValueError, IndexError) as exc:
        log.warning("Ошибка парсинга события '%s': %s", raw, exc)
        return None


def build_envelope(
    event: AnyEvent,
    session: SessionState,
    player_name: str,
) -> CanonicalEnvelope:
    """Собрать CanonicalEnvelope из события + текущей сессии."""
    return CanonicalEnvelope(
        bridge_ts=get_bridge_timestamp(),
        session_id=session.session_id,
        player_name=player_name,
        event=event,
        match=session.match,
    )


def normalize_raw(
    raw: str,
    session: SessionState,
    player_name: str,
) -> CanonicalEnvelope | None:
    """Полный pipeline: raw AC-string → CanonicalEnvelope или None.

    Также обновляет SessionState при ARENA_START / ARENA_END.
    """
    event = parse_event(raw)
    if event is None:
        return None

    # Обновляем состояние сессии
    if isinstance(event, ArenaStartEvent):
        session.start_session(event)
    elif isinstance(event, ArenaEndEvent):
        session.end_session()

    return build_envelope(event, session, player_name)
