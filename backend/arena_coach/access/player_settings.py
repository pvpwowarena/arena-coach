"""Per-player настройки коуча: режим голоса (4.5) и боевой текст (4.15).

Общая точка для двух процессов:
  • bot-процесс пишет через `/coach voice on|off|only` и `/coach text on|off`;
  • api-процесс (pipeline) читает перед отправкой hint'а.
Оба смотрят в один SQLite (coach.db).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from arena_coach.access.models import PlayerSettings

log = logging.getLogger(__name__)

#: Валидные режимы: on = текст + голос, off = только текст, only = только голос.
VOICE_MODES = ("on", "off", "only")
DEFAULT_VOICE_MODE = "on"

#: Боевой DM (TRINKET/ABILITY/состояние). Разбор на воротах и постматч — всегда.
#: Default `off` (Phase 4.15): «огромный текст в бою читать не очень удобно» —
#: игрок его не читает, а каждый DM это вызов Discord API и риск rate-limit.
COMBAT_TEXT_MODES = ("on", "off")
DEFAULT_COMBAT_TEXT = "off"


class PlayerSettingsService:
    """CRUD-минимум вокруг таблицы player_settings.

    **Чтение настроек НИКОГДА не должно ронять приём событий** (Phase 4.16). Урок
    оплачен продом 30.07: миграция 0005 не доехала до боевой БД, `SELECT` упал на
    `no such column: combat_text`, и каждый `POST /v1/events` стал 500 — то есть
    НЕОБЯЗАТЕЛЬНАЯ пользовательская настройка выключила весь коучинг в бою.

    Поэтому геттеры глушат любую ошибку БД и отдают дефолт: схема разъехалась,
    SQLite залочен, диск переполнен — игрок всё равно получает подсказки, просто с
    настройками по умолчанию. Сеттеры (`set_*`) ошибку НЕ глушат: там пользователь
    ждёт подтверждения, и молча «сохранить» ничего нельзя.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sf = session_factory
        #: О недоступности настроек кричим ОДИН раз: геттер зовётся на каждое событие,
        #: и полный SQLAlchemy-трейс в цикле сделал бы лог нечитаемым — ровно та беда,
        #: из-за которой в 4.12 глушили INFO httpx.
        self._warned = False

    def _row_unavailable(self, exc: SQLAlchemyError) -> None:
        if self._warned:
            log.debug("player_settings всё ещё недоступны: %s", exc)
            return
        self._warned = True
        reason = str(exc).splitlines()[0] if str(exc) else type(exc).__name__
        log.warning(
            "player_settings недоступны (%s) — работаем на дефолтных настройках. "
            "Чаще всего это НЕ доехавшая миграция: проверь "
            "`alembic -c alembic.ini current` с DATABASE_URL боевой БД.",
            reason,
        )

    async def get_voice_mode(self, discord_id: str) -> str:
        """Режим голоса игрока; 'on', если записи нет, значение битое или БД недоступна."""
        try:
            async with self._sf() as session:
                row = await session.get(PlayerSettings, discord_id)
        except SQLAlchemyError as exc:
            self._row_unavailable(exc)
            return DEFAULT_VOICE_MODE
        if row is None or row.voice_mode not in VOICE_MODES:
            return DEFAULT_VOICE_MODE
        return row.voice_mode

    async def get_combat_text(self, discord_id: str) -> str:
        """Режим боевого текста; default, если записи нет, значение битое или БД недоступна."""
        try:
            async with self._sf() as session:
                row = await session.get(PlayerSettings, discord_id)
        except SQLAlchemyError as exc:
            self._row_unavailable(exc)
            return DEFAULT_COMBAT_TEXT
        if row is None or row.combat_text not in COMBAT_TEXT_MODES:
            return DEFAULT_COMBAT_TEXT
        return row.combat_text

    async def set_combat_text(self, discord_id: str, mode: str) -> None:
        """Установить режим боевого текста. ValueError на неизвестный режим."""
        if mode not in COMBAT_TEXT_MODES:
            raise ValueError(f"Неизвестный text-режим: {mode!r} (ожидается {COMBAT_TEXT_MODES})")
        now = datetime.now(tz=timezone.utc)
        async with self._sf() as session:
            row = await session.get(PlayerSettings, discord_id)
            if row is None:
                session.add(PlayerSettings(discord_id=discord_id, combat_text=mode, updated_at=now))
            else:
                row.combat_text = mode
                row.updated_at = now
            await session.commit()

    async def set_voice_mode(self, discord_id: str, mode: str) -> None:
        """Установить режим голоса. ValueError на неизвестный режим."""
        if mode not in VOICE_MODES:
            raise ValueError(f"Неизвестный voice-режим: {mode!r} (ожидается {VOICE_MODES})")
        now = datetime.now(tz=timezone.utc)
        async with self._sf() as session:
            row = await session.get(PlayerSettings, discord_id)
            if row is None:
                session.add(PlayerSettings(discord_id=discord_id, voice_mode=mode, updated_at=now))
            else:
                row.voice_mode = mode
                row.updated_at = now
            await session.commit()
