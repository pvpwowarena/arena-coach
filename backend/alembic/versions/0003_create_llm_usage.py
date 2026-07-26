"""create llm_usage table (Phase 4.7 — token usage stats for admin)

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-26

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Защитно: если таблицу уже создал Base.metadata.create_all (lifespan) —
    # не падаем на «table already exists».
    bind = op.get_bind()
    if "llm_usage" in sa.inspect(bind).get_table_names():
        return
    op.create_table(
        "llm_usage",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("day", sa.String(length=10), nullable=False),
        sa.Column("purpose", sa.String(length=32), nullable=False),
        sa.Column("model", sa.String(length=64), nullable=False),
        sa.Column("input_tokens", sa.Integer(), server_default="0", nullable=False),
        sa.Column("output_tokens", sa.Integer(), server_default="0", nullable=False),
        sa.Column("calls", sa.Integer(), server_default="0", nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("day", "purpose", "model", name="uq_llm_usage_bucket"),
    )


def downgrade() -> None:
    op.drop_table("llm_usage")
