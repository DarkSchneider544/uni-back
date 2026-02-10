"""
Cafeteria management endpoints.
Allows cafeteria managers to create, update, and delete tables.
Handles table bookings.
Simplified API without location fields.
"""
from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.models.enums import ManagerType, UserRole
from app.schemas.cafeteria import (
    CafeteriaTableCreate,
    CafeteriaTableUpdate,
    CafeteriaTableResponse,
    CafeteriaBookingCreate,
    CafeteriaBookingUpdate,
    CafeteriaBookingResponse,
)
from app.services.cafeteria_service import CafeteriaService
from app.utils.response import create_response

router = APIRouter()


async def require_cafeteria_manager(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency that ensures the current user has cafeteria management permissions.
    Allows SUPER_ADMIN, ADMIN, or users with CAFETERIA manager type.
    """
    if current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
        return current_user
    
    if current_user.role == UserRole.MANAGER and current_user.manager_type == ManagerType.CAFETERIA:
        return current_user
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You don't have permission to manage cafeteria tables"
    )


# ============== Cafeteria Table Management (Manager Only) ==============

@router.post("/tables", response_model=dict)
async def create_cafeteria_table(
    table_data: CafeteriaTableCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_cafeteria_manager),
):
    """
    Create a new cafeteria table (Manager only).
    Table code will be auto-generated (TBL-XXXX).
    """
    service = CafeteriaService(db)
    table, error = await service.create_table(table_data, current_user)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return create_response(
        data=CafeteriaTableResponse.model_validate(table),
        message="Cafeteria table created successfully"
    )


@router.get("/tables", response_model=dict)
async def get_all_cafeteria_tables(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    min_capacity: Optional[int] = None,
    is_active: Optional[bool] = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all cafeteria tables with optional filters."""
    service = CafeteriaService(db)
    tables, total = await service.list_tables(
        min_capacity=min_capacity,
        is_active=is_active,
        page=page,
        page_size=page_size
    )
    return create_response(
        data=[CafeteriaTableResponse.model_validate(t) for t in tables],
        message="Cafeteria tables retrieved successfully"
    )


@router.get("/tables/{table_id}", response_model=dict)
async def get_cafeteria_table(
    table_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific cafeteria table by ID."""
    service = CafeteriaService(db)
    table = await service.get_table_by_id(table_id)
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cafeteria table not found"
        )
    return create_response(
        data=CafeteriaTableResponse.model_validate(table),
        message="Cafeteria table retrieved successfully"
    )


@router.put("/tables/{table_id}", response_model=dict)
async def update_cafeteria_table(
    table_id: UUID,
    table_data: CafeteriaTableUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_cafeteria_manager),
):
    """Update a cafeteria table (Manager only)."""
    service = CafeteriaService(db)
    table, error = await service.update_table(table_id, table_data, current_user)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return create_response(
        data=CafeteriaTableResponse.model_validate(table),
        message="Cafeteria table updated successfully"
    )


@router.delete("/tables/{table_id}", response_model=dict)
async def delete_cafeteria_table(
    table_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_cafeteria_manager),
):
    """Delete a cafeteria table (Manager only)."""
    service = CafeteriaService(db)
    success, error = await service.delete_table(table_id, current_user)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return create_response(
        data={"deleted": True},
        message="Cafeteria table deleted successfully"
    )


# ============== Cafeteria Table Bookings (All Users) ==============

@router.post("/bookings", response_model=dict)
async def create_cafeteria_booking(
    booking_data: CafeteriaBookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new cafeteria table booking.
    Available to all authenticated users.
    """
    service = CafeteriaService(db)
    booking, error = await service.create_booking(booking_data, current_user)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    
    # Build response with table details
    response_data = {
        "id": booking.id,
        "table_id": booking.table_id,
        "table_code": booking.table.table_code,
        "table_label": booking.table.table_label,
        "table_capacity": booking.table.capacity,
        "user_code": booking.user_code,
        "booking_date": booking.booking_date,
        "start_time": booking.start_time,
        "end_time": booking.end_time,
        "guest_count": booking.guest_count,
        "guest_names": booking.guest_names.split(",") if booking.guest_names else None,
        "status": booking.status,
        "notes": booking.notes,
        "created_at": booking.created_at,
        "updated_at": booking.updated_at
    }
    
    return create_response(
        data=response_data,
        message="Cafeteria booking created successfully"
    )


@router.get("/bookings", response_model=dict)
async def get_cafeteria_bookings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    table_id: Optional[UUID] = None,
    booking_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get cafeteria bookings with optional filters."""
    service = CafeteriaService(db)
    bookings, total = await service.list_bookings(
        table_id=table_id,
        booking_date=booking_date,
        page=page,
        page_size=page_size
    )
    
    # Build response with table details
    response_data = []
    for booking in bookings:
        response_data.append({
            "id": booking.id,
            "table_id": booking.table_id,
            "table_code": booking.table.table_code,
            "table_label": booking.table.table_label,
            "table_capacity": booking.table.capacity,
            "user_code": booking.user_code,
            "booking_date": booking.booking_date,
            "start_time": booking.start_time,
            "end_time": booking.end_time,
            "guest_count": booking.guest_count,
            "guest_names": booking.guest_names.split(",") if booking.guest_names else None,
            "status": booking.status,
            "notes": booking.notes,
            "created_at": booking.created_at,
            "updated_at": booking.updated_at
        })
    
    return create_response(
        data=response_data,
        message="Cafeteria bookings retrieved successfully"
    )


@router.get("/bookings/my", response_model=dict)
async def get_my_cafeteria_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current user's cafeteria bookings."""
    service = CafeteriaService(db)
    bookings, total = await service.list_bookings(
        user_code=current_user.user_code,
        page=1,
        page_size=50
    )
    
    # Build response with table details
    response_data = []
    for booking in bookings:
        response_data.append({
            "id": booking.id,
            "table_id": booking.table_id,
            "table_code": booking.table.table_code,
            "table_label": booking.table.table_label,
            "table_capacity": booking.table.capacity,
            "user_code": booking.user_code,
            "booking_date": booking.booking_date,
            "start_time": booking.start_time,
            "end_time": booking.end_time,
            "guest_count": booking.guest_count,
            "guest_names": booking.guest_names.split(",") if booking.guest_names else None,
            "status": booking.status,
            "notes": booking.notes,
            "created_at": booking.created_at,
            "updated_at": booking.updated_at
        })
    
    return create_response(
        data=response_data,
        message="My cafeteria bookings retrieved successfully"
    )


@router.put("/bookings/{booking_id}", response_model=dict)
async def update_cafeteria_booking(
    booking_id: UUID,
    booking_data: CafeteriaBookingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a cafeteria booking."""
    service = CafeteriaService(db)
    booking, error = await service.update_booking(booking_id, booking_data, current_user)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    
    response_data = {
        "id": booking.id,
        "table_id": booking.table_id,
        "table_code": booking.table.table_code,
        "table_label": booking.table.table_label,
        "table_capacity": booking.table.capacity,
        "user_code": booking.user_code,
        "booking_date": booking.booking_date,
        "start_time": booking.start_time,
        "end_time": booking.end_time,
        "guest_count": booking.guest_count,
        "guest_names": booking.guest_names.split(",") if booking.guest_names else None,
        "status": booking.status,
        "notes": booking.notes,
        "created_at": booking.created_at,
        "updated_at": booking.updated_at
    }
    
    return create_response(
        data=response_data,
        message="Cafeteria booking updated successfully"
    )


@router.delete("/bookings/{booking_id}", response_model=dict)
async def cancel_cafeteria_booking(
    booking_id: UUID,
    reason: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel a cafeteria booking."""
    service = CafeteriaService(db)
    success, error = await service.cancel_booking(booking_id, current_user, reason)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return create_response(
        data={"cancelled": True},
        message="Cafeteria booking cancelled successfully"
    )


# ============== Cafeteria Stats ==============

@router.get("/stats", response_model=dict)
async def get_cafeteria_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get cafeteria statistics."""
    service = CafeteriaService(db)
    stats = await service.get_cafeteria_stats()
    return create_response(
        data=stats,
        message="Cafeteria statistics retrieved successfully"
    )
