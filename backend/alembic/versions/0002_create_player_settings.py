"""create player_settings table (Phase 4.5 — voice)

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-24

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "player_settings",
        sa.Column("discord_id", sa.String(length=64), nullable=False),
        sa.Column("voice_mode", sa.String(length=8), nullable=False, server_default="on"),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("discord_id"),
    )


def downgrade() -> None:
    op.drop_table("player_settings")
