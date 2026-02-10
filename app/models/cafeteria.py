from sqlalchemy import (
    Column, String, DateTime, Date, ForeignKey, Text, Index, Enum, Time, Integer, Boolean, event
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import random
import string

from .base import Base, TimestampMixin
from .enums import BookingStatus


def generate_table_code() -> str:
    """Generate a unique cafeteria table code. Format: TBL-XXXX"""
    digits = ''.join(random.choices(string.digits, k=4))
    return f"TBL-{digits}"


class CafeteriaTable(Base, TimestampMixin):
    """
    Cafeteria table definition - managed by CAFETERIA Manager.
    Codes are auto-generated. Simplified without location fields.
    """
    __tablename__ = "cafeteria_tables"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Table identification - auto-generated
    table_code = Column(String(20), unique=True, nullable=False, index=True)
    table_label = Column(String(50), nullable=False)
    
    # Table properties
    capacity = Column(Integer, nullable=False, default=4)
    table_type = Column(String(50), default="regular")  # regular, high_top, booth
    
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Created by - using user_code
    created_by_code = Column(String(10), ForeignKey("users.user_code"), nullable=False)
    
    # Relationships
    bookings = relationship("CafeteriaTableBooking", back_populates="table")
    created_by = relationship("User", foreign_keys=[created_by_code], primaryjoin="CafeteriaTable.created_by_code == User.user_code")
    
    __table_args__ = (
        Index("ix_cafeteria_tables_capacity", "capacity"),
    )


# Auto-generate table_code before insert
@event.listens_for(CafeteriaTable, 'before_insert')
def generate_table_code_before_insert(mapper, connection, target):
    """Auto-generate a unique cafeteria table code before inserting."""
    if not target.table_code:
        target.table_code = generate_table_code()


class CafeteriaTableBooking(Base, TimestampMixin):
    """
    Cafeteria table booking records.
    Uses user_code instead of user_id.
    """
    __tablename__ = "cafeteria_table_bookings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Table reference
    table_id = Column(UUID(as_uuid=True), ForeignKey("cafeteria_tables.id"), nullable=False)
    
    # User reference - using user_code
    user_code = Column(String(10), ForeignKey("users.user_code"), nullable=False)
    
    # Booking details
    booking_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    # Guest info
    guest_count = Column(Integer, default=1)
    guest_names = Column(Text, nullable=True)  # Comma-separated if multiple guests
    
    # Status
    status = Column(Enum(BookingStatus), default=BookingStatus.CONFIRMED)
    
    notes = Column(Text, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    table = relationship("CafeteriaTable", back_populates="bookings")
    user = relationship("User", foreign_keys=[user_code], primaryjoin="CafeteriaTableBooking.user_code == User.user_code")
    
    __table_args__ = (
        Index("ix_cafeteria_booking_date", "table_id", "booking_date"),
        Index("ix_cafeteria_booking_user", "user_code", "booking_date"),
        Index("ix_cafeteria_booking_status", "status"),
    )
