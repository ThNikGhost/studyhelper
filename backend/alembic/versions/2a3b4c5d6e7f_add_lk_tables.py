"""add_lk_tables

Revision ID: 2a3b4c5d6e7f
Revises: 1f580bc1b2b5
Create Date: 2026-02-11 23:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a3b4c5d6e7f'
down_revision: Union[str, Sequence[str], None] = '1f580bc1b2b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create LK-related tables."""
    # Create lk_credentials table
    op.create_table(
        'lk_credentials',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('encrypted_email', sa.Text(), nullable=False),
        sa.Column('encrypted_password', sa.Text(), nullable=False),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )
    op.create_index(op.f('ix_lk_credentials_user_id'), 'lk_credentials', ['user_id'], unique=True)

    # Create session_grades table
    op.create_table(
        'session_grades',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_number', sa.String(length=50), nullable=False),
        sa.Column('subject_name', sa.String(length=300), nullable=False),
        sa.Column('result', sa.String(length=50), nullable=False),
        sa.Column('synced_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'session_number', 'subject_name', name='uq_session_grade'),
    )
    op.create_index(op.f('ix_session_grades_user_id'), 'session_grades', ['user_id'], unique=False)

    # Create semester_disciplines table
    op.create_table(
        'semester_disciplines',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('semester_number', sa.Integer(), nullable=False),
        sa.Column('discipline_name', sa.String(length=300), nullable=False),
        sa.Column('control_form', sa.String(length=100), nullable=False),
        sa.Column('hours', sa.Integer(), nullable=False),
        sa.Column('synced_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'semester_number', 'discipline_name', name='uq_semester_discipline'),
    )
    op.create_index(op.f('ix_semester_disciplines_user_id'), 'semester_disciplines', ['user_id'], unique=False)


def downgrade() -> None:
    """Drop LK-related tables."""
    op.drop_index(op.f('ix_semester_disciplines_user_id'), table_name='semester_disciplines')
    op.drop_table('semester_disciplines')
    op.drop_index(op.f('ix_session_grades_user_id'), table_name='session_grades')
    op.drop_table('session_grades')
    op.drop_index(op.f('ix_lk_credentials_user_id'), table_name='lk_credentials')
    op.drop_table('lk_credentials')
