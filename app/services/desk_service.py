from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from uuid import UUID
from datetime import date, time, datetime, timezone

from ..models.desk import Desk, DeskBooking, ConferenceRoom, ConferenceRoomBooking
from ..models.user import User
from ..models.enums import BookingStatus, DeskStatus, UserRole, ManagerType
from ..schemas.desk import (
    DeskCreate, DeskUpdate, DeskBookingCreate, DeskBookingUpdate,
    ConferenceRoomCreate, ConferenceRoomUpdate, ConferenceRoomBookingCreate, ConferenceRoomBookingUpdate
)


class DeskService:
    """
    Desk and Conference Room management service.
    Managed by DESK_CONFERENCE Manager.
    Simplified without location fields.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def can_manage_desks(self, user: User) -> bool:
        """Check if user can manage desks and conference rooms."""
        if user.role == UserRole.SUPER_ADMIN:
            return True
        if user.role == UserRole.ADMIN:
            return True
        if user.role == UserRole.MANAGER and user.manager_type == ManagerType.DESK_CONFERENCE:
            return True
        return False
    
    # ==================== Desk Management ====================
    
    async def get_desk_by_id(self, desk_id: UUID) -> Optional[Desk]:
        """Get desk by ID."""
        result = await self.db.execute(
            select(Desk).where(Desk.id == desk_id)
        )
        return result.scalar_one_or_none()
    
    async def get_desk_by_code(self, desk_code: str) -> Optional[Desk]:
        """Get desk by code."""
        result = await self.db.execute(
            select(Desk).where(Desk.desk_code == desk_code)
        )
        return result.scalar_one_or_none()
    
    async def list_desks(
        self,
        status: Optional[DeskStatus] = None,
        is_active: Optional[bool] = True,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Desk], int]:
        """List desks with filtering."""
        query = select(Desk)
        count_query = select(func.count(Desk.id))
        
        conditions = []
        if status:
            conditions.append(Desk.status == status)
        if is_active is not None:
            conditions.append(Desk.is_active == is_active)
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        desks = list(result.scalars().all())
        
        return desks, total
    
    async def create_desk(
        self,
        desk_data: DeskCreate,
        created_by: User
    ) -> Tuple[Optional[Desk], Optional[str]]:
        """Create a new desk - Manager only."""
        if not self.can_manage_desks(created_by):
            return None, "Only DESK_CONFERENCE Manager can create desks"
        
        desk = Desk(
            desk_label=desk_data.desk_label,
            has_monitor=desk_data.has_monitor,
            has_docking_station=desk_data.has_docking_station,
            notes=desk_data.notes,
            created_by_code=created_by.user_code
        )
        
        self.db.add(desk)
        await self.db.commit()
        await self.db.refresh(desk)
        
        return desk, None
    
    async def update_desk(
        self,
        desk_id: UUID,
        desk_data: DeskUpdate,
        user: User
    ) -> Tuple[Optional[Desk], Optional[str]]:
        """Update a desk - Manager only."""
        if not self.can_manage_desks(user):
            return None, "Only DESK_CONFERENCE Manager can update desks"
        
        desk = await self.get_desk_by_id(desk_id)
        if not desk:
            return None, "Desk not found"
        
        update_data = desk_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(desk, field, value)
        
        await self.db.commit()
        await self.db.refresh(desk)
        
        return desk, None
    
    async def delete_desk(
        self,
        desk_id: UUID,
        user: User
    ) -> Tuple[bool, Optional[str]]:
        """Soft delete a desk - Manager only."""
        if not self.can_manage_desks(user):
            return False, "Only DESK_CONFERENCE Manager can delete desks"
        
        desk = await self.get_desk_by_id(desk_id)
        if not desk:
            return False, "Desk not found"
        
        # Check for active bookings
        active_bookings = await self.db.execute(
            select(DeskBooking).where(
                and_(
                    DeskBooking.desk_id == desk_id,
                    DeskBooking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                    DeskBooking.end_date >= date.today()
                )
            )
        )
        if active_bookings.scalar_one_or_none():
            return False, "Cannot delete desk with active bookings"
        
        desk.is_active = False
        await self.db.commit()
        
        return True, None
    
    # ==================== Desk Booking ====================
    
    async def get_booking_by_id(self, booking_id: UUID) -> Optional[DeskBooking]:
        """Get desk booking by ID."""
        result = await self.db.execute(
            select(DeskBooking)
            .options(selectinload(DeskBooking.desk))
            .where(DeskBooking.id == booking_id)
        )
        return result.scalar_one_or_none()
    
    async def check_booking_overlap(
        self,
        desk_id: UUID,
        start_date: date,
        end_date: date,
        exclude_booking_id: Optional[UUID] = None
    ) -> bool:
        """Check if there's an overlapping booking for the date range."""
        # Date ranges overlap if: start1 <= end2 AND end1 >= start2
        query = select(DeskBooking).where(
            and_(
                DeskBooking.desk_id == desk_id,
                DeskBooking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                DeskBooking.start_date <= end_date,
                DeskBooking.end_date >= start_date
            )
        )
        
        if exclude_booking_id:
            query = query.where(DeskBooking.id != exclude_booking_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def create_booking(
        self,
        booking_data: DeskBookingCreate,
        user: User
    ) -> Tuple[Optional[DeskBooking], Optional[str]]:
        """Create a new desk booking."""
        # Validate desk exists and is active
        desk = await self.get_desk_by_id(booking_data.desk_id)
        if not desk:
            return None, "Desk not found"
        if not desk.is_active:
            return None, "Desk is not active"
        if desk.status == DeskStatus.MAINTENANCE:
            return None, "Desk is under maintenance"
        
        # Check for overlapping bookings
        has_overlap = await self.check_booking_overlap(
            booking_data.desk_id,
            booking_data.start_date,
            booking_data.end_date
        )
        if has_overlap:
            return None, "Date range overlaps with existing booking"
        
        booking = DeskBooking(
            desk_id=booking_data.desk_id,
            user_code=user.user_code,
            start_date=booking_data.start_date,
            end_date=booking_data.end_date,
            status=BookingStatus.CONFIRMED,
            notes=booking_data.notes
        )
        
        self.db.add(booking)
        await self.db.commit()
        await self.db.refresh(booking)
        
        return booking, None
    
    async def update_booking(
        self,
        booking_id: UUID,
        booking_data: DeskBookingUpdate,
        user: User
    ) -> Tuple[Optional[DeskBooking], Optional[str]]:
        """Update a desk booking."""
        booking = await self.get_booking_by_id(booking_id)
        if not booking:
            return None, "Booking not found"
        
        # Check ownership or admin access
        if booking.user_code != user.user_code:
            if not self.can_manage_desks(user):
                return None, "Cannot modify another user's booking"
        
        # If updating dates, check for overlaps
        if booking_data.start_date or booking_data.end_date:
            start = booking_data.start_date or booking.start_date
            end = booking_data.end_date or booking.end_date
            
            has_overlap = await self.check_booking_overlap(
                booking.desk_id,
                start,
                end,
                exclude_booking_id=booking_id
            )
            if has_overlap:
                return None, "Date range overlaps with existing booking"
        
        update_data = booking_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(booking, field, value)
        
        await self.db.commit()
        await self.db.refresh(booking)
        
        return booking, None
    
    async def cancel_booking(
        self,
        booking_id: UUID,
        user: User,
        reason: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """Cancel a desk booking."""
        booking = await self.get_booking_by_id(booking_id)
        if not booking:
            return False, "Booking not found"
        
        if booking.user_code != user.user_code:
            if not self.can_manage_desks(user):
                return False, "Cannot cancel another user's booking"
        
        if booking.status == BookingStatus.CANCELLED:
            return False, "Booking is already cancelled"
        
        booking.status = BookingStatus.CANCELLED
        booking.cancellation_reason = reason
        booking.cancelled_at = datetime.now(timezone.utc)
        
        await self.db.commit()
        
        return True, None
    
    async def list_bookings(
        self,
        desk_id: Optional[UUID] = None,
        user_code: Optional[str] = None,
        booking_date: Optional[date] = None,
        status: Optional[BookingStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[DeskBooking], int]:
        """List desk bookings with filtering."""
        query = select(DeskBooking).options(selectinload(DeskBooking.desk))
        count_query = select(func.count(DeskBooking.id))
        
        conditions = []
        if desk_id:
            conditions.append(DeskBooking.desk_id == desk_id)
        if user_code:
            conditions.append(DeskBooking.user_code == user_code)
        if booking_date:
            # Filter bookings that include this date
            conditions.append(DeskBooking.start_date <= booking_date)
            conditions.append(DeskBooking.end_date >= booking_date)
        if status:
            conditions.append(DeskBooking.status == status)
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.order_by(DeskBooking.start_date.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        bookings = list(result.scalars().all())
        
        return bookings, total
    
    async def get_available_desks(
        self,
        start_date: date,
        end_date: date
    ) -> List[Desk]:
        """Get all available desks for a date range."""
        # Get all active desks
        query = select(Desk).where(
            and_(
                Desk.is_active == True,
                Desk.status != DeskStatus.MAINTENANCE
            )
        )
        
        result = await self.db.execute(query)
        all_desks = list(result.scalars().all())
        
        # Get booked desks for the date range
        booked_result = await self.db.execute(
            select(DeskBooking.desk_id).where(
                and_(
                    DeskBooking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                    DeskBooking.start_date <= end_date,
                    DeskBooking.end_date >= start_date
                )
            )
        )
        booked_desk_ids = set(row[0] for row in booked_result.fetchall())
        
        # Filter out booked desks
        available_desks = [d for d in all_desks if d.id not in booked_desk_ids]
        
        return available_desks
    
    # ==================== Conference Room Management ====================
    
    async def get_room_by_id(self, room_id: UUID) -> Optional[ConferenceRoom]:
        """Get conference room by ID."""
        result = await self.db.execute(
            select(ConferenceRoom).where(ConferenceRoom.id == room_id)
        )
        return result.scalar_one_or_none()
    
    async def get_room_by_code(self, room_code: str) -> Optional[ConferenceRoom]:
        """Get conference room by code."""
        result = await self.db.execute(
            select(ConferenceRoom).where(ConferenceRoom.room_code == room_code)
        )
        return result.scalar_one_or_none()
    
    async def list_rooms(
        self,
        min_capacity: Optional[int] = None,
        is_active: Optional[bool] = True,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[ConferenceRoom], int]:
        """List conference rooms with filtering."""
        query = select(ConferenceRoom)
        count_query = select(func.count(ConferenceRoom.id))
        
        conditions = []
        if min_capacity:
            conditions.append(ConferenceRoom.capacity >= min_capacity)
        if is_active is not None:
            conditions.append(ConferenceRoom.is_active == is_active)
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        rooms = list(result.scalars().all())
        
        return rooms, total
    
    async def create_room(
        self,
        room_data: ConferenceRoomCreate,
        created_by: User
    ) -> Tuple[Optional[ConferenceRoom], Optional[str]]:
        """Create a new conference room - Manager only."""
        if not self.can_manage_desks(created_by):
            return None, "Only DESK_CONFERENCE Manager can create conference rooms"
        
        room = ConferenceRoom(
            room_label=room_data.room_label,
            capacity=room_data.capacity,
            has_projector=room_data.has_projector,
            has_whiteboard=room_data.has_whiteboard,
            has_video_conferencing=room_data.has_video_conferencing,
            notes=room_data.notes,
            created_by_code=created_by.user_code
        )
        
        self.db.add(room)
        await self.db.commit()
        await self.db.refresh(room)
        
        return room, None
    
    async def update_room(
        self,
        room_id: UUID,
        room_data: ConferenceRoomUpdate,
        user: User
    ) -> Tuple[Optional[ConferenceRoom], Optional[str]]:
        """Update a conference room - Manager only."""
        if not self.can_manage_desks(user):
            return None, "Only DESK_CONFERENCE Manager can update conference rooms"
        
        room = await self.get_room_by_id(room_id)
        if not room:
            return None, "Conference room not found"
        
        update_data = room_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(room, field, value)
        
        await self.db.commit()
        await self.db.refresh(room)
        
        return room, None
    
    async def delete_room(
        self,
        room_id: UUID,
        user: User
    ) -> Tuple[bool, Optional[str]]:
        """Soft delete a conference room - Manager only."""
        if not self.can_manage_desks(user):
            return False, "Only DESK_CONFERENCE Manager can delete conference rooms"
        
        room = await self.get_room_by_id(room_id)
        if not room:
            return False, "Conference room not found"
        
        # Check for active bookings
        active_bookings = await self.db.execute(
            select(ConferenceRoomBooking).where(
                and_(
                    ConferenceRoomBooking.room_id == room_id,
                    ConferenceRoomBooking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                    ConferenceRoomBooking.booking_date >= date.today()
                )
            )
        )
        if active_bookings.scalar_one_or_none():
            return False, "Cannot delete room with active bookings"
        
        room.is_active = False
        await self.db.commit()
        
        return True, None
    
    # ==================== Conference Room Booking ====================
    
    async def get_room_booking_by_id(self, booking_id: UUID) -> Optional[ConferenceRoomBooking]:
        """Get conference room booking by ID."""
        result = await self.db.execute(
            select(ConferenceRoomBooking)
            .options(selectinload(ConferenceRoomBooking.room))
            .where(ConferenceRoomBooking.id == booking_id)
        )
        return result.scalar_one_or_none()
    
    async def check_room_booking_overlap(
        self,
        room_id: UUID,
        booking_date: date,
        start_time: time,
        end_time: time,
        exclude_booking_id: Optional[UUID] = None
    ) -> bool:
        """Check if there's an overlapping room booking."""
        query = select(ConferenceRoomBooking).where(
            and_(
                ConferenceRoomBooking.room_id == room_id,
                ConferenceRoomBooking.booking_date == booking_date,
                ConferenceRoomBooking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                or_(
                    and_(
                        ConferenceRoomBooking.start_time <= start_time,
                        ConferenceRoomBooking.end_time > start_time
                    ),
                    and_(
                        ConferenceRoomBooking.start_time < end_time,
                        ConferenceRoomBooking.end_time >= end_time
                    ),
                    and_(
                        ConferenceRoomBooking.start_time >= start_time,
                        ConferenceRoomBooking.end_time <= end_time
                    )
                )
            )
        )
        
        if exclude_booking_id:
            query = query.where(ConferenceRoomBooking.id != exclude_booking_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def create_room_booking(
        self,
        booking_data: ConferenceRoomBookingCreate,
        user: User
    ) -> Tuple[Optional[ConferenceRoomBooking], Optional[str]]:
        """Create a new conference room booking."""
        room = await self.get_room_by_id(booking_data.room_id)
        if not room:
            return None, "Conference room not found"
        if not room.is_active:
            return None, "Conference room is not active"
        if room.status == DeskStatus.MAINTENANCE:
            return None, "Conference room is under maintenance"
        
        # Check capacity
        if booking_data.attendees_count > room.capacity:
            return None, f"Attendees count exceeds room capacity ({room.capacity})"
        
        # Check for overlapping bookings
        has_overlap = await self.check_room_booking_overlap(
            booking_data.room_id,
            booking_data.booking_date,
            booking_data.start_time,
            booking_data.end_time
        )
        if has_overlap:
            return None, "Time slot overlaps with existing booking"
        
        booking = ConferenceRoomBooking(
            room_id=booking_data.room_id,
            user_code=user.user_code,
            booking_date=booking_data.booking_date,
            start_time=booking_data.start_time,
            end_time=booking_data.end_time,
            title=booking_data.title,
            description=booking_data.description,
            attendees_count=booking_data.attendees_count,
            status=BookingStatus.PENDING,  # Requires manager approval
            notes=booking_data.notes
        )
        
        self.db.add(booking)
        await self.db.commit()
        await self.db.refresh(booking)
        
        return booking, None
    
    async def cancel_room_booking(
        self,
        booking_id: UUID,
        user: User,
        reason: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """Cancel a conference room booking."""
        booking = await self.get_room_booking_by_id(booking_id)
        if not booking:
            return False, "Booking not found"
        
        if booking.user_code != user.user_code:
            if not self.can_manage_desks(user):
                return False, "Cannot cancel another user's booking"
        
        if booking.status == BookingStatus.CANCELLED:
            return False, "Booking is already cancelled"
        
        booking.status = BookingStatus.CANCELLED
        booking.cancellation_reason = reason
        booking.cancelled_at = datetime.now(timezone.utc)
        
        await self.db.commit()
        
        return True, None
    
    async def list_room_bookings(
        self,
        room_id: Optional[UUID] = None,
        user_code: Optional[str] = None,
        booking_date: Optional[date] = None,
        status: Optional[BookingStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[ConferenceRoomBooking], int]:
        """List conference room bookings with filtering."""
        query = select(ConferenceRoomBooking).options(selectinload(ConferenceRoomBooking.room))
        count_query = select(func.count(ConferenceRoomBooking.id))
        
        conditions = []
        if room_id:
            conditions.append(ConferenceRoomBooking.room_id == room_id)
        if user_code:
            conditions.append(ConferenceRoomBooking.user_code == user_code)
        if booking_date:
            conditions.append(ConferenceRoomBooking.booking_date == booking_date)
        if status:
            conditions.append(ConferenceRoomBooking.status == status)
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.order_by(ConferenceRoomBooking.booking_date.desc(), ConferenceRoomBooking.start_time)
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        bookings = list(result.scalars().all())
        
        return bookings, total
    
    async def approve_room_booking(
        self,
        booking_id: UUID,
        user: User,
        notes: Optional[str] = None
    ) -> Tuple[Optional[ConferenceRoomBooking], Optional[str]]:
        """Approve a pending conference room booking. Manager only."""
        if not self.can_manage_desks(user):
            return None, "Only DESK_CONFERENCE Manager can approve bookings"
        
        booking = await self.get_room_booking_by_id(booking_id)
        if not booking:
            return None, "Booking not found"
        
        if booking.status != BookingStatus.PENDING:
            return None, f"Cannot approve booking with status '{booking.status.value}'. Only PENDING bookings can be approved."
        
        # Check for overlapping confirmed bookings (in case another was approved first)
        has_overlap = await self.check_room_booking_overlap(
            booking.room_id,
            booking.booking_date,
            booking.start_time,
            booking.end_time,
            exclude_booking_id=booking_id
        )
        if has_overlap:
            return None, "Cannot approve: Time slot now conflicts with another confirmed booking"
        
        booking.status = BookingStatus.CONFIRMED
        if notes:
            booking.notes = (booking.notes or "") + f"\nApproval note: {notes}"
        
        await self.db.commit()
        await self.db.refresh(booking)
        
        return booking, None
    
    async def reject_room_booking(
        self,
        booking_id: UUID,
        user: User,
        reason: str
    ) -> Tuple[Optional[ConferenceRoomBooking], Optional[str]]:
        """Reject a pending conference room booking. Manager only."""
        if not self.can_manage_desks(user):
            return None, "Only DESK_CONFERENCE Manager can reject bookings"
        
        booking = await self.get_room_booking_by_id(booking_id)
        if not booking:
            return None, "Booking not found"
        
        if booking.status != BookingStatus.PENDING:
            return None, f"Cannot reject booking with status '{booking.status.value}'. Only PENDING bookings can be rejected."
        
        booking.status = BookingStatus.REJECTED
        booking.cancellation_reason = reason
        booking.cancelled_at = datetime.now(timezone.utc)
        
        await self.db.commit()
        await self.db.refresh(booking)
        
        return booking, None
    
    async def list_pending_room_bookings(
        self,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[ConferenceRoomBooking], int]:
        """List all pending conference room bookings for manager review."""
        return await self.list_room_bookings(
            status=BookingStatus.PENDING,
            page=page,
            page_size=page_size
        )
