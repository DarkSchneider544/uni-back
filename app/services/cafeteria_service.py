from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from uuid import UUID
from datetime import date, time, datetime, timezone

from ..models.cafeteria import CafeteriaTable, CafeteriaTableBooking
from ..models.user import User
from ..models.enums import BookingStatus, UserRole, ManagerType
from ..schemas.cafeteria import (
    CafeteriaTableCreate, CafeteriaTableUpdate,
    CafeteriaBookingCreate, CafeteriaBookingUpdate
)


class CafeteriaService:
    """
    Cafeteria table management service.
    Managed by CAFETERIA Manager.
    Simplified without location fields.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def can_manage_cafeteria(self, user: User) -> bool:
        """Check if user can manage cafeteria tables."""
        if user.role == UserRole.SUPER_ADMIN:
            return True
        if user.role == UserRole.ADMIN:
            return True
        if user.role == UserRole.MANAGER and user.manager_type == ManagerType.CAFETERIA:
            return True
        return False
    
    # ==================== Cafeteria Table Management ====================
    
    async def get_table_by_id(self, table_id: UUID) -> Optional[CafeteriaTable]:
        """Get cafeteria table by ID."""
        result = await self.db.execute(
            select(CafeteriaTable).where(CafeteriaTable.id == table_id)
        )
        return result.scalar_one_or_none()
    
    async def get_table_by_code(self, table_code: str) -> Optional[CafeteriaTable]:
        """Get cafeteria table by code."""
        result = await self.db.execute(
            select(CafeteriaTable).where(CafeteriaTable.table_code == table_code)
        )
        return result.scalar_one_or_none()
    
    async def list_tables(
        self,
        min_capacity: Optional[int] = None,
        is_active: Optional[bool] = True,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[CafeteriaTable], int]:
        """List cafeteria tables with filtering."""
        query = select(CafeteriaTable)
        count_query = select(func.count(CafeteriaTable.id))
        
        conditions = []
        if min_capacity:
            conditions.append(CafeteriaTable.capacity >= min_capacity)
        if is_active is not None:
            conditions.append(CafeteriaTable.is_active == is_active)
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        tables = list(result.scalars().all())
        
        return tables, total
    
    async def create_table(
        self,
        table_data: CafeteriaTableCreate,
        created_by: User
    ) -> Tuple[Optional[CafeteriaTable], Optional[str]]:
        """Create a new cafeteria table - Manager only."""
        if not self.can_manage_cafeteria(created_by):
            return None, "Only CAFETERIA Manager can create cafeteria tables"
        
        table = CafeteriaTable(
            table_label=table_data.table_label,
            capacity=table_data.capacity,
            table_type=table_data.table_type,
            notes=table_data.notes,
            created_by_code=created_by.user_code
        )
        
        self.db.add(table)
        await self.db.commit()
        await self.db.refresh(table)
        
        return table, None
    
    async def update_table(
        self,
        table_id: UUID,
        table_data: CafeteriaTableUpdate,
        user: User
    ) -> Tuple[Optional[CafeteriaTable], Optional[str]]:
        """Update a cafeteria table - Manager only."""
        if not self.can_manage_cafeteria(user):
            return None, "Only CAFETERIA Manager can update cafeteria tables"
        
        table = await self.get_table_by_id(table_id)
        if not table:
            return None, "Cafeteria table not found"
        
        update_data = table_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(table, field, value)
        
        await self.db.commit()
        await self.db.refresh(table)
        
        return table, None
    
    async def delete_table(
        self,
        table_id: UUID,
        user: User
    ) -> Tuple[bool, Optional[str]]:
        """Soft delete a cafeteria table - Manager only."""
        if not self.can_manage_cafeteria(user):
            return False, "Only CAFETERIA Manager can delete cafeteria tables"
        
        table = await self.get_table_by_id(table_id)
        if not table:
            return False, "Cafeteria table not found"
        
        # Check for active bookings
        active_bookings = await self.db.execute(
            select(CafeteriaTableBooking).where(
                and_(
                    CafeteriaTableBooking.table_id == table_id,
                    CafeteriaTableBooking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                    CafeteriaTableBooking.booking_date >= date.today()
                )
            )
        )
        if active_bookings.scalar_one_or_none():
            return False, "Cannot delete table with active bookings"
        
        table.is_active = False
        await self.db.commit()
        
        return True, None
    
    # ==================== Cafeteria Booking ====================
    
    async def get_booking_by_id(self, booking_id: UUID) -> Optional[CafeteriaTableBooking]:
        """Get cafeteria booking by ID."""
        result = await self.db.execute(
            select(CafeteriaTableBooking)
            .options(selectinload(CafeteriaTableBooking.table))
            .where(CafeteriaTableBooking.id == booking_id)
        )
        return result.scalar_one_or_none()
    
    async def check_booking_overlap(
        self,
        table_id: UUID,
        booking_date: date,
        start_time: time,
        end_time: time,
        exclude_booking_id: Optional[UUID] = None
    ) -> bool:
        """Check if there's an overlapping booking."""
        query = select(CafeteriaTableBooking).where(
            and_(
                CafeteriaTableBooking.table_id == table_id,
                CafeteriaTableBooking.booking_date == booking_date,
                CafeteriaTableBooking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                or_(
                    and_(
                        CafeteriaTableBooking.start_time <= start_time,
                        CafeteriaTableBooking.end_time > start_time
                    ),
                    and_(
                        CafeteriaTableBooking.start_time < end_time,
                        CafeteriaTableBooking.end_time >= end_time
                    ),
                    and_(
                        CafeteriaTableBooking.start_time >= start_time,
                        CafeteriaTableBooking.end_time <= end_time
                    )
                )
            )
        )
        
        if exclude_booking_id:
            query = query.where(CafeteriaTableBooking.id != exclude_booking_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def create_booking(
        self,
        booking_data: CafeteriaBookingCreate,
        user: User
    ) -> Tuple[Optional[CafeteriaTableBooking], Optional[str]]:
        """Create a new cafeteria table booking."""
        # Validate table exists and is active
        table = await self.get_table_by_id(booking_data.table_id)
        if not table:
            return None, "Cafeteria table not found"
        if not table.is_active:
            return None, "Cafeteria table is not active"
        
        # Check capacity
        if booking_data.guest_count > table.capacity:
            return None, f"Guest count exceeds table capacity ({table.capacity})"
        
        # Check for overlapping bookings
        has_overlap = await self.check_booking_overlap(
            booking_data.table_id,
            booking_data.booking_date,
            booking_data.start_time,
            booking_data.end_time
        )
        if has_overlap:
            return None, "Time slot overlaps with existing booking"
        
        # Convert guest_names list to comma-separated string if provided
        guest_names_str = None
        if booking_data.guest_names:
            guest_names_str = ",".join(booking_data.guest_names)
        
        booking = CafeteriaTableBooking(
            table_id=booking_data.table_id,
            user_code=user.user_code,
            booking_date=booking_data.booking_date,
            start_time=booking_data.start_time,
            end_time=booking_data.end_time,
            guest_count=booking_data.guest_count,
            guest_names=guest_names_str,
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
        booking_data: CafeteriaBookingUpdate,
        user: User
    ) -> Tuple[Optional[CafeteriaTableBooking], Optional[str]]:
        """Update a cafeteria booking."""
        booking = await self.get_booking_by_id(booking_id)
        if not booking:
            return None, "Booking not found"
        
        # Check ownership or admin access
        if booking.user_code != user.user_code:
            if not self.can_manage_cafeteria(user):
                return None, "Cannot modify another user's booking"
        
        # If updating time, check for overlaps
        if booking_data.start_time or booking_data.end_time:
            start = booking_data.start_time or booking.start_time
            end = booking_data.end_time or booking.end_time
            
            has_overlap = await self.check_booking_overlap(
                booking.table_id,
                booking.booking_date,
                start,
                end,
                exclude_booking_id=booking_id
            )
            if has_overlap:
                return None, "Time slot overlaps with existing booking"
        
        update_data = booking_data.model_dump(exclude_unset=True)
        
        # Handle guest_names conversion
        if 'guest_names' in update_data and update_data['guest_names']:
            update_data['guest_names'] = ",".join(update_data['guest_names'])
        
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
        """Cancel a cafeteria booking."""
        booking = await self.get_booking_by_id(booking_id)
        if not booking:
            return False, "Booking not found"
        
        if booking.user_code != user.user_code:
            if not self.can_manage_cafeteria(user):
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
        table_id: Optional[UUID] = None,
        user_code: Optional[str] = None,
        booking_date: Optional[date] = None,
        status: Optional[BookingStatus] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[CafeteriaTableBooking], int]:
        """List cafeteria bookings with filtering."""
        query = select(CafeteriaTableBooking).options(selectinload(CafeteriaTableBooking.table))
        count_query = select(func.count(CafeteriaTableBooking.id))
        
        conditions = []
        if table_id:
            conditions.append(CafeteriaTableBooking.table_id == table_id)
        if user_code:
            conditions.append(CafeteriaTableBooking.user_code == user_code)
        if booking_date:
            conditions.append(CafeteriaTableBooking.booking_date == booking_date)
        if status:
            conditions.append(CafeteriaTableBooking.status == status)
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.order_by(CafeteriaTableBooking.booking_date.desc(), CafeteriaTableBooking.start_time)
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        bookings = list(result.scalars().all())
        
        return bookings, total
    
    async def get_available_tables(
        self,
        booking_date: date,
        start_time: time,
        end_time: time,
        min_capacity: Optional[int] = None
    ) -> List[CafeteriaTable]:
        """Get all available tables for a time slot."""
        # Get all active tables
        query = select(CafeteriaTable).where(CafeteriaTable.is_active == True)
        
        if min_capacity:
            query = query.where(CafeteriaTable.capacity >= min_capacity)
        
        result = await self.db.execute(query)
        all_tables = list(result.scalars().all())
        
        # Get booked tables for the time slot
        booked_result = await self.db.execute(
            select(CafeteriaTableBooking.table_id).where(
                and_(
                    CafeteriaTableBooking.booking_date == booking_date,
                    CafeteriaTableBooking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
                    or_(
                        and_(
                            CafeteriaTableBooking.start_time <= start_time,
                            CafeteriaTableBooking.end_time > start_time
                        ),
                        and_(
                            CafeteriaTableBooking.start_time < end_time,
                            CafeteriaTableBooking.end_time >= end_time
                        ),
                        and_(
                            CafeteriaTableBooking.start_time >= start_time,
                            CafeteriaTableBooking.end_time <= end_time
                        )
                    )
                )
            )
        )
        booked_table_ids = set(row[0] for row in booked_result.fetchall())
        
        # Filter out booked tables
        available_tables = [t for t in all_tables if t.id not in booked_table_ids]
        
        return available_tables
    
    async def get_cafeteria_stats(self) -> dict:
        """Get cafeteria statistics."""
        # Total tables
        total_result = await self.db.execute(
            select(func.count(CafeteriaTable.id)).where(CafeteriaTable.is_active == True)
        )
        total_tables = total_result.scalar() or 0
        
        # Total capacity
        capacity_result = await self.db.execute(
            select(func.sum(CafeteriaTable.capacity)).where(CafeteriaTable.is_active == True)
        )
        total_capacity = capacity_result.scalar() or 0
        
        # Current bookings (today)
        today = date.today()
        booked_result = await self.db.execute(
            select(func.count(CafeteriaTableBooking.id)).where(
                and_(
                    CafeteriaTableBooking.booking_date == today,
                    CafeteriaTableBooking.status == BookingStatus.CONFIRMED
                )
            )
        )
        booked_tables = booked_result.scalar() or 0
        
        available_tables = total_tables - booked_tables
        occupancy_percentage = (booked_tables / total_tables * 100) if total_tables > 0 else 0
        
        return {
            "total_tables": total_tables,
            "available_tables": available_tables,
            "booked_tables": booked_tables,
            "total_capacity": total_capacity,
            "occupancy_percentage": round(occupancy_percentage, 2)
        }
    
    async def get_today_menu(self) -> dict:
        """Get today's cafeteria menu - placeholder."""
        return {
            "date": date.today().isoformat(),
            "items": [],
            "message": "Menu feature coming soon"
        }
