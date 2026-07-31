"""Drop dormant runtime_sessions table (Wave 6 / G2).

Revision ID: 049
Revises: 048
Create Date: 2026-07-31

downgrade restores the table *structure* only, not the data — row content
lives exclusively in the archive artifact from G2 step 2 when COUNT(*) > 0
(``docs/superpowers/plans/baselines/W6-G2-runtime-sessions-archive.json``).
When COUNT was 0 at drop time, there is no archive and downgrade still
yields an empty table.
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = "049"
down_revision = "048"
branch_labels = None
depends_on = None


def upgrade() -> None:
    from sqlalchemy import inspect

    bind = op.get_bind()
    existing = set(inspect(bind).get_table_names())
    if "runtime_sessions" in existing:
        op.drop_table("runtime_sessions")


def downgrade() -> None:
    """Restore runtime_sessions structure only — not archived row data."""
    from sqlalchemy import inspect

    bind = op.get_bind()
    existing = set(inspect(bind).get_table_names())
    if "runtime_sessions" in existing:
        return

    # Prefer dialect JSON when available; SQLite falls back via SQLAlchemy.
    json_type = sa.JSON().with_variant(postgresql.JSON(), "postgresql")
    op.create_table(
        "runtime_sessions",
        sa.Column("session_id", sa.String(length=64), primary_key=True),
        sa.Column("module_id", sa.String(length=120), nullable=False),
        sa.Column(
            "module_version",
            sa.String(length=32),
            nullable=False,
            server_default="1.0.0",
        ),
        sa.Column("session_metadata", json_type, nullable=False),
        sa.Column("canonical_state", json_type, nullable=False),
        sa.Column("current_scene_id", sa.String(length=120), nullable=False),
        sa.Column(
            "status",
            sa.String(length=32),
            nullable=False,
            server_default="active",
        ),
        sa.Column(
            "turn_counter",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
