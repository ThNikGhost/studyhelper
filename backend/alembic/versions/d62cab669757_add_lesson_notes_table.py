"""add_lesson_notes_table

Revision ID: d62cab669757
Revises: df769e398a43
Create Date: 2026-02-08 14:57:55.417281

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d62cab669757"
down_revision: str | Sequence[str] | None = "df769e398a43"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "lesson_notes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("schedule_entry_id", sa.Integer(), nullable=True),
        sa.Column("subject_name", sa.String(length=200), nullable=False),
        sa.Column("lesson_date", sa.Date(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
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
            "user_id", "schedule_entry_id", name="uq_lesson_note_user_entry"
        ),
    )
    op.create_index(
        "ix_lesson_notes_user_date",
        "lesson_notes",
        ["user_id", "lesson_date"],
        unique=False,
    )
    op.create_index(
        "ix_lesson_notes_user_subject",
        "lesson_notes",
        ["user_id", "subject_name"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_lesson_notes_user_subject", table_name="lesson_notes")
    op.drop_index("ix_lesson_notes_user_date", table_name="lesson_notes")
    op.drop_table("lesson_notes")
