"""create advice_cache table (Phase 4.7 — persistent LLM advice cache)

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-26

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    if "advice_cache" in sa.inspect(bind).get_table_names():
        return
    op.create_table(
        "advice_cache",
        sa.Column("sig", sa.String(length=200), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("model", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("sig"),
    )


def downgrade() -> None:
    op.drop_table("advice_cache")
