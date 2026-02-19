"""convert hidden_subjects from list to dict format

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2
Create Date: 2026-02-19 12:00:00.000000

"""

from __future__ import annotations

import json
from collections.abc import Sequence

from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "h8i9j0k1l2m3"
down_revision: str | Sequence[str] | None = "g7h8i9j0k1l2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Convert hidden_subjects from list[int] to dict[str, null]."""
    conn = op.get_bind()
    rows = conn.execute(
        text("SELECT id, hidden_subjects FROM users WHERE hidden_subjects IS NOT NULL")
    )
    for row in rows:
        old = row.hidden_subjects
        if isinstance(old, str):
            old = json.loads(old)
        if isinstance(old, list):
            new = {str(sid): None for sid in old if isinstance(sid, int) and sid > 0}
            if new:
                conn.execute(
                    text("UPDATE users SET hidden_subjects = :val WHERE id = :id"),
                    {"val": json.dumps(new), "id": row.id},
                )
            else:
                conn.execute(
                    text("UPDATE users SET hidden_subjects = NULL WHERE id = :id"),
                    {"id": row.id},
                )


def downgrade() -> None:
    """Convert hidden_subjects from dict back to list[int]."""
    conn = op.get_bind()
    rows = conn.execute(
        text("SELECT id, hidden_subjects FROM users WHERE hidden_subjects IS NOT NULL")
    )
    for row in rows:
        old = row.hidden_subjects
        if isinstance(old, str):
            old = json.loads(old)
        if isinstance(old, dict):
            new = [int(k) for k in old if k.isdigit()]
            if new:
                conn.execute(
                    text("UPDATE users SET hidden_subjects = :val WHERE id = :id"),
                    {"val": json.dumps(new), "id": row.id},
                )
            else:
                conn.execute(
                    text("UPDATE users SET hidden_subjects = NULL WHERE id = :id"),
                    {"id": row.id},
                )
