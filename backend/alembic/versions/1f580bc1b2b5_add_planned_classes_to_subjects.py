"""add_planned_classes_to_subjects

Revision ID: 1f580bc1b2b5
Revises: f1a2b3c4d5e6
Create Date: 2026-02-11 19:02:46.601243

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f580bc1b2b5'
down_revision: Union[str, Sequence[str], None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add planned_classes column to subjects table."""
    op.add_column('subjects', sa.Column('planned_classes', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Remove planned_classes column from subjects table."""
    op.drop_column('subjects', 'planned_classes')
