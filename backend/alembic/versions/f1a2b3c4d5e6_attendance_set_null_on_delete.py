"""attendance_set_null_on_delete

Revision ID: f1a2b3c4d5e6
Revises: e8f9a0b1c2d3
Create Date: 2026-02-11 18:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f1a2b3c4d5e6"
down_revision: str = "e8f9a0b1c2d3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Make absences.schedule_entry_id nullable + SET NULL, add subject_name/lesson_date.

    Also change lesson_notes FK from CASCADE to SET NULL.
    """
    # --- absences table ---

    # 1. Add subject_name and lesson_date columns (nullable first for backfill)
    op.add_column("absences", sa.Column("subject_name", sa.String(200), nullable=True))
    op.add_column("absences", sa.Column("lesson_date", sa.Date(), nullable=True))

    # 2. Backfill subject_name and lesson_date from schedule_entries
    op.execute(
        """
        UPDATE absences
        SET subject_name = se.subject_name,
            lesson_date = se.lesson_date
        FROM schedule_entries se
        WHERE absences.schedule_entry_id = se.id
        """
    )

    # 3. Set subject_name NOT NULL (all rows should be backfilled)
    # For any orphaned rows without a matching entry, set a placeholder
    op.execute(
        """
        UPDATE absences
        SET subject_name = 'Unknown'
        WHERE subject_name IS NULL
        """
    )
    op.alter_column("absences", "subject_name", nullable=False)

    # 4. Make schedule_entry_id nullable
    op.alter_column(
        "absences",
        "schedule_entry_id",
        existing_type=sa.Integer(),
        nullable=True,
    )

    # 5. Drop old FK and create new one with SET NULL
    op.drop_constraint(
        "absences_schedule_entry_id_fkey", "absences", type_="foreignkey"
    )
    op.create_foreign_key(
        "absences_schedule_entry_id_fkey",
        "absences",
        "schedule_entries",
        ["schedule_entry_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # 6. Add index for subject_name + lesson_date lookups
    op.create_index(
        "ix_absences_user_subject_date",
        "absences",
        ["user_id", "subject_name", "lesson_date"],
    )

    # --- lesson_notes table ---

    # Change FK from CASCADE to SET NULL
    op.drop_constraint(
        "lesson_notes_schedule_entry_id_fkey",
        "lesson_notes",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "lesson_notes_schedule_entry_id_fkey",
        "lesson_notes",
        "schedule_entries",
        ["schedule_entry_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Revert: restore CASCADE, remove subject_name/lesson_date."""
    # --- lesson_notes ---
    op.drop_constraint(
        "lesson_notes_schedule_entry_id_fkey",
        "lesson_notes",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "lesson_notes_schedule_entry_id_fkey",
        "lesson_notes",
        "schedule_entries",
        ["schedule_entry_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # --- absences ---
    op.drop_index("ix_absences_user_subject_date", table_name="absences")

    # Remove NULL entries before making NOT NULL
    op.execute("DELETE FROM absences WHERE schedule_entry_id IS NULL")

    op.drop_constraint(
        "absences_schedule_entry_id_fkey", "absences", type_="foreignkey"
    )
    op.create_foreign_key(
        "absences_schedule_entry_id_fkey",
        "absences",
        "schedule_entries",
        ["schedule_entry_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.alter_column(
        "absences",
        "schedule_entry_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.drop_column("absences", "lesson_date")
    op.drop_column("absences", "subject_name")
