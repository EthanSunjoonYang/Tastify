"""create comparisons table

Revision ID: afd9fa61fcdc
Revises: 1d5f70a06a41
Create Date: 2026-08-07

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "afd9fa61fcdc"
down_revision: str | None = "1d5f70a06a41"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "comparisons",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_a_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_b_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("overall_score", sa.Float(), nullable=False),
        sa.Column("era_score", sa.Float(), nullable=False),
        sa.Column("artist_score", sa.Float(), nullable=False),
        sa.Column("shared_artists", postgresql.JSONB(), nullable=False),
        sa.Column("taste_gaps", postgresql.JSONB(), nullable=False),
        sa.Column("era_breakdown", postgresql.JSONB(), nullable=False),
        sa.Column("playlist_track_ids", postgresql.JSONB(), nullable=True),
        sa.Column("spotify_playlist_id", sa.String(length=50), nullable=True),
        sa.Column("computed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_unique_constraint(
        "uq_comparisons_user_a_id_user_b_id", "comparisons", ["user_a_id", "user_b_id"]
    )
    op.create_foreign_key(
        "fk_comparisons_user_a_id", "comparisons", "users", ["user_a_id"], ["id"]
    )
    op.create_foreign_key(
        "fk_comparisons_user_b_id", "comparisons", "users", ["user_b_id"], ["id"]
    )


def downgrade() -> None:
    op.drop_table("comparisons")
