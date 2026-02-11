"""change_note_unique_to_subject

Revision ID: e8f9a0b1c2d3
Revises: a3b4c5d6e7f8
Create Date: 2026-02-11 12:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e8f9a0b1c2d3"
down_revision: str | Sequence[str] | None = "a3b4c5d6e7f8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Change unique constraint from (user_id, schedule_entry_id) to (user_id, subject_name).

    Deduplicates existing notes: for each (user_id, subject_name) pair,
    keeps only the note with the latest updated_at.
    """
    # Step 1: Deduplicate — delete older notes for same (user_id, subject_name)
    op.execute("""
        DELETE FROM lesson_notes
        WHERE id NOT IN (
            SELECT DISTINCT ON (user_id, subject_name) id
            FROM lesson_notes
            ORDER BY user_id, subject_name, updated_at DESC
        )
    """)

    # Step 2: Drop old unique constraint on (user_id, schedule_entry_id)
    op.drop_constraint("uq_lesson_note_user_entry", "lesson_notes", type_="unique")

    # Step 3: Drop old non-unique index on (user_id, subject_name)
    op.drop_index("ix_lesson_notes_user_subject", table_name="lesson_notes")

    # Step 4: Create new unique constraint on (user_id, subject_name)
    op.create_unique_constraint(
        "uq_lesson_note_user_subject",
        "lesson_notes",
        ["user_id", "subject_name"],
    )


def downgrade() -> None:
    """Revert to original constraint."""
    # Drop new unique constraint
    op.drop_constraint("uq_lesson_note_user_subject", "lesson_notes", type_="unique")

    # Recreate old index
    op.create_index(
        "ix_lesson_notes_user_subject",
        "lesson_notes",
        ["user_id", "subject_name"],
        unique=False,
    )

    # Recreate old unique constraint
    op.create_unique_constraint(
        "uq_lesson_note_user_entry",
        "lesson_notes",
        ["user_id", "schedule_entry_id"],
    )
