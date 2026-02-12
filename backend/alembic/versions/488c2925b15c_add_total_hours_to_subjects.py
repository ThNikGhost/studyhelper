"""add_total_hours_to_subjects

Revision ID: 488c2925b15c
Revises: 2a3b4c5d6e7f
Create Date: 2026-02-12 01:51:53.899828

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "488c2925b15c"
down_revision: str | Sequence[str] | None = "2a3b4c5d6e7f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("subjects", sa.Column("total_hours", sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("subjects", "total_hours")
