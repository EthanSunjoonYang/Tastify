"""create lobbies table

Revision ID: e68ac0324e78
Revises: cc4c6bc60324
Create Date: 2026-08-09

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "e68ac0324e78"
down_revision: str | None = "cc4c6bc60324"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "lobbies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("host_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("guest_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_unique_constraint("uq_lobbies_host_user_id", "lobbies", ["host_user_id"])
    op.create_foreign_key(
        "fk_lobbies_host_user_id", "lobbies", "users", ["host_user_id"], ["id"]
    )
    op.create_foreign_key(
        "fk_lobbies_guest_user_id", "lobbies", "users", ["guest_user_id"], ["id"]
    )


def downgrade() -> None:
    op.drop_table("lobbies")
