from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
import re

from ..models.enums import ParkingType, ParkingSlotStatus, VehicleType


# ==================== Parking Slot Schemas ====================

class ParkingSlotBase(BaseModel):
    """Base parking slot schema - simplified without location fields."""
    slot_label: str = Field(..., min_length=1, max_length=50)
    parking_type: ParkingType = ParkingType.EMPLOYEE
    vehicle_type: Optional[VehicleType] = None
    notes: Optional[str] = Field(None, max_length=500)


class ParkingSlotCreate(ParkingSlotBase):
    """
    Parking slot creation schema - used by PARKING Manager.
    slot_code is auto-generated in the database.
    """
    pass


class ParkingSlotUpdate(BaseModel):
    """Parking slot update schema."""
    slot_label: Optional[str] = Field(None, min_length=1, max_length=50)
    parking_type: Optional[ParkingType] = None
    vehicle_type: Optional[VehicleType] = None
    status: Optional[ParkingSlotStatus] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=500)


class ParkingSlotResponse(BaseModel):
    """Parking slot response schema with auto-generated slot_code."""
    id: UUID
    slot_code: str  # Auto-generated: PKG-XXXX
    slot_label: str
    parking_type: ParkingType
    vehicle_type: Optional[VehicleType] = None
    status: ParkingSlotStatus
    is_active: bool
    notes: Optional[str] = None
    created_by_code: str
    created_at: datetime
    updated_at: datetime
    current_allocation: Optional["ParkingAllocationResponse"] = None
    
    class Config:
        from_attributes = True


class ParkingSlotListResponse(BaseModel):
    """Parking slot list response schema."""
    slots: List[ParkingSlotResponse]
    total: int
    available: int
    occupied: int


# ==================== Parking Allocation Schemas ====================

class ParkingAllocationBase(BaseModel):
    """
    Base parking allocation schema.
    Available to: EMPLOYEE, TEAM_LEAD, MANAGER roles
    """
    vehicle_number: str = Field(..., min_length=4, max_length=20)
    vehicle_type: VehicleType = VehicleType.CAR
    notes: Optional[str] = Field(None, max_length=500)


class ParkingAllocationCreate(ParkingAllocationBase):
    """
    Parking allocation creation schema for employees.
    Employee books their own parking.
    """
    slot_id: UUID
    
    @field_validator('vehicle_number')
    @classmethod
    def validate_vehicle_number(cls, v):
        if not re.match(r'^[A-Z0-9\s-]{4,20}$', v.upper()):
            raise ValueError('Invalid vehicle number format')
        return v.upper()


class VisitorParkingCreate(BaseModel):
    """
    Schema for Parking Manager to assign visitor parking.
    Only PARKING manager can create visitor parking.
    """
    visitor_name: str = Field(..., min_length=2, max_length=100)
    visitor_phone: Optional[str] = Field(None, max_length=20)
    visitor_company: Optional[str] = Field(None, max_length=100)
    vehicle_number: Optional[str] = Field(None, max_length=20)
    vehicle_type: VehicleType = VehicleType.CAR
    notes: Optional[str] = Field(None, max_length=500)
    host_user_code: Optional[str] = Field(None, description="User code of the employee hosting the visitor")
    slot_id: Optional[UUID] = None  # If not provided, auto-assigns an available visitor slot
    
    @field_validator('visitor_phone')
    @classmethod
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[\d\s-]{10,20}$', v):
            raise ValueError('Invalid phone number format')
        return v


class ParkingAllocationUpdate(BaseModel):
    """Parking allocation update schema."""
    vehicle_number: Optional[str] = None
    vehicle_type: Optional[VehicleType] = None
    notes: Optional[str] = None


class ParkingCheckInOut(BaseModel):
    """Parking check-in/check-out schema."""
    allocation_id: UUID
    action: str = Field(..., pattern="^(check_in|check_out)$")


class ParkingAllocationResponse(BaseModel):
    """Parking allocation response schema."""
    id: UUID
    slot_id: UUID
    slot_code: str
    slot_label: str
    parking_type: ParkingType
    user_code: Optional[str] = None
    user_name: Optional[str] = None
    visitor_name: Optional[str] = None
    visitor_phone: Optional[str] = None
    visitor_company: Optional[str] = None
    vehicle_number: Optional[str] = None
    vehicle_type: VehicleType
    entry_time: datetime
    expected_exit_time: Optional[datetime] = None
    exit_time: Optional[datetime] = None
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ParkingAllocationListResponse(BaseModel):
    """Parking allocation list response schema."""
    allocations: List[ParkingAllocationResponse]
    total: int
    page: int
    page_size: int


class MyParkingResponse(BaseModel):
    """User's current parking allocation response."""
    has_parking: bool
    allocation: Optional[ParkingAllocationResponse] = None
    default_vehicle_number: Optional[str] = None
    default_vehicle_type: Optional[VehicleType] = None


# ==================== Parking History Schemas ====================

class ParkingHistoryResponse(BaseModel):
    """Parking history response schema."""
    id: UUID
    allocation_id: UUID
    slot_id: UUID
    slot_code: str
    parking_type: ParkingType
    user_code: Optional[str] = None
    user_name: Optional[str] = None
    visitor_name: Optional[str] = None
    vehicle_number: Optional[str] = None
    vehicle_type: VehicleType
    entry_time: datetime
    exit_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ParkingHistoryListResponse(BaseModel):
    """Parking history list response schema."""
    history: List[ParkingHistoryResponse]
    total: int
    page: int
    page_size: int


# ==================== Parking Statistics ====================

class ParkingStatistics(BaseModel):
    """Parking statistics for dashboard."""
    total_slots: int
    employee_slots: int
    visitor_slots: int
    occupied_slots: int
    available_slots: int
    occupancy_percentage: float
    today_check_ins: int
    today_check_outs: int


# Forward reference resolution
ParkingSlotResponse.model_rebuild()
