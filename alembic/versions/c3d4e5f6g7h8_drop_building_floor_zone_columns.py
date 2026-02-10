"""Drop building floor zone columns from all tables

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2025-02-10 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6g7h8'
down_revision: Union[str, None] = 'b2c3d4e5f6g7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Drop building, floor, zone columns from:
    - desks
    - conference_rooms
    - parking_slots
    - cafeteria_tables
    
    These location fields are no longer needed.
    """
    
    # Drop indexes first (if they exist)
    # Note: Using try/except to handle cases where indexes may not exist
    
    # Desks table
    try:
        op.drop_index('ix_desks_building_floor', table_name='desks')
    except Exception:
        pass
    
    op.drop_column('desks', 'building')
    op.drop_column('desks', 'floor')
    op.drop_column('desks', 'zone')
    
    # Conference rooms table
    try:
        op.drop_index('ix_conference_rooms_building_floor', table_name='conference_rooms')
    except Exception:
        pass
    
    op.drop_column('conference_rooms', 'building')
    op.drop_column('conference_rooms', 'floor')
    op.drop_column('conference_rooms', 'zone')
    
    # Parking slots table
    try:
        op.drop_index('ix_parking_slots_building_floor', table_name='parking_slots')
    except Exception:
        pass
    
    op.drop_column('parking_slots', 'building')
    op.drop_column('parking_slots', 'floor')
    op.drop_column('parking_slots', 'zone')
    
    # Cafeteria tables table
    try:
        op.drop_index('ix_cafeteria_tables_building_floor', table_name='cafeteria_tables')
    except Exception:
        pass
    
    op.drop_column('cafeteria_tables', 'building')
    op.drop_column('cafeteria_tables', 'floor')
    op.drop_column('cafeteria_tables', 'zone')


def downgrade() -> None:
    """
    Re-add building, floor, zone columns to all tables.
    """
    
    # Cafeteria tables
    op.add_column('cafeteria_tables', sa.Column('building', sa.String(100), nullable=True))
    op.add_column('cafeteria_tables', sa.Column('floor', sa.String(50), nullable=True))
    op.add_column('cafeteria_tables', sa.Column('zone', sa.String(50), nullable=True))
    op.create_index('ix_cafeteria_tables_building_floor', 'cafeteria_tables', ['building', 'floor'])
    
    # Parking slots
    op.add_column('parking_slots', sa.Column('building', sa.String(100), nullable=True))
    op.add_column('parking_slots', sa.Column('floor', sa.String(50), nullable=True))
    op.add_column('parking_slots', sa.Column('zone', sa.String(50), nullable=True))
    op.create_index('ix_parking_slots_building_floor', 'parking_slots', ['building', 'floor'])
    
    # Conference rooms
    op.add_column('conference_rooms', sa.Column('building', sa.String(100), nullable=True))
    op.add_column('conference_rooms', sa.Column('floor', sa.String(50), nullable=True))
    op.add_column('conference_rooms', sa.Column('zone', sa.String(50), nullable=True))
    op.create_index('ix_conference_rooms_building_floor', 'conference_rooms', ['building', 'floor'])
    
    # Desks
    op.add_column('desks', sa.Column('building', sa.String(100), nullable=True))
    op.add_column('desks', sa.Column('floor', sa.String(50), nullable=True))
    op.add_column('desks', sa.Column('zone', sa.String(50), nullable=True))
    op.create_index('ix_desks_building_floor', 'desks', ['building', 'floor'])
