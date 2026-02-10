from sqlalchemy import (
    Column, String, Boolean, DateTime, Date, ForeignKey, Text, Index, Enum, Time, Integer, event
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import random
import string

from .base import Base, TimestampMixin
from .enums import BookingStatus, DeskStatus


def generate_desk_code() -> str:
    """Generate a unique desk code. Format: DSK-XXXX"""
    digits = ''.join(random.choices(string.digits, k=4))
    return f"DSK-{digits}"


def generate_room_code() -> str:
    """Generate a unique conference room code. Format: CNF-XXXX"""
    digits = ''.join(random.choices(string.digits, k=4))
    return f"CNF-{digits}"


class Desk(Base, TimestampMixin):
    """
    Desk definition - managed by DESK_CONFERENCE Manager.
    Codes are auto-generated. Simplified without location fields.
    """
    __tablename__ = "desks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Desk identification - auto-generated
    desk_code = Column(String(20), unique=True, nullable=False, index=True)
    desk_label = Column(String(50), nullable=False)
    
    # Desk properties
    status = Column(Enum(DeskStatus), default=DeskStatus.AVAILABLE)
    has_monitor = Column(Boolean, default=True)
    has_docking_station = Column(Boolean, default=False)
    
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Created by - using user_code
    created_by_code = Column(String(10), ForeignKey("users.user_code"), nullable=False)
    
    # Relationships
    bookings = relationship("DeskBooking", back_populates="desk")
    created_by = relationship("User", foreign_keys=[created_by_code], primaryjoin="Desk.created_by_code == User.user_code")
    
    __table_args__ = (
        Index("ix_desks_status", "status"),
    )


# Auto-generate desk_code before insert
@event.listens_for(Desk, 'before_insert')
def generate_desk_code_before_insert(mapper, connection, target):
    """Auto-generate a unique desk code before inserting."""
    if not target.desk_code:
        target.desk_code = generate_desk_code()


class DeskBooking(Base, TimestampMixin):
    """
    Desk booking records.
    Uses user_code instead of user_id.
    Supports time-based booking within business hours (9 AM - 7 PM).
    """
    __tablename__ = "desk_bookings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Desk reference
    desk_id = Column(UUID(as_uuid=True), ForeignKey("desks.id"), nullable=False)
    
    # User reference - using user_code
    user_code = Column(String(10), ForeignKey("users.user_code"), nullable=False)
    
    # Booking details
    booking_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)  # Business hours: 9:00 - 19:00
    end_time = Column(Time, nullable=False)
    
    # Status
    status = Column(Enum(BookingStatus), default=BookingStatus.CONFIRMED)
    
    # Check-in/out tracking
    checked_in_at = Column(DateTime(timezone=True), nullable=True)
    checked_out_at = Column(DateTime(timezone=True), nullable=True)
    
    notes = Column(Text, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    desk = relationship("Desk", back_populates="bookings")
    user = relationship("User", foreign_keys=[user_code], primaryjoin="DeskBooking.user_code == User.user_code")
    
    __table_args__ = (
        Index("ix_desk_booking_date", "desk_id", "booking_date"),
        Index("ix_desk_booking_user", "user_code", "booking_date"),
        Index("ix_desk_booking_status", "status"),
    )


class ConferenceRoom(Base, TimestampMixin):
    """
    Conference room definition - managed by DESK_CONFERENCE Manager.
    Codes are auto-generated. Simplified with only essential fields.
    """
    __tablename__ = "conference_rooms"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Room identification - auto-generated
    room_code = Column(String(20), unique=True, nullable=False, index=True)
    room_label = Column(String(100), nullable=False)
    
    # Room properties - only essential ones
    capacity = Column(Integer, nullable=False)
    has_projector = Column(Boolean, default=False)
    has_whiteboard = Column(Boolean, default=True)
    has_video_conferencing = Column(Boolean, default=False)
    
    status = Column(Enum(DeskStatus), default=DeskStatus.AVAILABLE)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Created by - using user_code
    created_by_code = Column(String(10), ForeignKey("users.user_code"), nullable=False)
    
    # Relationships
    bookings = relationship("ConferenceRoomBooking", back_populates="room")
    created_by = relationship("User", foreign_keys=[created_by_code], primaryjoin="ConferenceRoom.created_by_code == User.user_code")
    
    __table_args__ = (
        Index("ix_conference_rooms_capacity", "capacity"),
    )


# Auto-generate room_code before insert
@event.listens_for(ConferenceRoom, 'before_insert')
def generate_room_code_before_insert(mapper, connection, target):
    """Auto-generate a unique conference room code before inserting."""
    if not target.room_code:
        target.room_code = generate_room_code()


class ConferenceRoomBooking(Base, TimestampMixin):
    """
    Conference room booking records.
    Uses user_code instead of user_id.
    """
    __tablename__ = "conference_room_bookings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Room reference
    room_id = Column(UUID(as_uuid=True), ForeignKey("conference_rooms.id"), nullable=False)
    
    # User reference - using user_code
    user_code = Column(String(10), ForeignKey("users.user_code"), nullable=False)
    
    # Booking details
    booking_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    # Meeting info
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    attendees_count = Column(Integer, nullable=False)
    
    # Status
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING)
    
    notes = Column(Text, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    room = relationship("ConferenceRoom", back_populates="bookings")
    user = relationship("User", foreign_keys=[user_code], primaryjoin="ConferenceRoomBooking.user_code == User.user_code")
    
    __table_args__ = (
        Index("ix_conf_booking_date", "room_id", "booking_date"),
        Index("ix_conf_booking_user", "user_code", "booking_date"),
        Index("ix_conf_booking_status", "status"),
    )
