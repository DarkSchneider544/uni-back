"""
Desk and Conference Room management endpoints.
Allows desk managers to create, update, and delete desks/rooms.
Handles desk and conference room bookings.
Simplified API without location fields.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from datetime import date

from ....core.database import get_db
from ....core.dependencies import get_current_active_user, require_admin_or_above
from ....models.user import User
from ....models.enums import BookingStatus, DeskStatus, UserRole, ManagerType
from ....schemas.desk import (
    DeskCreate, DeskUpdate, DeskResponse, DeskListResponse,
    DeskBookingCreate, DeskBookingUpdate, DeskBookingResponse, DeskBookingListResponse,
    ConferenceRoomCreate, ConferenceRoomUpdate, ConferenceRoomResponse, ConferenceRoomListResponse,
    ConferenceRoomBookingCreate, ConferenceRoomBookingUpdate, ConferenceRoomBookingResponse,
    ConferenceRoomBookingListResponse, DeskStatistics,
    ConferenceRoomBookingApproval, ConferenceRoomBookingRejection
)
from ....schemas.base import APIResponse, PaginatedResponse
from ....services.desk_service import DeskService
from ....utils.response import create_response, create_paginated_response

router = APIRouter()


def require_desk_manager(user: User = Depends(get_current_active_user)) -> User:
    """Dependency to check if user is desk manager or admin."""
    if user.role == UserRole.SUPER_ADMIN:
        return user
    if user.role == UserRole.ADMIN:
        return user
    if user.role == UserRole.MANAGER and user.manager_type == ManagerType.DESK_CONFERENCE:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="DESK_CONFERENCE Manager access required"
    )


# ==================== Desk Management APIs (Manager Only) ====================

@router.post("", response_model=APIResponse[DeskResponse])
async def create_desk(
    desk_data: DeskCreate,
    current_user: User = Depends(require_desk_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new desk.
    
    **DESK_CONFERENCE Manager only**
    - desk_code is auto-generated (DSK-XXXX)
    """
    desk_service = DeskService(db)
    desk, error = await desk_service.create_desk(desk_data, current_user)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return create_response(
        data=DeskResponse.model_validate(desk),
        message="Desk created successfully"
    )


@router.get("", response_model=PaginatedResponse[DeskResponse])
async def list_desks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[DeskStatus] = None,
    is_active: Optional[bool] = True,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List all desks with filtering."""
    desk_service = DeskService(db)
    desks, total = await desk_service.list_desks(
        status=status,
        is_active=is_active,
        page=page,
        page_size=page_size
    )
    
    return create_paginated_response(
        data=[DeskResponse.model_validate(d) for d in desks],
        total=total,
        page=page,
        page_size=page_size,
        message="Desks retrieved successfully"
    )


# NOTE: /{desk_id} routes moved to end of file to avoid route conflicts with /bookings, /rooms etc.


# ==================== Desk Booking APIs ====================

@router.post("/bookings", response_model=APIResponse[DeskBookingResponse])
async def create_desk_booking(
    booking_data: DeskBookingCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Book a desk for a specific date and time.
    
    Available to all authenticated users.
    """
    desk_service = DeskService(db)
    booking, error = await desk_service.create_booking(booking_data, current_user)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # Build response with desk details
    response_data = {
        "id": booking.id,
        "desk_id": booking.desk_id,
        "desk_code": booking.desk.desk_code,
        "desk_label": booking.desk.desk_label,
        "user_code": booking.user_code,
        "start_date": booking.start_date,
        "end_date": booking.end_date,
        "status": booking.status,
        "checked_in_at": booking.checked_in_at,
        "checked_out_at": booking.checked_out_at,
        "notes": booking.notes,
        "created_at": booking.created_at,
        "updated_at": booking.updated_at
    }
    
    return create_response(
        data=response_data,
        message="Desk booking created successfully"
    )


@router.get("/bookings", response_model=PaginatedResponse[DeskBookingResponse])
async def list_desk_bookings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    desk_id: Optional[UUID] = None,
    booking_date: Optional[date] = None,
    status: Optional[BookingStatus] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List desk bookings with filtering."""
    desk_service = DeskService(db)
    bookings, total = await desk_service.list_bookings(
        desk_id=desk_id,
        booking_date=booking_date,
        status=status,
        page=page,
        page_size=page_size
    )
    
    # Build response with desk details
    response_data = []
    for booking in bookings:
        response_data.append({
            "id": booking.id,
            "desk_id": booking.desk_id,
            "desk_code": booking.desk.desk_code,
            "desk_label": booking.desk.desk_label,
            "user_code": booking.user_code,
            "start_date": booking.start_date,
            "end_date": booking.end_date,
            "status": booking.status,
            "checked_in_at": booking.checked_in_at,
            "checked_out_at": booking.checked_out_at,
            "notes": booking.notes,
            "created_at": booking.created_at,
            "updated_at": booking.updated_at
        })
    
    return create_paginated_response(
        data=response_data,
        total=total,
        page=page,
        page_size=page_size,
        message="Desk bookings retrieved successfully"
    )


@router.get("/bookings/my", response_model=APIResponse)
async def get_my_desk_bookings(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's desk bookings."""
    desk_service = DeskService(db)
    bookings, total = await desk_service.list_bookings(
        user_code=current_user.user_code,
        page=1,
        page_size=50
    )
    
    # Build response with desk details
    response_data = []
    for booking in bookings:
        response_data.append({
            "id": booking.id,
            "desk_id": booking.desk_id,
            "desk_code": booking.desk.desk_code,
            "desk_label": booking.desk.desk_label,
            "user_code": booking.user_code,
            "start_date": booking.start_date,
            "end_date": booking.end_date,
            "status": booking.status,
            "checked_in_at": booking.checked_in_at,
            "checked_out_at": booking.checked_out_at,
            "notes": booking.notes,
            "created_at": booking.created_at,
            "updated_at": booking.updated_at
        })
    
    return create_response(
        data=response_data,
        message="My desk bookings retrieved successfully"
    )


@router.delete("/bookings/{booking_id}", response_model=APIResponse)
async def cancel_desk_booking(
    booking_id: UUID,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a desk booking."""
    desk_service = DeskService(db)
    success, error = await desk_service.cancel_booking(booking_id, current_user, reason)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return create_response(
        data={"cancelled": True},
        message="Desk booking cancelled successfully"
    )


# ==================== Conference Room APIs ====================

@router.post("/rooms", response_model=APIResponse[ConferenceRoomResponse])
async def create_conference_room(
    room_data: ConferenceRoomCreate,
    current_user: User = Depends(require_desk_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new conference room.
    
    **DESK_CONFERENCE Manager only**
    - room_code is auto-generated (CNF-XXXX)
    """
    desk_service = DeskService(db)
    room, error = await desk_service.create_room(room_data, current_user)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return create_response(
        data=ConferenceRoomResponse.model_validate(room),
        message="Conference room created successfully"
    )


@router.get("/rooms", response_model=PaginatedResponse[ConferenceRoomResponse])
async def list_conference_rooms(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    min_capacity: Optional[int] = None,
    is_active: Optional[bool] = True,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List all conference rooms with filtering."""
    desk_service = DeskService(db)
    rooms, total = await desk_service.list_rooms(
        min_capacity=min_capacity,
        is_active=is_active,
        page=page,
        page_size=page_size
    )
    
    return create_paginated_response(
        data=[ConferenceRoomResponse.model_validate(r) for r in rooms],
        total=total,
        page=page,
        page_size=page_size,
        message="Conference rooms retrieved successfully"
    )


@router.get("/rooms/{room_id}", response_model=APIResponse[ConferenceRoomResponse])
async def get_conference_room(
    room_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get conference room by ID."""
    desk_service = DeskService(db)
    room = await desk_service.get_room_by_id(room_id)
    
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conference room not found"
        )
    
    return create_response(
        data=ConferenceRoomResponse.model_validate(room),
        message="Conference room retrieved successfully"
    )


@router.put("/rooms/{room_id}", response_model=APIResponse[ConferenceRoomResponse])
async def update_conference_room(
    room_id: UUID,
    room_data: ConferenceRoomUpdate,
    current_user: User = Depends(require_desk_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a conference room.
    
    **DESK_CONFERENCE Manager only**
    """
    desk_service = DeskService(db)
    room, error = await desk_service.update_room(room_id, room_data, current_user)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return create_response(
        data=ConferenceRoomResponse.model_validate(room),
        message="Conference room updated successfully"
    )


@router.delete("/rooms/{room_id}", response_model=APIResponse)
async def delete_conference_room(
    room_id: UUID,
    current_user: User = Depends(require_desk_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a conference room (soft delete).
    
    **DESK_CONFERENCE Manager only**
    """
    desk_service = DeskService(db)
    success, error = await desk_service.delete_room(room_id, current_user)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return create_response(
        data={"deleted": True},
        message="Conference room deleted successfully"
    )


# ==================== Conference Room Booking APIs ====================

@router.post("/rooms/bookings", response_model=APIResponse[ConferenceRoomBookingResponse])
async def create_room_booking(
    booking_data: ConferenceRoomBookingCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Book a conference room.
    
    Available to all authenticated users.
    """
    desk_service = DeskService(db)
    booking, error = await desk_service.create_room_booking(booking_data, current_user)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # Build response with room details
    response_data = {
        "id": booking.id,
        "room_id": booking.room_id,
        "room_code": booking.room.room_code,
        "room_label": booking.room.room_label,
        "capacity": booking.room.capacity,
        "user_code": booking.user_code,
        "booking_date": booking.booking_date,
        "start_time": booking.start_time,
        "end_time": booking.end_time,
        "title": booking.title,
        "description": booking.description,
        "attendees_count": booking.attendees_count,
        "status": booking.status,
        "notes": booking.notes,
        "created_at": booking.created_at,
        "updated_at": booking.updated_at
    }
    
    return create_response(
        data=response_data,
        message="Conference room booking created successfully"
    )


@router.get("/rooms/bookings", response_model=PaginatedResponse[ConferenceRoomBookingResponse])
async def list_room_bookings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    room_id: Optional[UUID] = None,
    booking_date: Optional[date] = None,
    status: Optional[BookingStatus] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List conference room bookings with filtering."""
    desk_service = DeskService(db)
    bookings, total = await desk_service.list_room_bookings(
        room_id=room_id,
        booking_date=booking_date,
        status=status,
        page=page,
        page_size=page_size
    )
    
    # Build response with room details
    response_data = []
    for booking in bookings:
        response_data.append({
            "id": booking.id,
            "room_id": booking.room_id,
            "room_code": booking.room.room_code,
            "room_label": booking.room.room_label,
            "capacity": booking.room.capacity,
            "user_code": booking.user_code,
            "booking_date": booking.booking_date,
            "start_time": booking.start_time,
            "end_time": booking.end_time,
            "title": booking.title,
            "description": booking.description,
            "attendees_count": booking.attendees_count,
            "status": booking.status,
            "notes": booking.notes,
            "created_at": booking.created_at,
            "updated_at": booking.updated_at
        })
    
    return create_paginated_response(
        data=response_data,
        total=total,
        page=page,
        page_size=page_size,
        message="Conference room bookings retrieved successfully"
    )


@router.delete("/rooms/bookings/{booking_id}", response_model=APIResponse)
async def cancel_room_booking(
    booking_id: UUID,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a conference room booking."""
    desk_service = DeskService(db)
    success, error = await desk_service.cancel_room_booking(booking_id, current_user, reason)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return create_response(
        data={"cancelled": True},
        message="Conference room booking cancelled successfully"
    )


# ==================== Conference Room Booking Approval APIs (Manager Only) ====================

@router.get("/rooms/bookings/pending", response_model=PaginatedResponse[ConferenceRoomBookingResponse])
async def list_pending_room_bookings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_desk_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    List all pending conference room bookings awaiting approval.
    
    **DESK_CONFERENCE Manager only**
    """
    desk_service = DeskService(db)
    bookings, total = await desk_service.list_pending_room_bookings(
        page=page,
        page_size=page_size
    )
    
    # Build response with room details
    response_data = []
    for booking in bookings:
        response_data.append({
            "id": booking.id,
            "room_id": booking.room_id,
            "room_code": booking.room.room_code,
            "room_label": booking.room.room_label,
            "capacity": booking.room.capacity,
            "user_code": booking.user_code,
            "booking_date": booking.booking_date,
            "start_time": booking.start_time,
            "end_time": booking.end_time,
            "title": booking.title,
            "description": booking.description,
            "attendees_count": booking.attendees_count,
            "status": booking.status,
            "notes": booking.notes,
            "created_at": booking.created_at,
            "updated_at": booking.updated_at
        })
    
    return create_paginated_response(
        data=response_data,
        total=total,
        page=page,
        page_size=page_size,
        message="Pending conference room bookings retrieved successfully"
    )


@router.post("/rooms/bookings/{booking_id}/approve", response_model=APIResponse[ConferenceRoomBookingResponse])
async def approve_room_booking(
    booking_id: UUID,
    approval_data: ConferenceRoomBookingApproval = None,
    current_user: User = Depends(require_desk_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Approve a pending conference room booking.
    
    **DESK_CONFERENCE Manager only**
    """
    desk_service = DeskService(db)
    notes = approval_data.notes if approval_data else None
    booking, error = await desk_service.approve_room_booking(booking_id, current_user, notes)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # Build response with room details
    response_data = {
        "id": booking.id,
        "room_id": booking.room_id,
        "room_code": booking.room.room_code,
        "room_label": booking.room.room_label,
        "capacity": booking.room.capacity,
        "user_code": booking.user_code,
        "booking_date": booking.booking_date,
        "start_time": booking.start_time,
        "end_time": booking.end_time,
        "title": booking.title,
        "description": booking.description,
        "attendees_count": booking.attendees_count,
        "status": booking.status,
        "notes": booking.notes,
        "created_at": booking.created_at,
        "updated_at": booking.updated_at
    }
    
    return create_response(
        data=response_data,
        message="Conference room booking approved successfully"
    )


@router.post("/rooms/bookings/{booking_id}/reject", response_model=APIResponse[ConferenceRoomBookingResponse])
async def reject_room_booking(
    booking_id: UUID,
    rejection_data: ConferenceRoomBookingRejection,
    current_user: User = Depends(require_desk_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Reject a pending conference room booking.
    
    **DESK_CONFERENCE Manager only**
    """
    desk_service = DeskService(db)
    booking, error = await desk_service.reject_room_booking(booking_id, current_user, rejection_data.reason)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # Build response with room details
    response_data = {
        "id": booking.id,
        "room_id": booking.room_id,
        "room_code": booking.room.room_code,
        "room_label": booking.room.room_label,
        "capacity": booking.room.capacity,
        "user_code": booking.user_code,
        "booking_date": booking.booking_date,
        "start_time": booking.start_time,
        "end_time": booking.end_time,
        "title": booking.title,
        "description": booking.description,
        "attendees_count": booking.attendees_count,
        "status": booking.status,
        "notes": booking.notes,
        "created_at": booking.created_at,
        "updated_at": booking.updated_at
    }
    
    return create_response(
        data=response_data,
        message="Conference room booking rejected"
    )


# ==================== Desk by ID APIs (placed at end to avoid route conflicts) ====================

@router.get("/{desk_id}", response_model=APIResponse[DeskResponse])
async def get_desk(
    desk_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get desk by ID."""
    desk_service = DeskService(db)
    desk = await desk_service.get_desk_by_id(desk_id)
    
    if not desk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Desk not found"
        )
    
    return create_response(
        data=DeskResponse.model_validate(desk),
        message="Desk retrieved successfully"
    )


@router.put("/{desk_id}", response_model=APIResponse[DeskResponse])
async def update_desk(
    desk_id: UUID,
    desk_data: DeskUpdate,
    current_user: User = Depends(require_desk_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a desk.
    
    **DESK_CONFERENCE Manager only**
    """
    desk_service = DeskService(db)
    desk, error = await desk_service.update_desk(desk_id, desk_data, current_user)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return create_response(
        data=DeskResponse.model_validate(desk),
        message="Desk updated successfully"
    )


@router.delete("/{desk_id}", response_model=APIResponse)
async def delete_desk(
    desk_id: UUID,
    current_user: User = Depends(require_desk_manager),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a desk (soft delete).
    
    **DESK_CONFERENCE Manager only**
    """
    desk_service = DeskService(db)
    success, error = await desk_service.delete_desk(desk_id, current_user)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return create_response(
        data={"deleted": True},
        message="Desk deleted successfully"
    )
