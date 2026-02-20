"""make lesson notes shared (one per subject, visible to all users)

Revision ID: i9j0k1l2m3n4
Revises: h8i9j0k1l2m3
Create Date: 2026-02-20 18:00:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "i9j0k1l2m3n4"
down_revision: str | Sequence[str] | None = "h8i9j0k1l2m3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Convert lesson_notes from per-user to shared (one note per subject_name)."""
    # 1. Deduplicate: keep the most recently updated note per subject_name
    op.execute("""
        DELETE FROM lesson_notes
        WHERE id NOT IN (
            SELECT DISTINCT ON (subject_name) id
            FROM lesson_notes
            ORDER BY subject_name, updated_at DESC
        )
    """)

    # 2. Re-create FK with ondelete=SET NULL (was CASCADE)
    op.drop_constraint("lesson_notes_user_id_fkey", "lesson_notes", type_="foreignkey")
    op.create_foreign_key(
        "lesson_notes_user_id_fkey",
        "lesson_notes",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # 3. Drop old per-user unique constraint and index
    op.drop_constraint("uq_lesson_note_user_subject", "lesson_notes", type_="unique")
    op.drop_index("ix_lesson_notes_user_date", table_name="lesson_notes")

    # 4. Make user_id nullable
    op.alter_column("lesson_notes", "user_id", nullable=True)

    # 5. Create new shared unique constraint and index
    op.create_unique_constraint(
        "uq_lesson_note_subject", "lesson_notes", ["subject_name"]
    )
    op.create_index("ix_lesson_notes_lesson_date", "lesson_notes", ["lesson_date"])


def downgrade() -> None:
    """Revert to per-user lesson notes."""
    # 1. Remove shared constraints/index
    op.drop_constraint("uq_lesson_note_subject", "lesson_notes", type_="unique")
    op.drop_index("ix_lesson_notes_lesson_date", table_name="lesson_notes")

    # 2. Delete notes where user_id is NULL (cannot restore original owner)
    op.execute("DELETE FROM lesson_notes WHERE user_id IS NULL")

    # 3. Make user_id NOT NULL again
    op.alter_column("lesson_notes", "user_id", nullable=False)

    # 4. Re-create FK with ondelete=CASCADE
    op.drop_constraint("lesson_notes_user_id_fkey", "lesson_notes", type_="foreignkey")
    op.create_foreign_key(
        "lesson_notes_user_id_fkey",
        "lesson_notes",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # 5. Restore old per-user unique constraint and index
    op.create_unique_constraint(
        "uq_lesson_note_user_subject", "lesson_notes", ["user_id", "subject_name"]
    )
    op.create_index(
        "ix_lesson_notes_user_date", "lesson_notes", ["user_id", "lesson_date"]
    )
