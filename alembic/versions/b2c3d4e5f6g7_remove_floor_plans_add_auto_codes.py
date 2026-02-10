"""Remove floor plans and add auto-generated codes

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-10 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6g7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop foreign key constraints that reference floor_plans
    op.drop_constraint('desks_floor_plan_id_fkey', 'desks', type_='foreignkey')
    op.drop_constraint('parking_slots_floor_plan_id_fkey', 'parking_slots', type_='foreignkey')
    op.drop_constraint('cafeteria_tables_floor_plan_id_fkey', 'cafeteria_tables', type_='foreignkey')
    op.drop_constraint('conference_rooms_floor_plan_id_fkey', 'conference_rooms', type_='foreignkey')
    op.drop_constraint('floor_plan_versions_floor_plan_id_fkey', 'floor_plan_versions', type_='foreignkey')
    
    # Drop indexes that reference floor_plan_id
    op.drop_index('ix_desks_floor', table_name='desks')
    op.drop_index('ix_parking_slots_floor', table_name='parking_slots')
    op.drop_index('ix_cafeteria_tables_floor', table_name='cafeteria_tables')
    op.drop_index('ix_conference_rooms_floor', table_name='conference_rooms')
    op.drop_index('ix_floor_plan_versions_unique', table_name='floor_plan_versions')
    
    # Drop floor_plan_versions table
    op.drop_table('floor_plan_versions')
    
    # Drop floor_plans table
    op.drop_index('ix_floor_plans_active_type', table_name='floor_plans')
    op.drop_index('ix_floor_plans_code', table_name='floor_plans')
    op.drop_index(op.f('ix_floor_plans_floor_code'), table_name='floor_plans')
    op.drop_index('ix_floor_plans_type', table_name='floor_plans')
    op.drop_table('floor_plans')
    
    # Drop the FloorPlanType enum
    op.execute('DROP TYPE IF EXISTS floorplantype')
    
    # === DESKS TABLE MODIFICATIONS ===
    # Remove floor_plan_id and cell coordinates
    op.drop_column('desks', 'floor_plan_id')
    op.drop_column('desks', 'cell_row')
    op.drop_column('desks', 'cell_column')
    
    # Add new columns for desk
    op.add_column('desks', sa.Column('created_by_code', sa.String(length=10), nullable=True))
    op.add_column('desks', sa.Column('building', sa.String(length=100), nullable=True))
    op.add_column('desks', sa.Column('floor', sa.String(length=50), nullable=True))
    
    # Create foreign key for created_by_code
    op.create_foreign_key('fk_desks_created_by_code', 'desks', 'users', ['created_by_code'], ['user_code'])
    
    # Create indexes for new columns
    op.create_index('ix_desks_building', 'desks', ['building'], unique=False)
    op.create_index('ix_desks_floor', 'desks', ['floor'], unique=False)
    op.create_index('ix_desks_created_by', 'desks', ['created_by_code'], unique=False)
    
    # === CONFERENCE ROOMS TABLE MODIFICATIONS ===
    # Remove floor_plan_id and cell coordinates
    op.drop_column('conference_rooms', 'floor_plan_id')
    op.drop_column('conference_rooms', 'cell_row')
    op.drop_column('conference_rooms', 'cell_column')
    op.drop_column('conference_rooms', 'cell_span_rows')
    op.drop_column('conference_rooms', 'cell_span_cols')
    
    # Add new columns for conference rooms
    op.add_column('conference_rooms', sa.Column('created_by_code', sa.String(length=10), nullable=True))
    op.add_column('conference_rooms', sa.Column('building', sa.String(length=100), nullable=True))
    op.add_column('conference_rooms', sa.Column('floor', sa.String(length=50), nullable=True))
    op.add_column('conference_rooms', sa.Column('zone', sa.String(length=50), nullable=True))
    
    # Create foreign key for created_by_code
    op.create_foreign_key('fk_conference_rooms_created_by_code', 'conference_rooms', 'users', ['created_by_code'], ['user_code'])
    
    # Create indexes for new columns
    op.create_index('ix_conference_rooms_building', 'conference_rooms', ['building'], unique=False)
    op.create_index('ix_conference_rooms_floor', 'conference_rooms', ['floor'], unique=False)
    op.create_index('ix_conference_rooms_zone', 'conference_rooms', ['zone'], unique=False)
    op.create_index('ix_conference_rooms_created_by', 'conference_rooms', ['created_by_code'], unique=False)
    
    # === PARKING SLOTS TABLE MODIFICATIONS ===
    # Remove floor_plan_id and cell coordinates
    op.drop_column('parking_slots', 'floor_plan_id')
    op.drop_column('parking_slots', 'cell_row')
    op.drop_column('parking_slots', 'cell_column')
    
    # Add new columns for parking slots
    op.add_column('parking_slots', sa.Column('created_by_code', sa.String(length=10), nullable=True))
    op.add_column('parking_slots', sa.Column('building', sa.String(length=100), nullable=True))
    op.add_column('parking_slots', sa.Column('floor', sa.String(length=50), nullable=True))
    op.add_column('parking_slots', sa.Column('zone', sa.String(length=50), nullable=True))
    
    # Create foreign key for created_by_code
    op.create_foreign_key('fk_parking_slots_created_by_code', 'parking_slots', 'users', ['created_by_code'], ['user_code'])
    
    # Create indexes for new columns
    op.create_index('ix_parking_slots_building', 'parking_slots', ['building'], unique=False)
    op.create_index('ix_parking_slots_floor', 'parking_slots', ['floor'], unique=False)
    op.create_index('ix_parking_slots_zone', 'parking_slots', ['zone'], unique=False)
    op.create_index('ix_parking_slots_created_by', 'parking_slots', ['created_by_code'], unique=False)
    
    # === CAFETERIA TABLES TABLE MODIFICATIONS ===
    # Remove floor_plan_id and cell coordinates
    op.drop_column('cafeteria_tables', 'floor_plan_id')
    op.drop_column('cafeteria_tables', 'cell_row')
    op.drop_column('cafeteria_tables', 'cell_column')
    
    # Add new columns for cafeteria tables
    op.add_column('cafeteria_tables', sa.Column('created_by_code', sa.String(length=10), nullable=True))
    op.add_column('cafeteria_tables', sa.Column('building', sa.String(length=100), nullable=True))
    op.add_column('cafeteria_tables', sa.Column('floor', sa.String(length=50), nullable=True))
    op.add_column('cafeteria_tables', sa.Column('zone', sa.String(length=50), nullable=True))
    
    # Create foreign key for created_by_code
    op.create_foreign_key('fk_cafeteria_tables_created_by_code', 'cafeteria_tables', 'users', ['created_by_code'], ['user_code'])
    
    # Create indexes for new columns
    op.create_index('ix_cafeteria_tables_building', 'cafeteria_tables', ['building'], unique=False)
    op.create_index('ix_cafeteria_tables_floor', 'cafeteria_tables', ['floor'], unique=False)
    op.create_index('ix_cafeteria_tables_zone', 'cafeteria_tables', ['zone'], unique=False)
    op.create_index('ix_cafeteria_tables_created_by', 'cafeteria_tables', ['created_by_code'], unique=False)


def downgrade() -> None:
    # === CAFETERIA TABLES - RESTORE ===
    op.drop_index('ix_cafeteria_tables_created_by', table_name='cafeteria_tables')
    op.drop_index('ix_cafeteria_tables_zone', table_name='cafeteria_tables')
    op.drop_index('ix_cafeteria_tables_floor', table_name='cafeteria_tables')
    op.drop_index('ix_cafeteria_tables_building', table_name='cafeteria_tables')
    op.drop_constraint('fk_cafeteria_tables_created_by_code', 'cafeteria_tables', type_='foreignkey')
    
    op.drop_column('cafeteria_tables', 'zone')
    op.drop_column('cafeteria_tables', 'floor')
    op.drop_column('cafeteria_tables', 'building')
    op.drop_column('cafeteria_tables', 'created_by_code')
    
    op.add_column('cafeteria_tables', sa.Column('cell_column', sa.INTEGER(), nullable=False, server_default='0'))
    op.add_column('cafeteria_tables', sa.Column('cell_row', sa.INTEGER(), nullable=False, server_default='0'))
    op.add_column('cafeteria_tables', sa.Column('floor_plan_id', sa.UUID(), nullable=True))
    
    # === PARKING SLOTS - RESTORE ===
    op.drop_index('ix_parking_slots_created_by', table_name='parking_slots')
    op.drop_index('ix_parking_slots_zone', table_name='parking_slots')
    op.drop_index('ix_parking_slots_floor', table_name='parking_slots')
    op.drop_index('ix_parking_slots_building', table_name='parking_slots')
    op.drop_constraint('fk_parking_slots_created_by_code', 'parking_slots', type_='foreignkey')
    
    op.drop_column('parking_slots', 'zone')
    op.drop_column('parking_slots', 'floor')
    op.drop_column('parking_slots', 'building')
    op.drop_column('parking_slots', 'created_by_code')
    
    op.add_column('parking_slots', sa.Column('cell_column', sa.INTEGER(), nullable=False, server_default='0'))
    op.add_column('parking_slots', sa.Column('cell_row', sa.INTEGER(), nullable=False, server_default='0'))
    op.add_column('parking_slots', sa.Column('floor_plan_id', sa.UUID(), nullable=True))
    
    # === CONFERENCE ROOMS - RESTORE ===
    op.drop_index('ix_conference_rooms_created_by', table_name='conference_rooms')
    op.drop_index('ix_conference_rooms_zone', table_name='conference_rooms')
    op.drop_index('ix_conference_rooms_floor', table_name='conference_rooms')
    op.drop_index('ix_conference_rooms_building', table_name='conference_rooms')
    op.drop_constraint('fk_conference_rooms_created_by_code', 'conference_rooms', type_='foreignkey')
    
    op.drop_column('conference_rooms', 'zone')
    op.drop_column('conference_rooms', 'floor')
    op.drop_column('conference_rooms', 'building')
    op.drop_column('conference_rooms', 'created_by_code')
    
    op.add_column('conference_rooms', sa.Column('cell_span_cols', sa.INTEGER(), nullable=True))
    op.add_column('conference_rooms', sa.Column('cell_span_rows', sa.INTEGER(), nullable=True))
    op.add_column('conference_rooms', sa.Column('cell_column', sa.INTEGER(), nullable=False, server_default='0'))
    op.add_column('conference_rooms', sa.Column('cell_row', sa.INTEGER(), nullable=False, server_default='0'))
    op.add_column('conference_rooms', sa.Column('floor_plan_id', sa.UUID(), nullable=True))
    
    # === DESKS - RESTORE ===
    op.drop_index('ix_desks_created_by', table_name='desks')
    op.drop_index('ix_desks_floor', table_name='desks')
    op.drop_index('ix_desks_building', table_name='desks')
    op.drop_constraint('fk_desks_created_by_code', 'desks', type_='foreignkey')
    
    op.drop_column('desks', 'floor')
    op.drop_column('desks', 'building')
    op.drop_column('desks', 'created_by_code')
    
    op.add_column('desks', sa.Column('cell_column', sa.INTEGER(), nullable=False, server_default='0'))
    op.add_column('desks', sa.Column('cell_row', sa.INTEGER(), nullable=False, server_default='0'))
    op.add_column('desks', sa.Column('floor_plan_id', sa.UUID(), nullable=True))
    
    # Recreate floor_plans table
    op.execute("CREATE TYPE floorplantype AS ENUM ('PARKING', 'DESK_AREA', 'CAFETERIA')")
    
    op.create_table('floor_plans',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('floor_code', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('plan_type', postgresql.ENUM('PARKING', 'DESK_AREA', 'CAFETERIA', name='floorplantype', create_type=False), nullable=False),
        sa.Column('rows', sa.Integer(), nullable=False),
        sa.Column('columns', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('current_version', sa.Integer(), nullable=True),
        sa.Column('created_by_code', sa.String(length=10), nullable=False),
        sa.Column('building_name', sa.String(length=100), nullable=True),
        sa.Column('floor_number', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by_code'], ['users.user_code'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_floor_plans_active_type', 'floor_plans', ['is_active', 'plan_type'], unique=False)
    op.create_index('ix_floor_plans_code', 'floor_plans', ['floor_code'], unique=False)
    op.create_index(op.f('ix_floor_plans_floor_code'), 'floor_plans', ['floor_code'], unique=True)
    op.create_index('ix_floor_plans_type', 'floor_plans', ['plan_type'], unique=False)
    
    # Recreate floor_plan_versions table
    op.create_table('floor_plan_versions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('floor_plan_id', sa.UUID(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('grid_data', sa.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_by_code', sa.String(length=10), nullable=False),
        sa.Column('change_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by_code'], ['users.user_code'], ),
        sa.ForeignKeyConstraint(['floor_plan_id'], ['floor_plans.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_floor_plan_versions_unique', 'floor_plan_versions', ['floor_plan_id', 'version'], unique=True)
    
    # Recreate foreign keys and indexes
    op.create_index('ix_desks_floor', 'desks', ['floor_plan_id'], unique=False)
    op.create_foreign_key('desks_floor_plan_id_fkey', 'desks', 'floor_plans', ['floor_plan_id'], ['id'])
    
    op.create_index('ix_conference_rooms_floor', 'conference_rooms', ['floor_plan_id'], unique=False)
    op.create_foreign_key('conference_rooms_floor_plan_id_fkey', 'conference_rooms', 'floor_plans', ['floor_plan_id'], ['id'])
    
    op.create_index('ix_parking_slots_floor', 'parking_slots', ['floor_plan_id'], unique=False)
    op.create_foreign_key('parking_slots_floor_plan_id_fkey', 'parking_slots', 'floor_plans', ['floor_plan_id'], ['id'])
    
    op.create_index('ix_cafeteria_tables_floor', 'cafeteria_tables', ['floor_plan_id'], unique=False)
    op.create_foreign_key('cafeteria_tables_floor_plan_id_fkey', 'cafeteria_tables', 'floor_plans', ['floor_plan_id'], ['id'])
