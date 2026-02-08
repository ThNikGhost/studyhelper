"""add_absences_table

Revision ID: df769e398a43
Revises: 931762f130d3
Create Date: 2026-02-08 14:06:58.115541

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "df769e398a43"
down_revision: str | Sequence[str] | None = "931762f130d3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "absences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("schedule_entry_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["schedule_entry_id"], ["schedule_entries.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "schedule_entry_id", name="uq_absence_user_entry"
        ),
    )
    op.create_index(
        "ix_absences_schedule_entry_id", "absences", ["schedule_entry_id"], unique=False
    )
    op.create_index("ix_absences_user_id", "absences", ["user_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_absences_user_id", table_name="absences")
    op.drop_index("ix_absences_schedule_entry_id", table_name="absences")
    op.drop_table("absences")
