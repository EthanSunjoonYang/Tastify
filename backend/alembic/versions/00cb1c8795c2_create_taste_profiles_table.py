"""create taste_profiles table

Revision ID: 00cb1c8795c2
Revises: 51498a7db256
Create Date: 2026-08-06

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "00cb1c8795c2"
down_revision: str | None = "51498a7db256"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "taste_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("era_vector", postgresql.JSONB(), nullable=False),
        sa.Column("top_artist_ids", postgresql.JSONB(), nullable=False),
        sa.Column("top_track_ids", postgresql.JSONB(), nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_unique_constraint(
        "uq_taste_profiles_user_id", "taste_profiles", ["user_id"]
    )
    op.create_foreign_key(
        "fk_taste_profiles_user_id", "taste_profiles", "users", ["user_id"], ["id"]
    )


def downgrade() -> None:
    op.drop_table("taste_profiles")
