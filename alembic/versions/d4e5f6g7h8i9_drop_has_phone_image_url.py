"""Drop has_phone and image_url from conference_rooms

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2025-02-10 13:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6g7h8i9'
down_revision: Union[str, None] = 'c3d4e5f6g7h8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Drop unnecessary columns from conference_rooms:
    - has_phone
    - image_url
    
    Also rename room_name to room_label and has_video_conference to has_video_conferencing
    """
    
    # Drop unnecessary columns
    op.drop_column('conference_rooms', 'has_phone')
    op.drop_column('conference_rooms', 'image_url')
    
    # Rename columns for consistency
    op.alter_column('conference_rooms', 'room_name', new_column_name='room_label')
    op.alter_column('conference_rooms', 'has_video_conference', new_column_name='has_video_conferencing')


def downgrade() -> None:
    """
    Re-add columns to conference_rooms.
    """
    
    # Rename columns back
    op.alter_column('conference_rooms', 'room_label', new_column_name='room_name')
    op.alter_column('conference_rooms', 'has_video_conferencing', new_column_name='has_video_conference')
    
    # Re-add columns
    op.add_column('conference_rooms', sa.Column('has_phone', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('conference_rooms', sa.Column('image_url', sa.String(500), nullable=True))
