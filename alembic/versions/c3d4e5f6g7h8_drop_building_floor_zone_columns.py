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
    
    # Drop indexes first (if they exist) using raw SQL with IF EXISTS
    conn = op.get_bind()
    
    # Drop indexes with IF EXISTS
    conn.execute(sa.text('DROP INDEX IF EXISTS ix_desks_building_floor'))
    conn.execute(sa.text('DROP INDEX IF EXISTS ix_conference_rooms_building_floor'))
    conn.execute(sa.text('DROP INDEX IF EXISTS ix_parking_slots_building_floor'))
    conn.execute(sa.text('DROP INDEX IF EXISTS ix_cafeteria_tables_building_floor'))
    
    # Desks table - use raw SQL with IF EXISTS
    conn.execute(sa.text('ALTER TABLE desks DROP COLUMN IF EXISTS building'))
    conn.execute(sa.text('ALTER TABLE desks DROP COLUMN IF EXISTS floor'))
    conn.execute(sa.text('ALTER TABLE desks DROP COLUMN IF EXISTS zone'))
    
    # Conference rooms table
    conn.execute(sa.text('ALTER TABLE conference_rooms DROP COLUMN IF EXISTS building'))
    conn.execute(sa.text('ALTER TABLE conference_rooms DROP COLUMN IF EXISTS floor'))
    conn.execute(sa.text('ALTER TABLE conference_rooms DROP COLUMN IF EXISTS zone'))
    
    # Parking slots table
    conn.execute(sa.text('ALTER TABLE parking_slots DROP COLUMN IF EXISTS building'))
    conn.execute(sa.text('ALTER TABLE parking_slots DROP COLUMN IF EXISTS floor'))
    conn.execute(sa.text('ALTER TABLE parking_slots DROP COLUMN IF EXISTS zone'))
    
    # Cafeteria tables table
    conn.execute(sa.text('ALTER TABLE cafeteria_tables DROP COLUMN IF EXISTS building'))
    conn.execute(sa.text('ALTER TABLE cafeteria_tables DROP COLUMN IF EXISTS floor'))
    conn.execute(sa.text('ALTER TABLE cafeteria_tables DROP COLUMN IF EXISTS zone'))


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
