"""add player_settings.combat_text (Phase 4.15 — боевой DM в opt-in)

Revision ID: 0005
Revises: 0004
Create Date: 2026-07-30

Живой тест 30.07: «огромный текст в бою читать не очень удобно». Боевой DM тогда
урезали до двух строк, но игрок его всё равно не читает — а каждый такой DM это
вызов Discord API. Теперь боевой текст по умолчанию выключен ('off'), а разбор на
воротах и постматч приходят всегда. Вернуть — `/coach text on`.

Идемпотентна: если колонка уже есть (create_all на свежей БД), выходим молча.
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_TABLE = "player_settings"
_COLUMN = "combat_text"


def _has_column(bind: sa.engine.Connection) -> bool:
    inspector = sa.inspect(bind)
    if _TABLE not in inspector.get_table_names():
        return True  # таблицы нет — создаст create_all уже с колонкой
    return any(c["name"] == _COLUMN for c in inspector.get_columns(_TABLE))


def upgrade() -> None:
    bind = op.get_bind()
    if _has_column(bind):
        return
    op.add_column(
        _TABLE,
        sa.Column(_COLUMN, sa.String(length=8), nullable=False, server_default="off"),
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if _TABLE not in inspector.get_table_names():
        return
    if any(c["name"] == _COLUMN for c in inspector.get_columns(_TABLE)):
        op.drop_column(_TABLE, _COLUMN)
