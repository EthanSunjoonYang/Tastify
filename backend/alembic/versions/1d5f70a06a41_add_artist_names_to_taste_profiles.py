"""add artist_names to taste_profiles

Revision ID: 1d5f70a06a41
Revises: 00cb1c8795c2
Create Date: 2026-08-07

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "1d5f70a06a41"
down_revision: str | None = "00cb1c8795c2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "taste_profiles",
        sa.Column(
            "artist_names", postgresql.JSONB(), nullable=False, server_default="{}"
        ),
    )
    op.alter_column("taste_profiles", "artist_names", server_default=None)


def downgrade() -> None:
    op.drop_column("taste_profiles", "artist_names")
