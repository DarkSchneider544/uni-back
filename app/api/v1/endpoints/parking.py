"""
Parking management endpoints.
Allows parking managers to create, update, and delete parking slots.
Handles parking allocation and history.
Simplified API without location fields.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.models.enums import ManagerType, UserRole, ParkingType
from app.schemas.parking import (
    ParkingSlotCreate,
    ParkingSlotUpdate,
    ParkingSlotResponse,
    ParkingAllocationCreate,
    ParkingAllocationResponse,
    ParkingHistoryResponse,
    VisitorParkingCreate,
)
from app.services.parking_service import ParkingService
from app.utils.response import create_response

router = APIRouter()


async def require_parking_manager(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency that ensures the current user has parking management permissions.
    Allows SUPER_ADMIN, ADMIN, or users with PARKING manager type.
    """
    if current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        return current_user
    
    if current_user.role == UserRole.MANAGER and current_user.manager_type == ManagerType.PARKING:
        return current_user
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You don't have permission to manage parking slots"
    )


# ============== Parking Slot Management (Manager Only) ==============

@router.post("/slots", response_model=dict)
async def create_parking_slot(
    slot_data: ParkingSlotCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_parking_manager),
):
    """
    Create a new parking slot (Manager only).
    Slot code will be auto-generated (PKG-XXXX).
    """
    service = ParkingService(db)
    slot, error = await service.create_slot(slot_data, current_user)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return create_response(
        data=ParkingSlotResponse.model_validate(slot),
        message="Parking slot created successfully"
    )


@router.get("/slots", response_model=dict)
async def get_all_parking_slots(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    parking_type: Optional[ParkingType] = None,
    is_active: Optional[bool] = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all parking slots with optional filters."""
    service = ParkingService(db)
    slots, total = await service.list_slots(
        parking_type=parking_type,
        is_active=is_active,
        page=page,
        page_size=page_size
    )
    return create_response(
        data=[ParkingSlotResponse.model_validate(s) for s in slots],
        message="Parking slots retrieved successfully"
    )


@router.get("/slots/{slot_id}", response_model=dict)
async def get_parking_slot(
    slot_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific parking slot by ID."""
    service = ParkingService(db)
    slot = await service.get_slot_by_id(slot_id)
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parking slot not found"
        )
    return create_response(
        data=ParkingSlotResponse.model_validate(slot),
        message="Parking slot retrieved successfully"
    )


@router.put("/slots/{slot_id}", response_model=dict)
async def update_parking_slot(
    slot_id: UUID,
    slot_data: ParkingSlotUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_parking_manager),
):
    """Update a parking slot (Manager only)."""
    service = ParkingService(db)
    slot, error = await service.update_slot(slot_id, slot_data, current_user)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return create_response(
        data=ParkingSlotResponse.model_validate(slot),
        message="Parking slot updated successfully"
    )


@router.delete("/slots/{slot_id}", response_model=dict)
async def delete_parking_slot(
    slot_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_parking_manager),
):
    """Delete a parking slot (Manager only)."""
    service = ParkingService(db)
    success, error = await service.delete_slot(slot_id, current_user)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return create_response(
        data={"deleted": True},
        message="Parking slot deleted successfully"
    )


# ============== Parking Allocation (All Users) ==============

@router.post("/allocations", response_model=dict)
async def create_parking_allocation(
    allocation_data: ParkingAllocationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a parking allocation (employee parks their car).
    Available to all authenticated users.
    """
    service = ParkingService(db)
    allocation, error = await service.create_allocation(allocation_data, current_user)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    
    # Build response with slot details
    response_data = {
        "id": allocation.id,
        "slot_id": allocation.slot_id,
        "slot_code": allocation.slot.slot_code,
        "slot_label": allocation.slot.slot_label,
        "parking_type": allocation.parking_type,
        "user_code": allocation.user_code,
        "vehicle_number": allocation.vehicle_number,
        "vehicle_type": allocation.vehicle_type,
        "entry_time": allocation.entry_time,
        "is_active": allocation.is_active,
        "notes": allocation.notes,
        "created_at": allocation.created_at,
        "updated_at": allocation.updated_at
    }
    
    return create_response(
        data=response_data,
        message="Parking allocation created successfully"
    )


@router.get("/allocations", response_model=dict)
async def get_parking_allocations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    parking_type: Optional[ParkingType] = None,
    is_active: Optional[bool] = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get parking allocations with optional filters."""
    service = ParkingService(db)
    allocations, total = await service.list_allocations(
        parking_type=parking_type,
        is_active=is_active,
        page=page,
        page_size=page_size
    )
    
    # Build response with slot details
    response_data = []
    for allocation in allocations:
        response_data.append({
            "id": allocation.id,
            "slot_id": allocation.slot_id,
            "slot_code": allocation.slot.slot_code,
            "slot_label": allocation.slot.slot_label,
            "parking_type": allocation.parking_type,
            "user_code": allocation.user_code,
            "visitor_name": allocation.visitor_name,
            "visitor_phone": allocation.visitor_phone,
            "visitor_company": allocation.visitor_company,
            "vehicle_number": allocation.vehicle_number,
            "vehicle_type": allocation.vehicle_type,
            "entry_time": allocation.entry_time,
            "exit_time": allocation.exit_time,
            "is_active": allocation.is_active,
            "notes": allocation.notes,
            "created_at": allocation.created_at,
            "updated_at": allocation.updated_at
        })
    
    return create_response(
        data=response_data,
        message="Parking allocations retrieved successfully"
    )


@router.get("/allocations/my", response_model=dict)
async def get_my_parking(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's active parking allocation."""
    service = ParkingService(db)
    allocation = await service.check_user_active_parking(current_user.user_code)
    
    if not allocation:
        return create_response(
            data={"has_parking": False, "allocation": None},
            message="No active parking allocation"
        )
    
    # Get slot details
    slot = await service.get_slot_by_id(allocation.slot_id)
    
    response_data = {
        "has_parking": True,
        "allocation": {
            "id": allocation.id,
            "slot_id": allocation.slot_id,
            "slot_code": slot.slot_code if slot else "UNKNOWN",
            "slot_label": slot.slot_label if slot else "UNKNOWN",
            "parking_type": allocation.parking_type,
            "user_code": allocation.user_code,
            "vehicle_number": allocation.vehicle_number,
            "vehicle_type": allocation.vehicle_type,
            "entry_time": allocation.entry_time,
            "is_active": allocation.is_active,
            "notes": allocation.notes,
            "created_at": allocation.created_at,
            "updated_at": allocation.updated_at
        }
    }
    
    return create_response(
        data=response_data,
        message="My parking allocation retrieved successfully"
    )


@router.post("/allocations/{allocation_id}/exit", response_model=dict)
async def record_parking_exit(
    allocation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record parking exit (release the slot)."""
    service = ParkingService(db)
    allocation, error = await service.record_exit(allocation_id, current_user)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    
    return create_response(
        data={"exited": True, "exit_time": allocation.exit_time},
        message="Parking exit recorded successfully"
    )


# ============== Visitor Parking (Manager Only) ==============

@router.post("/visitors", response_model=dict)
async def assign_visitor_parking(
    visitor_data: VisitorParkingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_parking_manager),
):
    """
    Assign a parking slot to a visitor (Manager only).
    If slot_id is not provided, auto-assigns an available visitor slot.
    """
    service = ParkingService(db)
    allocation, error = await service.assign_visitor_slot(visitor_data, current_user)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    
    # Get slot details
    slot = await service.get_slot_by_id(allocation.slot_id)
    
    response_data = {
        "id": allocation.id,
        "slot_id": allocation.slot_id,
        "slot_code": slot.slot_code if slot else "UNKNOWN",
        "slot_label": slot.slot_label if slot else "UNKNOWN",
        "parking_type": allocation.parking_type,
        "visitor_name": allocation.visitor_name,
        "visitor_phone": allocation.visitor_phone,
        "visitor_company": allocation.visitor_company,
        "vehicle_number": allocation.vehicle_number,
        "vehicle_type": allocation.vehicle_type,
        "entry_time": allocation.entry_time,
        "is_active": allocation.is_active,
        "notes": allocation.notes,
        "created_at": allocation.created_at,
        "updated_at": allocation.updated_at
    }
    
    return create_response(
        data=response_data,
        message="Visitor parking assigned successfully"
    )


@router.get("/visitors", response_model=dict)
async def get_visitor_allocations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get visitor parking allocations."""
    service = ParkingService(db)
    allocations, total = await service.list_visitor_allocations(
        is_active=is_active,
        page=page,
        page_size=page_size
    )
    
    # Build response with slot details
    response_data = []
    for allocation in allocations:
        response_data.append({
            "id": allocation.id,
            "slot_id": allocation.slot_id,
            "slot_code": allocation.slot.slot_code,
            "slot_label": allocation.slot.slot_label,
            "parking_type": allocation.parking_type,
            "visitor_name": allocation.visitor_name,
            "visitor_phone": allocation.visitor_phone,
            "visitor_company": allocation.visitor_company,
            "vehicle_number": allocation.vehicle_number,
            "vehicle_type": allocation.vehicle_type,
            "entry_time": allocation.entry_time,
            "exit_time": allocation.exit_time,
            "is_active": allocation.is_active,
            "notes": allocation.notes,
            "created_at": allocation.created_at,
            "updated_at": allocation.updated_at
        })
    
    return create_response(
        data=response_data,
        message="Visitor parking allocations retrieved successfully"
    )


# ============== Parking Stats ==============

@router.get("/stats", response_model=dict)
async def get_parking_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get parking statistics."""
    service = ParkingService(db)
    stats = await service.get_parking_stats()
    return create_response(
        data=stats,
        message="Parking statistics retrieved successfully"
    )
