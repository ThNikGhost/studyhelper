"""add_semester_dates

Revision ID: a3b4c5d6e7f8
Revises: d62cab669757
Create Date: 2026-02-08 18:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a3b4c5d6e7f8"
down_revision: str | None = "d62cab669757"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add start_date and end_date columns to semesters table."""
    op.add_column("semesters", sa.Column("start_date", sa.Date(), nullable=True))
    op.add_column("semesters", sa.Column("end_date", sa.Date(), nullable=True))


def downgrade() -> None:
    """Remove start_date and end_date columns from semesters table."""
    op.drop_column("semesters", "end_date")
    op.drop_column("semesters", "start_date")
