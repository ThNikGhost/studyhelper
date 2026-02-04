"""add lesson_date to schedule_entries

Revision ID: c937e42e988d
Revises: g7h8i9j0k1l2
Create Date: 2026-02-04 23:40:05.682866

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c937e42e988d"
down_revision: str | Sequence[str] | None = "g7h8i9j0k1l2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "schedule_entries", sa.Column("lesson_date", sa.Date(), nullable=True)
    )
    op.create_index(
        op.f("ix_schedule_entries_lesson_date"),
        "schedule_entries",
        ["lesson_date"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_schedule_entries_lesson_date"), table_name="schedule_entries"
    )
    op.drop_column("schedule_entries", "lesson_date")
