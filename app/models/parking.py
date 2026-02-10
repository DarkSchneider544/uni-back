from sqlalchemy import (
    Column, String, Boolean, DateTime, ForeignKey, Text, Index, Enum, Integer, event
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import random
import string

from .base import Base, TimestampMixin
from .enums import ParkingType, ParkingSlotStatus, VehicleType


def generate_slot_code() -> str:
    """Generate a unique parking slot code. Format: PKG-XXXX"""
    digits = ''.join(random.choices(string.digits, k=4))
    return f"PKG-{digits}"


class ParkingSlot(Base, TimestampMixin):
    """
    Parking slot definition - managed by PARKING Manager.
    Codes are auto-generated. Simplified without location fields.
    """
    __tablename__ = "parking_slots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Slot identification - auto-generated
    slot_code = Column(String(20), unique=True, nullable=False, index=True)
    slot_label = Column(String(50), nullable=False)
    
    # Slot properties
    parking_type = Column(Enum(ParkingType), nullable=False, default=ParkingType.EMPLOYEE)
    vehicle_type = Column(Enum(VehicleType), nullable=True)  # car, bike - if specific
    status = Column(Enum(ParkingSlotStatus), default=ParkingSlotStatus.AVAILABLE)
    
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Created by - using user_code
    created_by_code = Column(String(10), ForeignKey("users.user_code"), nullable=False)
    
    # Relationships
    allocations = relationship("ParkingAllocation", back_populates="slot")
    created_by = relationship("User", foreign_keys=[created_by_code], primaryjoin="ParkingSlot.created_by_code == User.user_code")
    
    __table_args__ = (
        Index("ix_parking_slots_status", "status"),
        Index("ix_parking_slots_type", "parking_type"),
    )


# Auto-generate slot_code before insert
@event.listens_for(ParkingSlot, 'before_insert')
def generate_slot_code_before_insert(mapper, connection, target):
    """Auto-generate a unique parking slot code before inserting."""
    if not target.slot_code:
        target.slot_code = generate_slot_code()


class ParkingAllocation(Base, TimestampMixin):
    """
    Current parking allocations (who is parked where).
    Uses user_code instead of user_id.
    """
    __tablename__ = "parking_allocations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Slot reference
    slot_id = Column(UUID(as_uuid=True), ForeignKey("parking_slots.id"), nullable=False)
    
    # For employee parking - use user_code
    user_code = Column(String(10), ForeignKey("users.user_code"), nullable=True)
    
    # For visitor parking
    parking_type = Column(Enum(ParkingType), nullable=False, default=ParkingType.EMPLOYEE)
    visitor_name = Column(String(200), nullable=True)
    visitor_phone = Column(String(20), nullable=True)
    visitor_company = Column(String(200), nullable=True)
    
    # Vehicle info
    vehicle_number = Column(String(50), nullable=False)
    vehicle_type = Column(Enum(VehicleType), nullable=False)
    
    # Timing
    entry_time = Column(DateTime(timezone=True), nullable=False)
    expected_exit_time = Column(DateTime(timezone=True), nullable=True)
    exit_time = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    slot = relationship("ParkingSlot", back_populates="allocations")
    user = relationship("User", foreign_keys=[user_code], primaryjoin="ParkingAllocation.user_code == User.user_code")
    
    __table_args__ = (
        Index("ix_parking_allocation_user", "user_code", "is_active"),
        Index("ix_parking_allocation_slot", "slot_id", "is_active"),
        Index("ix_parking_allocation_entry", "entry_time"),
    )


class ParkingHistory(Base, TimestampMixin):
    """
    Historical record of all parking allocations.
    Created when a parking allocation is released.
    """
    __tablename__ = "parking_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Original allocation reference
    allocation_id = Column(UUID(as_uuid=True), nullable=False)
    slot_id = Column(UUID(as_uuid=True), nullable=False)
    slot_code = Column(String(20), nullable=False)
    
    # Parking type
    parking_type = Column(Enum(ParkingType), nullable=False)
    
    # User/Visitor info
    user_code = Column(String(10), nullable=True)
    visitor_name = Column(String(200), nullable=True)
    
    # Vehicle info
    vehicle_number = Column(String(50), nullable=True)
    vehicle_type = Column(Enum(VehicleType), nullable=False)
    
    # Timing
    entry_time = Column(DateTime(timezone=True), nullable=False)
    exit_time = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    __table_args__ = (
        Index("ix_parking_history_user", "user_code"),
        Index("ix_parking_history_entry", "entry_time"),
    )
