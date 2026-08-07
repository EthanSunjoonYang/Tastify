"""add artist_images to taste_profiles

Revision ID: cc4c6bc60324
Revises: 55f62c933c12
Create Date: 2026-08-07

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "cc4c6bc60324"
down_revision: str | None = "55f62c933c12"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "taste_profiles",
        sa.Column("artist_images", postgresql.JSONB(), nullable=False, server_default="{}"),
    )
    op.alter_column("taste_profiles", "artist_images", server_default=None)


def downgrade() -> None:
    op.drop_column("taste_profiles", "artist_images")
