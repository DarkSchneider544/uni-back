"""
Parking Management - Simple & Easy to Use!

Access Levels:
- SUPER_ADMIN, ADMIN, PARKING_MANAGER: Full access (manage slots, assign visitors)
- ALL OTHER USERS (Managers, Team Leads, Employees): Use parking service only

Simple Operations:
- POST /parking/allocate - Get a parking slot (auto-assigns)
- POST /parking/release - Release your parking slot
- GET /parking/my-slot - Check your current parking status
"""
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.models.parking import ParkingSlot, ParkingAllocation
from app.models.enums import ManagerType, UserRole, ParkingType, VehicleType, ParkingSlotStatus
from app.services.parking_service import ParkingService
from app.utils.response import create_response
from app.schemas.base import APIResponse

router = APIRouter()


# ============== Permission Helpers ==============

async def require_parking_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Only SUPER_ADMIN, ADMIN, or PARKING Manager can manage slots.
    """
    if current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        return current_user
    
    if current_user.role == UserRole.MANAGER and current_user.manager_type == ManagerType.PARKING:
        return current_user
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You don't have permission to manage parking"
    )


# ============== USER OPERATIONS (Everyone Can Use) ==============

@router.post("/allocate", response_model=APIResponse[dict])
async def allocate_parking(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    🅿️ Get a parking slot - just click the button!
    
    - Auto-assigns first available slot
    - Uses your vehicle info from profile
    - One parking per user at a time
    """
    service = ParkingService(db)
    
    # Check if user has vehicle info
    if not current_user.vehicle_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please update your profile with vehicle number before parking"
        )
    
    # Check if user already has active parking
    existing = await service.check_user_active_parking(current_user.user_code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active parking slot"
        )
    
    # Find first available slot
    query = select(ParkingSlot).where(
        ParkingSlot.parking_type == ParkingType.EMPLOYEE,
        ParkingSlot.status == ParkingSlotStatus.AVAILABLE,
        ParkingSlot.is_active == True
    ).limit(1)
    
    result = await db.execute(query)
    slot = result.scalar_one_or_none()
    
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No available parking slots"
        )
    
    # Create allocation
    allocation = ParkingAllocation(
        slot_id=slot.id,
        user_code=current_user.user_code,
        parking_type=ParkingType.EMPLOYEE,
        vehicle_number=current_user.vehicle_number,
        vehicle_type=current_user.vehicle_type or VehicleType.CAR,
        entry_time=datetime.now(timezone.utc),
        is_active=True
    )
    
    # Mark slot as occupied
    slot.status = ParkingSlotStatus.OCCUPIED
    
    db.add(allocation)
    await db.commit()
    await db.refresh(allocation)
    
    return create_response(
        data={
            "message": "Parking allocated successfully",
            "slot_code": slot.slot_code,
            "vehicle_number": current_user.vehicle_number,
            "vehicle_type": current_user.vehicle_type if current_user.vehicle_type else "car",
            "entry_time": allocation.entry_time.isoformat()
        },
        message="Parking allocated successfully"
    )


@router.post("/release", response_model=APIResponse[dict])
async def release_parking(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    🚗 Release your parking slot - just click the button!
    
    - Auto-finds your active parking
    - Calculates duration
    - Frees up the slot
    """
    service = ParkingService(db)
    
    # Find user's active parking
    allocation = await service.check_user_active_parking(current_user.user_code)
    if not allocation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active parking found"
        )
    
    # Get the slot
    slot = await service.get_slot_by_id(allocation.slot_id)
    
    # Record exit time
    exit_time = datetime.now(timezone.utc)
    duration_mins = int((exit_time - allocation.entry_time).total_seconds() / 60)
    if duration_mins < 1:
        duration_mins = 1  # Minimum 1 minute
    
    allocation.exit_time = exit_time
    allocation.is_active = False
    
    # Free up the slot
    if slot:
        slot.status = ParkingSlotStatus.AVAILABLE
    
    await db.commit()
    
    return create_response(
        data={
            "message": "Parking released successfully",
            "slot_code": slot.slot_code if slot else "UNKNOWN",
            "vehicle_number": allocation.vehicle_number,
            "entry_time": allocation.entry_time.isoformat(),
            "exit_time": exit_time.isoformat(),
            "duration_mins": duration_mins
        },
        message="Parking released successfully"
    )


@router.get("/my-slot", response_model=APIResponse[dict])
async def get_my_parking(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    📍 Check your current parking status.
    """
    service = ParkingService(db)
    allocation = await service.check_user_active_parking(current_user.user_code)
    
    if not allocation:
        return create_response(
            data={
                "has_active_parking": False,
                "slot": None,
                "vehicle": {
                    "vehicle_number": current_user.vehicle_number,
                    "vehicle_type": current_user.vehicle_type if current_user.vehicle_type else None
                },
                "entry_time": None
            },
            message="No active parking"
        )
    
    slot = await service.get_slot_by_id(allocation.slot_id)
    
    return create_response(
        data={
            "has_active_parking": True,
            "slot": {
                "id": str(slot.id) if slot else None,
                "slot_code": slot.slot_code if slot else "UNKNOWN"
            },
            "vehicle": {
                "vehicle_number": allocation.vehicle_number,
                "vehicle_type": allocation.vehicle_type.value if allocation.vehicle_type and hasattr(allocation.vehicle_type, 'value') else (allocation.vehicle_type or "car")
            },
            "entry_time": allocation.entry_time.isoformat()
        },
        message="Active parking found"
    )


# ============== ADMIN OPERATIONS (Parking Manager, Admin, Super Admin) ==============

@router.get("/slots/summary", response_model=APIResponse[dict])
async def get_slot_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    📊 Get parking slot statistics.
    """
    service = ParkingService(db)
    stats = await service.get_parking_stats()
    return create_response(
        data=stats,
        message="Parking statistics retrieved"
    )


@router.get("/slots/list", response_model=APIResponse[dict])
async def list_slots(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    📋 List all parking slots with occupant details.
    """
    service = ParkingService(db)
    
    # Build query
    query = select(ParkingSlot).where(ParkingSlot.is_active == True)
    
    if status_filter:
        try:
            status_enum = ParkingSlotStatus(status_filter.upper())
            query = query.where(ParkingSlot.status == status_enum)
        except ValueError:
            pass
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    slots = result.scalars().all()
    
    # Get total count
    count_query = select(ParkingSlot).where(ParkingSlot.is_active == True)
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())
    
    # Build response with occupant info
    slots_data = []
    for slot in slots:
        # Get current occupant if any
        alloc_query = select(ParkingAllocation).where(
            ParkingAllocation.slot_id == slot.id,
            ParkingAllocation.is_active == True
        )
        alloc_result = await db.execute(alloc_query)
        allocation = alloc_result.scalar_one_or_none()
        
        slot_info = {
            "id": str(slot.id),
            "slot_code": slot.slot_code,
            "status": slot.status.value,
            "created_at": slot.created_at.isoformat() if slot.created_at else None,
            "updated_at": slot.updated_at.isoformat() if slot.updated_at else None,
            "current_occupant": None,
            "user_email": None,
            "vehicle_number": None
        }
        
        if allocation:
            if allocation.visitor_name:
                slot_info["current_occupant"] = allocation.visitor_name
                slot_info["user_email"] = "Visitor"
            else:
                # Get user name
                from app.models.user import User as UserModel
                user_query = select(UserModel).where(UserModel.user_code == allocation.user_code)
                user_result = await db.execute(user_query)
                user = user_result.scalar_one_or_none()
                slot_info["current_occupant"] = f"{user.first_name} {user.last_name}" if user else allocation.user_code
                slot_info["user_email"] = user.email if user else None
            slot_info["vehicle_number"] = allocation.vehicle_number
        
        slots_data.append(slot_info)
    
    return create_response(
        data={"total": total, "slots": slots_data},
        message="Slots retrieved successfully"
    )


@router.post("/slots/create", response_model=APIResponse[dict])
async def create_slot(
    slot_code: str = Query(..., description="Unique slot code (e.g., A-01)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_parking_admin),
):
    """
    ➕ Create a new parking slot (Admin only).
    """
    # Check if slot code exists
    existing = await db.execute(
        select(ParkingSlot).where(ParkingSlot.slot_code == slot_code.upper())
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slot code already exists"
        )
    
    slot = ParkingSlot(
        slot_code=slot_code.upper(),
        slot_label=f"Parking Slot {slot_code.upper()}",
        parking_type=ParkingType.EMPLOYEE,
        status=ParkingSlotStatus.AVAILABLE,
        is_active=True,
        created_by_code=current_user.user_code
    )
    
    db.add(slot)
    await db.commit()
    await db.refresh(slot)
    
    return create_response(
        data={
            "id": str(slot.id),
            "slot_code": slot.slot_code,
            "status": slot.status.value,
            "created_at": slot.created_at.isoformat() if slot.created_at else None
        },
        message="Slot created successfully"
    )


@router.delete("/slots/delete/{slot_code}", response_model=APIResponse[dict])
async def delete_slot(
    slot_code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_parking_admin),
):
    """
    🗑️ Delete a parking slot (Admin only). Cannot delete occupied slots.
    """
    result = await db.execute(
        select(ParkingSlot).where(ParkingSlot.slot_code == slot_code.upper())
    )
    slot = result.scalar_one_or_none()
    
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot not found"
        )
    
    if slot.status == ParkingSlotStatus.OCCUPIED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete occupied slot"
        )
    
    await db.delete(slot)
    await db.commit()
    
    return create_response(
        data={"message": "Slot deleted successfully"},
        message="Slot deleted successfully"
    )


@router.post("/slots/change-status/{slot_code}", response_model=APIResponse[dict])
async def change_slot_status(
    slot_code: str,
    new_status: str = Query(..., description="AVAILABLE, OCCUPIED, or DISABLED"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_parking_admin),
):
    """
    🔄 Change slot status (Admin only).
    If changing from OCCUPIED to AVAILABLE, auto-releases parking.
    """
    result = await db.execute(
        select(ParkingSlot).where(ParkingSlot.slot_code == slot_code.upper())
    )
    slot = result.scalar_one_or_none()
    
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot not found"
        )
    
    try:
        status_enum = ParkingSlotStatus(new_status.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status. Use: AVAILABLE, OCCUPIED, or DISABLED"
        )
    
    # If changing from OCCUPIED to AVAILABLE, release the parking
    if slot.status == ParkingSlotStatus.OCCUPIED and status_enum == ParkingSlotStatus.AVAILABLE:
        alloc_query = select(ParkingAllocation).where(
            ParkingAllocation.slot_id == slot.id,
            ParkingAllocation.is_active == True
        )
        alloc_result = await db.execute(alloc_query)
        allocation = alloc_result.scalar_one_or_none()
        
        if allocation:
            allocation.exit_time = datetime.now(timezone.utc)
            allocation.is_active = False
    
    slot.status = status_enum
    await db.commit()
    
    return create_response(
        data={
            "message": f"Slot status changed to {new_status.upper()}",
            "slot_code": slot.slot_code,
            "status": slot.status.value
        },
        message=f"Slot status changed to {new_status.upper()}"
    )


@router.post("/slots/assign-visitor", response_model=APIResponse[dict])
async def assign_visitor(
    visitor_name: str = Query(..., description="Visitor's name"),
    vehicle_number: str = Query(..., description="Vehicle number"),
    vehicle_type: str = Query("CAR", description="CAR or BIKE"),
    slot_code: str = Query(..., description="Slot code to assign"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_parking_admin),
):
    """
    👤 Assign a slot to a visitor (Admin only).
    """
    # Find the slot
    result = await db.execute(
        select(ParkingSlot).where(ParkingSlot.slot_code == slot_code.upper())
    )
    slot = result.scalar_one_or_none()
    
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot not found"
        )
    
    if slot.status != ParkingSlotStatus.AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Slot is not available"
        )
    
    # Create visitor allocation
    try:
        vtype = VehicleType(vehicle_type.upper())
    except ValueError:
        vtype = VehicleType.CAR
    
    allocation = ParkingAllocation(
        slot_id=slot.id,
        parking_type=ParkingType.VISITOR,
        visitor_name=visitor_name,
        vehicle_number=vehicle_number.upper(),
        vehicle_type=vtype,
        entry_time=datetime.now(timezone.utc),
        is_active=True
    )
    
    slot.status = ParkingSlotStatus.OCCUPIED
    
    db.add(allocation)
    await db.commit()
    
    return create_response(
        data={
            "message": "Visitor assigned to slot successfully",
            "slot_code": slot.slot_code,
            "visitor_name": visitor_name,
            "vehicle_number": vehicle_number.upper(),
            "vehicle_type": vtype.value,
            "entry_time": allocation.entry_time.isoformat(),
            "status": "OCCUPIED"
        },
        message="Visitor assigned to slot successfully"
    )


# ============== PARKING LOGS (Admin Only) ==============

@router.get("/logs/list", response_model=APIResponse[dict])
async def list_parking_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_parking_admin),
):
    """
    📜 Get parking history logs (Admin only).
    """
    query = select(ParkingAllocation)
    
    if is_active is not None:
        query = query.where(ParkingAllocation.is_active == is_active)
    
    query = query.order_by(ParkingAllocation.entry_time.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    allocations = result.scalars().all()
    
    # Get total
    count_query = select(ParkingAllocation)
    if is_active is not None:
        count_query = count_query.where(ParkingAllocation.is_active == is_active)
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())
    
    logs = []
    for alloc in allocations:
        # Get slot info
        slot = await db.execute(select(ParkingSlot).where(ParkingSlot.id == alloc.slot_id))
        slot_obj = slot.scalar_one_or_none()
        
        # Get user info if employee
        user_name = alloc.visitor_name
        if alloc.user_code:
            from app.models.user import User as UserModel
            user_result = await db.execute(select(UserModel).where(UserModel.user_code == alloc.user_code))
            user = user_result.scalar_one_or_none()
            user_name = f"{user.first_name} {user.last_name}" if user else alloc.user_code
        
        # Calculate duration
        duration_mins = None
        if alloc.exit_time and alloc.entry_time:
            duration_mins = int((alloc.exit_time - alloc.entry_time).total_seconds() / 60)
        
        logs.append({
            "id": str(alloc.id),
            "user_name": user_name,
            "slot_code": slot_obj.slot_code if slot_obj else "UNKNOWN",
            "vehicle_number": alloc.vehicle_number,
            "entry_time": alloc.entry_time.isoformat() if alloc.entry_time else None,
            "exit_time": alloc.exit_time.isoformat() if alloc.exit_time else None,
            "duration_mins": duration_mins,
            "is_active": alloc.is_active
        })
    
    return create_response(
        data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "logs": logs
        },
        message="Parking logs retrieved"
    )
