"""add hidden_subjects to users

Revision ID: a1b2c3d4e5f7
Revises: 02665a1d4d94
Create Date: 2026-02-19 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f7"
down_revision: str | Sequence[str] | None = "02665a1d4d94"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add hidden_subjects JSON field to users table."""
    op.add_column("users", sa.Column("hidden_subjects", sa.JSON(), nullable=True))


def downgrade() -> None:
    """Remove hidden_subjects from users table."""
    op.drop_column("users", "hidden_subjects")
