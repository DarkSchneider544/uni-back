"""add_approver_code_to_attendance

Revision ID: 67dac324c4c4
Revises: d4e5f6g7h8i9
Create Date: 2026-02-11 11:03:13.304352

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '67dac324c4c4'
down_revision: Union[str, None] = 'd4e5f6g7h8i9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add approver_code column to attendances table
    op.add_column('attendances', sa.Column('approver_code', sa.String(length=10), nullable=True))
    op.create_foreign_key('fk_attendances_approver_code', 'attendances', 'users', ['approver_code'], ['user_code'])


def downgrade() -> None:
    op.drop_constraint('fk_attendances_approver_code', 'attendances', type_='foreignkey')
    op.drop_column('attendances', 'approver_code')
    op.drop_column('attendances', 'approver_code')
    # ### end Alembic commands ###
