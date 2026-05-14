"""pydantic-settings: загрузка .env. Phase 2."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Все настройки приложения — читаются из .env и переменных окружения.

    Приоритет: env vars > .env файл > defaults.
    Секреты (токен, fernet key) обязательны при запуске бота,
    но могут отсутствовать в тестах (пустая строка — индикатор «не настроено»).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ── Discord ───────────────────────────────────────────────────────────
    discord_bot_token: str = Field(default="", description="Bot token из Developer Portal")
    discord_guild_id: int = Field(default=0, description="ID приватного Discord-сервера")
    # CSV или JSON-список Discord-ID владельцев (всегда admin, нельзя удалить через /access remove).
    # В .env: ARENA_COACH_OWNER_DISCORD_IDS=123456789,987654321
    arena_coach_owner_discord_ids: list[str] = Field(default_factory=list)

    # ── Anthropic ─────────────────────────────────────────────────────────
    anthropic_api_key: str = Field(default="")
    anthropic_model_synth: str = "claude-sonnet-4-6"
    anthropic_model_classify: str = "claude-haiku-4-5-20251001"

    # ── Storage ───────────────────────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./coach.db"
    kb_path: Path = Path("kb")
    audit_log_dir: Path = Path("audit")

    # ── Crypto ────────────────────────────────────────────────────────────
    # 32-байтный Fernet-ключ (base64url).
    # Генерация: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    arena_coach_fernet_key: str = Field(default="")
    # Предыдущий ключ при ротации (для дешифровки старых записей)
    arena_coach_fernet_prev_key: str | None = Field(default=None)

    # ── WSS / bridge ──────────────────────────────────────────────────────
    wss_bind: str = "127.0.0.1:8765"
    wss_public_url: str = "wss://coach.example.com/ws"
    bridge_bearer_token: str = ""

    # ── Ops ───────────────────────────────────────────────────────────────
    log_level: str = "INFO"
    sentry_dsn: str = ""

    # ── Validators ────────────────────────────────────────────────────────

    @field_validator("arena_coach_owner_discord_ids", mode="before")
    @classmethod
    def _parse_owner_ids(cls, v: object) -> object:
        """Поддерживаем CSV-строку ('123,456') и JSON-список ('["123","456"]')."""
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                return json.loads(v)
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    # ── Properties ───────────────────────────────────────────────────────

    @property
    def owner_ids_set(self) -> frozenset[str]:
        """frozenset Discord-ID владельцев для O(1)-проверки."""
        return frozenset(self.arena_coach_owner_discord_ids)

    @property
    def sync_database_url(self) -> str:
        """Синхронный URL для alembic-миграций (убирает +aiosqlite)."""
        return self.database_url.replace("+aiosqlite", "")


# Синглтон — импортируем в других модулях:
#   from arena_coach.shared.settings import settings
settings: Settings = Settings()
