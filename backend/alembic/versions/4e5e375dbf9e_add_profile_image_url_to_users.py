"""add profile_image_url to users

Revision ID: 4e5e375dbf9e
Revises: e68ac0324e78
Create Date: 2026-08-09

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "4e5e375dbf9e"
down_revision: str | None = "e68ac0324e78"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("users", sa.Column("profile_image_url", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "profile_image_url")
