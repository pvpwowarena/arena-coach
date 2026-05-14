"""Alembic environment — поддерживает синхронный SQLite для миграций.

Использует sync_database_url из settings (без +aiosqlite).
"""

from __future__ import annotations

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Импортируем метаданные всех моделей
from arena_coach.access.models import Base

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _get_url() -> str:
    """Получить sync DATABASE_URL из settings или alembic.ini."""
    try:
        from arena_coach.shared.settings import settings

        return settings.sync_database_url
    except Exception:
        url = config.get_main_option("sqlalchemy.url")
        if url is None:
            raise RuntimeError("DATABASE_URL / sqlalchemy.url не задан") from None
        return url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (без подключения к БД)."""
    url = _get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (с подключением к БД)."""
    cfg = config.get_section(config.config_ini_section, {})
    cfg["sqlalchemy.url"] = _get_url()

    connectable = engine_from_config(
        cfg,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
