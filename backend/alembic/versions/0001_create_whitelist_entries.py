"""create whitelist_entries table

Revision ID: 0001
Revises:
Create Date: 2026-05-13

"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "whitelist_entries",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("discord_id", sa.String(length=64), nullable=False),
        sa.Column("character_enc", sa.LargeBinary(), nullable=False),
        sa.Column("realm_enc", sa.LargeBinary(), nullable=False),
        sa.Column(
            "role",
            sa.Enum("viewer", "player", "admin", name="role"),
            nullable=False,
        ),
        sa.Column("added_by", sa.String(length=64), nullable=False),
        sa.Column("added_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_whitelist_entries_discord_id"),
        "whitelist_entries",
        ["discord_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_whitelist_entries_discord_id"), table_name="whitelist_entries"
    )
    op.drop_table("whitelist_entries")
