"""Нормализация raw addon-событий в canonical schema для backend.

Формат AC-сообщений из Tracker.lua:
  [AC|ARENA_START|2v2|ROGUE/HUMAN,MAGE/GNOME]
  [AC|TRINKET|EnemyName|42292|pvp_trinket]
  [AC|ABILITY|EnemyName|33786|cyclone]
  [AC|ARENA_END|42]

Нормализатор парсит поля → pydantic-модели → JSON envelope для backend.

Envelope schema (v1):
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
    "enemies": [{"class": "ROGUE", "race": "HUMAN"}, ...],
    "matchup_slug_hint": "rogue-mage-vs-warrior-druid"  # или null
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
    """Трекер текущей арена-сессии в рамках bridge-процесса."""

    def __init__(self) -> None:
        self._session_id: str = ""
        self._match: MatchInfo = MatchInfo()

    def start_session(self, event: ArenaStartEvent) -> None:
        self._session_id = str(uuid.uuid4())
        self._match = MatchInfo(
            bracket=event.bracket,
            enemies=event.enemies,
            matchup_slug_hint=_build_slug_hint(event.enemies),
        )
        log.info(
            "Сессия начата %s: %s, matchup=%s",
            self._session_id,
            event.bracket,
            self._match.matchup_slug_hint,
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
    Backend сопоставляет с KB-документами по composition поля.
    """
    if not enemies:
        return None
    classes = sorted(e.wow_class.lower() for e in enemies)
    return "-".join(classes)


# ── Парсер AC-строк → pydantic событий ──────────────────────────────────────


def parse_event(raw: str) -> AnyEvent | None:
    """Разобрать payload [AC|...] в typed event.

    Args:
        raw: payload без обрамляющих [AC| и ] — например «TRINKET|EnemyName|42292|pvp_trinket»

    Returns:
        Typed event или None при ошибке парсинга.
    """
    parts = parse_ac_line(raw)
    if not parts:
        return None

    event_type = parts[0].upper()

    try:
        if event_type == "ARENA_START":
            # [ARENA_START|2v2|ROGUE/HUMAN,MAGE/GNOME]
            bracket = parts[1] if len(parts) > 1 else "unknown"
            enemy_str = parts[2] if len(parts) > 2 else ""
            enemies: list[EnemyInfo] = []
            if enemy_str:
                for e in enemy_str.split(","):
                    e = e.strip()
                    if e:
                        enemies.append(EnemyInfo.from_str(e))
            return ArenaStartEvent(bracket=bracket, enemies=enemies)

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
