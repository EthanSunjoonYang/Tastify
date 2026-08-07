"""add track_meta to taste_profiles

Revision ID: 55f62c933c12
Revises: afd9fa61fcdc
Create Date: 2026-08-07

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "55f62c933c12"
down_revision: str | None = "afd9fa61fcdc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "taste_profiles",
        sa.Column("track_meta", postgresql.JSONB(), nullable=False, server_default="{}"),
    )
    op.alter_column("taste_profiles", "track_meta", server_default=None)


def downgrade() -> None:
    op.drop_column("taste_profiles", "track_meta")
