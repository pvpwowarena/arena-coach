"""Per-player настройки коуча: режим голоса (4.5) и боевой текст (4.15).

Общая точка для двух процессов:
  • bot-процесс пишет через `/coach voice on|off|only` и `/coach text on|off`;
  • api-процесс (pipeline) читает перед отправкой hint'а.
Оба смотрят в один SQLite (coach.db).
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from arena_coach.access.models import PlayerSettings

#: Валидные режимы: on = текст + голос, off = только текст, only = только голос.
VOICE_MODES = ("on", "off", "only")
DEFAULT_VOICE_MODE = "on"

#: Боевой DM (TRINKET/ABILITY/состояние). Разбор на воротах и постматч — всегда.
#: Default `off` (Phase 4.15): «огромный текст в бою читать не очень удобно» —
#: игрок его не читает, а каждый DM это вызов Discord API и риск rate-limit.
COMBAT_TEXT_MODES = ("on", "off")
DEFAULT_COMBAT_TEXT = "off"


class PlayerSettingsService:
    """CRUD-минимум вокруг таблицы player_settings."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._sf = session_factory

    async def get_voice_mode(self, discord_id: str) -> str:
        """Режим голоса игрока; 'on', если записи нет или значение битое."""
        async with self._sf() as session:
            row = await session.get(PlayerSettings, discord_id)
            if row is None or row.voice_mode not in VOICE_MODES:
                return DEFAULT_VOICE_MODE
            return row.voice_mode

    async def get_combat_text(self, discord_id: str) -> str:
        """Режим боевого текста; default, если записи нет или значение битое."""
        async with self._sf() as session:
            row = await session.get(PlayerSettings, discord_id)
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
