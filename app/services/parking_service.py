from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from uuid import UUID
from datetime import datetime, timezone

from ..models.parking import ParkingSlot, ParkingAllocation, ParkingHistory
from ..models.user import User
from ..models.enums import ParkingType, ParkingSlotStatus, UserRole, ManagerType, VehicleType
from ..schemas.parking import (
    ParkingSlotCreate, ParkingSlotUpdate,
    ParkingAllocationCreate, ParkingAllocationUpdate, VisitorParkingCreate
)


class ParkingService:
    """
    Parking management service.
    Managed by PARKING Manager.
    Simplified without location fields.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def can_manage_parking(self, user: User) -> bool:
        """Check if user can manage parking slots."""
        if user.role == UserRole.SUPER_ADMIN:
            return True
        if user.role == UserRole.ADMIN:
            return True
        if user.role == UserRole.MANAGER and user.manager_type == ManagerType.PARKING:
            return True
        return False
    
    # ==================== Parking Slot Management ====================
    
    async def get_slot_by_id(self, slot_id: UUID) -> Optional[ParkingSlot]:
        """Get parking slot by ID."""
        result = await self.db.execute(
            select(ParkingSlot).where(ParkingSlot.id == slot_id)
        )
        return result.scalar_one_or_none()
    
    async def get_slot_by_code(self, slot_code: str) -> Optional[ParkingSlot]:
        """Get parking slot by code."""
        result = await self.db.execute(
            select(ParkingSlot).where(ParkingSlot.slot_code == slot_code)
        )
        return result.scalar_one_or_none()
    
    async def list_slots(
        self,
        parking_type: Optional[ParkingType] = None,
        status: Optional[ParkingSlotStatus] = None,
        is_active: Optional[bool] = True,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[ParkingSlot], int]:
        """List parking slots with filtering."""
        query = select(ParkingSlot)
        count_query = select(func.count(ParkingSlot.id))
        
        conditions = []
        if parking_type:
            conditions.append(ParkingSlot.parking_type == parking_type)
        if status:
            conditions.append(ParkingSlot.status == status)
        if is_active is not None:
            conditions.append(ParkingSlot.is_active == is_active)
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        slots = list(result.scalars().all())
        
        return slots, total
    
    async def create_slot(
        self,
        slot_data: ParkingSlotCreate,
        created_by: User
    ) -> Tuple[Optional[ParkingSlot], Optional[str]]:
        """Create a new parking slot - Manager only."""
        if not self.can_manage_parking(created_by):
            return None, "Only PARKING Manager can create parking slots"
        
        slot = ParkingSlot(
            slot_label=slot_data.slot_label,
            parking_type=slot_data.parking_type,
            vehicle_type=slot_data.vehicle_type,
            notes=slot_data.notes,
            created_by_code=created_by.user_code
        )
        
        self.db.add(slot)
        await self.db.commit()
        await self.db.refresh(slot)
        
        return slot, None
    
    async def update_slot(
        self,
        slot_id: UUID,
        slot_data: ParkingSlotUpdate,
        user: User
    ) -> Tuple[Optional[ParkingSlot], Optional[str]]:
        """Update a parking slot - Manager only."""
        if not self.can_manage_parking(user):
            return None, "Only PARKING Manager can update parking slots"
        
        slot = await self.get_slot_by_id(slot_id)
        if not slot:
            return None, "Parking slot not found"
        
        update_data = slot_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(slot, field, value)
        
        await self.db.commit()
        await self.db.refresh(slot)
        
        return slot, None
    
    async def delete_slot(
        self,
        slot_id: UUID,
        user: User
    ) -> Tuple[bool, Optional[str]]:
        """Soft delete a parking slot - Manager only."""
        if not self.can_manage_parking(user):
            return False, "Only PARKING Manager can delete parking slots"
        
        slot = await self.get_slot_by_id(slot_id)
        if not slot:
            return False, "Parking slot not found"
        
        # Check for active allocations
        active_allocation = await self.db.execute(
            select(ParkingAllocation).where(
                and_(
                    ParkingAllocation.slot_id == slot_id,
                    ParkingAllocation.is_active == True
                )
            )
        )
        if active_allocation.scalar_one_or_none():
            return False, "Cannot delete slot with active allocation"
        
        slot.is_active = False
        await self.db.commit()
        
        return True, None
    
    # ==================== Parking Allocation ====================
    
    async def get_allocation_by_id(self, allocation_id: UUID) -> Optional[ParkingAllocation]:
        """Get parking allocation by ID."""
        result = await self.db.execute(
            select(ParkingAllocation)
            .options(selectinload(ParkingAllocation.slot))
            .where(ParkingAllocation.id == allocation_id)
        )
        return result.scalar_one_or_none()
    
    async def check_user_active_parking(self, user_code: str) -> Optional[ParkingAllocation]:
        """Check if user has an active parking allocation."""
        result = await self.db.execute(
            select(ParkingAllocation).where(
                and_(
                    ParkingAllocation.user_code == user_code,
                    ParkingAllocation.is_active == True,
                    ParkingAllocation.exit_time.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def check_slot_availability(self, slot_id: UUID) -> bool:
        """Check if a parking slot is available."""
        result = await self.db.execute(
            select(ParkingAllocation).where(
                and_(
                    ParkingAllocation.slot_id == slot_id,
                    ParkingAllocation.is_active == True,
                    ParkingAllocation.exit_time.is_(None)
                )
            )
        )
        return result.scalar_one_or_none() is None
    
    async def get_available_slots(
        self,
        parking_type: Optional[ParkingType] = None,
        vehicle_type: Optional[VehicleType] = None
    ) -> List[ParkingSlot]:
        """Get all available parking slots."""
        # Get all active slots
        query = select(ParkingSlot).where(
            and_(
                ParkingSlot.is_active == True,
                ParkingSlot.status == ParkingSlotStatus.AVAILABLE
            )
        )
        
        if parking_type:
            query = query.where(ParkingSlot.parking_type == parking_type)
        if vehicle_type:
            query = query.where(
                (ParkingSlot.vehicle_type == vehicle_type) | (ParkingSlot.vehicle_type.is_(None))
            )
        
        result = await self.db.execute(query)
        all_slots = list(result.scalars().all())
        
        # Get occupied slots
        occupied_result = await self.db.execute(
            select(ParkingAllocation.slot_id).where(
                and_(
                    ParkingAllocation.is_active == True,
                    ParkingAllocation.exit_time.is_(None)
                )
            )
        )
        occupied_slot_ids = set(row[0] for row in occupied_result.fetchall())
        
        # Filter out occupied slots
        available_slots = [s for s in all_slots if s.id not in occupied_slot_ids]
        
        return available_slots
    
    async def create_allocation(
        self,
        allocation_data: ParkingAllocationCreate,
        user: User
    ) -> Tuple[Optional[ParkingAllocation], Optional[str]]:
        """Create a new parking allocation for employee - auto-fills vehicle info from user profile."""
        # Check if user has vehicle info
        if not user.vehicle_number:
            return None, "Please update your profile with vehicle number before parking"
        
        # Check if user already has active parking
        existing = await self.check_user_active_parking(user.user_code)
        if existing:
            return None, "You already have an active parking allocation"
        
        # Validate slot exists and is available
        slot = await self.get_slot_by_id(allocation_data.slot_id)
        if not slot:
            return None, "Parking slot not found"
        if not slot.is_active:
            return None, "Parking slot is not active"
        if slot.status == ParkingSlotStatus.MAINTENANCE:
            return None, "Parking slot is under maintenance"
        if slot.parking_type != ParkingType.EMPLOYEE:
            return None, "This slot is not for employees"
        
        # Check slot availability
        is_available = await self.check_slot_availability(allocation_data.slot_id)
        if not is_available:
            return None, "Parking slot is already occupied"
        
        # Auto-fill vehicle info from user profile
        allocation = ParkingAllocation(
            slot_id=allocation_data.slot_id,
            user_code=user.user_code,
            parking_type=ParkingType.EMPLOYEE,
            vehicle_number=user.vehicle_number,  # Auto-filled from user
            vehicle_type=user.vehicle_type or VehicleType.CAR,  # Auto-filled from user
            entry_time=datetime.now(timezone.utc),
            is_active=True,
            notes=allocation_data.notes
        )
        
        # Update slot status
        slot.status = ParkingSlotStatus.OCCUPIED
        
        self.db.add(allocation)
        await self.db.commit()
        await self.db.refresh(allocation)
        
        return allocation, None
    
    async def assign_visitor_slot(
        self,
        visitor_data: VisitorParkingCreate,
        assigned_by: User
    ) -> Tuple[Optional[ParkingAllocation], Optional[str]]:
        """Assign a parking slot to a visitor - Manager only."""
        if not self.can_manage_parking(assigned_by):
            return None, "Only PARKING Manager can assign visitor parking"
        
        # Get slot or auto-assign
        if visitor_data.slot_id:
            slot = await self.get_slot_by_id(visitor_data.slot_id)
            if not slot:
                return None, "Parking slot not found"
        else:
            # Auto-assign available visitor slot
            available = await self.get_available_slots(
                parking_type=ParkingType.VISITOR,
                vehicle_type=visitor_data.vehicle_type
            )
            if not available:
                return None, "No visitor parking slots available"
            slot = available[0]
        
        if not slot.is_active:
            return None, "Parking slot is not active"
        
        # Check slot availability
        is_available = await self.check_slot_availability(slot.id)
        if not is_available:
            return None, "Parking slot is already occupied"
        
        allocation = ParkingAllocation(
            slot_id=slot.id,
            parking_type=ParkingType.VISITOR,
            visitor_name=visitor_data.visitor_name,
            visitor_phone=visitor_data.visitor_phone,
            visitor_company=visitor_data.visitor_company,
            vehicle_number=visitor_data.vehicle_number,
            vehicle_type=visitor_data.vehicle_type,
            entry_time=datetime.now(timezone.utc),
            is_active=True,
            notes=visitor_data.notes
        )
        
        # Update slot status
        slot.status = ParkingSlotStatus.OCCUPIED
        
        self.db.add(allocation)
        await self.db.commit()
        await self.db.refresh(allocation)
        
        return allocation, None
    
    async def record_exit(
        self,
        allocation_id: UUID,
        user: User
    ) -> Tuple[Optional[ParkingAllocation], Optional[str]]:
        """Record parking exit."""
        allocation = await self.get_allocation_by_id(allocation_id)
        if not allocation:
            return None, "Allocation not found"
        
        if not allocation.is_active:
            return None, "Allocation is not active"
        
        # Check permission - user can release own parking, or manager can release any
        if allocation.user_code != user.user_code:
            if not self.can_manage_parking(user):
                return None, "Cannot release another user's parking"
        
        allocation.exit_time = datetime.now(timezone.utc)
        allocation.is_active = False
        
        # Update slot status
        slot = await self.get_slot_by_id(allocation.slot_id)
        if slot:
            slot.status = ParkingSlotStatus.AVAILABLE
        
        # Create history record
        duration = (allocation.exit_time - allocation.entry_time).total_seconds() / 60
        history = ParkingHistory(
            allocation_id=allocation.id,
            slot_id=allocation.slot_id,
            slot_code=slot.slot_code if slot else "UNKNOWN",
            parking_type=allocation.parking_type,
            user_code=allocation.user_code,
            visitor_name=allocation.visitor_name,
            vehicle_number=allocation.vehicle_number,
            vehicle_type=allocation.vehicle_type,
            entry_time=allocation.entry_time,
            exit_time=allocation.exit_time,
            duration_minutes=int(duration)
        )
        
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(allocation)
        
        return allocation, None
    
    async def list_allocations(
        self,
        slot_id: Optional[UUID] = None,
        user_code: Optional[str] = None,
        parking_type: Optional[ParkingType] = None,
        is_active: Optional[bool] = True,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[ParkingAllocation], int]:
        """List parking allocations with filtering."""
        query = select(ParkingAllocation).options(selectinload(ParkingAllocation.slot))
        count_query = select(func.count(ParkingAllocation.id))
        
        conditions = []
        if slot_id:
            conditions.append(ParkingAllocation.slot_id == slot_id)
        if user_code:
            conditions.append(ParkingAllocation.user_code == user_code)
        if parking_type:
            conditions.append(ParkingAllocation.parking_type == parking_type)
        if is_active is not None:
            conditions.append(ParkingAllocation.is_active == is_active)
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.order_by(ParkingAllocation.entry_time.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        allocations = list(result.scalars().all())
        
        return allocations, total
    
    async def list_visitor_allocations(
        self,
        is_active: Optional[bool] = True,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[ParkingAllocation], int]:
        """List visitor parking allocations."""
        return await self.list_allocations(
            parking_type=ParkingType.VISITOR,
            is_active=is_active,
            page=page,
            page_size=page_size
        )
    
    async def get_parking_stats(self) -> dict:
        """Get parking statistics."""
        # Total slots
        total_result = await self.db.execute(
            select(func.count(ParkingSlot.id)).where(ParkingSlot.is_active == True)
        )
        total_slots = total_result.scalar() or 0
        
        # Employee slots
        emp_result = await self.db.execute(
            select(func.count(ParkingSlot.id)).where(
                and_(
                    ParkingSlot.is_active == True,
                    ParkingSlot.parking_type == ParkingType.EMPLOYEE
                )
            )
        )
        employee_slots = emp_result.scalar() or 0
        
        # Visitor slots
        visitor_slots = total_slots - employee_slots
        
        # Occupied slots
        occupied_result = await self.db.execute(
            select(func.count(ParkingAllocation.id)).where(
                and_(
                    ParkingAllocation.is_active == True,
                    ParkingAllocation.exit_time.is_(None)
                )
            )
        )
        occupied_slots = occupied_result.scalar() or 0
        
        available_slots = total_slots - occupied_slots
        occupancy_percentage = (occupied_slots / total_slots * 100) if total_slots > 0 else 0
        
        return {
            "total_slots": total_slots,
            "employee_slots": employee_slots,
            "visitor_slots": visitor_slots,
            "occupied_slots": occupied_slots,
            "available_slots": available_slots,
            "occupancy_percentage": round(occupancy_percentage, 2)
        }
