"""desk_booking_date_range

Revision ID: 439084bc84ea
Revises: 67dac324c4c4
Create Date: 2026-02-11 14:35:01.529768

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '439084bc84ea'
down_revision: Union[str, None] = '67dac324c4c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new date columns (initially nullable for data migration)
    op.add_column('desk_bookings', sa.Column('start_date', sa.Date(), nullable=True))
    op.add_column('desk_bookings', sa.Column('end_date', sa.Date(), nullable=True))
    
    # Migrate existing data: copy booking_date to start_date and end_date
    op.execute("UPDATE desk_bookings SET start_date = booking_date, end_date = booking_date")
    
    # Now make the columns non-nullable
    op.alter_column('desk_bookings', 'start_date', nullable=False)
    op.alter_column('desk_bookings', 'end_date', nullable=False)
    
    # Update indexes
    op.drop_index('ix_desk_booking_date', table_name='desk_bookings')
    op.create_index('ix_desk_booking_date', 'desk_bookings', ['desk_id', 'start_date', 'end_date'], unique=False)
    op.drop_index('ix_desk_booking_user', table_name='desk_bookings')
    op.create_index('ix_desk_booking_user', 'desk_bookings', ['user_code', 'start_date'], unique=False)
    
    # Drop old columns
    op.drop_column('desk_bookings', 'booking_date')
    op.drop_column('desk_bookings', 'start_time')
    op.drop_column('desk_bookings', 'end_time')


def downgrade() -> None:
    # Add old columns back
    op.add_column('desk_bookings', sa.Column('booking_date', sa.DATE(), nullable=True))
    op.add_column('desk_bookings', sa.Column('start_time', postgresql.TIME(), nullable=True))
    op.add_column('desk_bookings', sa.Column('end_time', postgresql.TIME(), nullable=True))
    
    # Migrate data back: use start_date as booking_date, default times
    op.execute("UPDATE desk_bookings SET booking_date = start_date, start_time = '09:00:00', end_time = '18:00:00'")
    
    # Make columns non-nullable
    op.alter_column('desk_bookings', 'booking_date', nullable=False)
    op.alter_column('desk_bookings', 'start_time', nullable=False)
    op.alter_column('desk_bookings', 'end_time', nullable=False)
    
    # Restore indexes
    op.drop_index('ix_desk_booking_user', table_name='desk_bookings')
    op.create_index('ix_desk_booking_user', 'desk_bookings', ['user_code', 'booking_date'], unique=False)
    op.drop_index('ix_desk_booking_date', table_name='desk_bookings')
    op.create_index('ix_desk_booking_date', 'desk_bookings', ['desk_id', 'booking_date'], unique=False)
    
    # Drop new columns
    op.drop_column('desk_bookings', 'end_date')
    op.drop_column('desk_bookings', 'start_date')
    op.drop_column('desk_bookings', 'start_date')
    op.create_index('ix_conference_rooms_created_by', 'conference_rooms', ['created_by_code'], unique=False)
    op.alter_column('conference_rooms', 'created_by_code',
               existing_type=sa.VARCHAR(length=10),
               nullable=True)
    op.create_index('ix_cafeteria_tables_created_by', 'cafeteria_tables', ['created_by_code'], unique=False)
    op.alter_column('cafeteria_tables', 'created_by_code',
               existing_type=sa.VARCHAR(length=10),
               nullable=True)
    op.drop_index('ix_cafeteria_booking_user', table_name='cafeteria_table_bookings')
    op.drop_index('ix_cafeteria_booking_status', table_name='cafeteria_table_bookings')
    op.drop_index('ix_cafeteria_booking_date', table_name='cafeteria_table_bookings')
    op.create_index('ix_table_booking_user', 'cafeteria_table_bookings', ['user_code', 'booking_date'], unique=False)
    op.create_index('ix_table_booking_status', 'cafeteria_table_bookings', ['status'], unique=False)
    op.create_index('ix_table_booking_date', 'cafeteria_table_bookings', ['table_id', 'booking_date'], unique=False)
    # ### end Alembic commands ###
