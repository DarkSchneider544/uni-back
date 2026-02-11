from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID
from datetime import date

from ....core.database import get_db
from ....core.dependencies import get_current_active_user, require_team_lead_or_above, require_manager_or_above
from ....models.user import User
from ....models.enums import LeaveType, LeaveStatus
from ....models.leave import LeaveRequest
from ....schemas.leave import (
    LeaveRequestCreate, LeaveRequestResponse, LeaveBalanceResponse, LeaveApproval
)
from ....schemas.base import APIResponse, PaginatedResponse
from ....services.leave_service import LeaveService
from ....utils.response import create_response, create_paginated_response

router = APIRouter()


def build_leave_request_response(leave_request: LeaveRequest) -> dict:
    """Build response dict from LeaveRequest model to avoid lazy-loading issues."""
    return {
        "id": leave_request.id,
        "user_code": leave_request.user_code,
        "leave_type": leave_request.leave_type.code if leave_request.leave_type else None,
        "leave_type_name": leave_request.leave_type.name if leave_request.leave_type else None,
        "start_date": leave_request.start_date,
        "end_date": leave_request.end_date,
        "total_days": leave_request.total_days,
        "is_half_day": leave_request.is_half_day,
        "half_day_type": leave_request.half_day_type,
        "reason": leave_request.reason,
        "status": leave_request.status,
        "level1_approver_code": leave_request.level1_approver_code,
        "level1_approver_name": None,  # Could be fetched if needed
        "level1_approved_at": leave_request.level1_approved_at,
        "level1_notes": leave_request.level1_notes,
        "final_approver_code": leave_request.final_approver_code,
        "final_approver_name": None,  # Could be fetched if needed
        "final_approved_at": leave_request.final_approved_at,
        "final_approval_notes": leave_request.final_approval_notes,
        "rejection_reason": leave_request.rejection_reason,
        "rejected_by_code": leave_request.rejected_by_code,
        "rejected_at": leave_request.rejected_at,
        "cancelled_at": leave_request.cancelled_at,
        "cancellation_reason": leave_request.cancellation_reason,
        "emergency_contact": leave_request.emergency_contact,
        "emergency_phone": leave_request.emergency_phone,
        "created_at": leave_request.created_at,
        "updated_at": leave_request.updated_at,
    }


@router.post("/requests", response_model=APIResponse[LeaveRequestResponse])
async def create_leave_request(
    request_data: LeaveRequestCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new leave request."""
    leave_service = LeaveService(db)
    leave_request, error = await leave_service.create_leave_request(
        current_user,
        request_data.leave_type,
        request_data.start_date,
        request_data.end_date,
        request_data.reason
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return create_response(
        data=build_leave_request_response(leave_request),
        message="Leave request created successfully"
    )


@router.get("/requests", response_model=PaginatedResponse[LeaveRequestResponse])
async def list_leave_requests(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: Optional[UUID] = None,
    status: Optional[LeaveStatus] = None,
    leave_type: Optional[LeaveType] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List leave requests."""
    from ....models.enums import UserRole
    
    # Non-managers can only see their own requests
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MANAGER, UserRole.TEAM_LEAD]:
        user_id = current_user.id
    
    leave_service = LeaveService(db)
    requests, total = await leave_service.list_leave_requests(
        user_id=user_id,
        status=status,
        leave_type=leave_type,
        page=page,
        page_size=page_size
    )
    
    return create_paginated_response(
        data=[build_leave_request_response(r) for r in requests],
        total=total,
        page=page,
        page_size=page_size,
        message="Leave requests retrieved successfully"
    )


@router.get("/requests/{request_id}", response_model=APIResponse[LeaveRequestResponse])
async def get_leave_request(
    request_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get leave request by ID."""
    leave_service = LeaveService(db)
    leave_request = await leave_service.get_leave_request_by_id(request_id)
    
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )
    
    return create_response(
        data=build_leave_request_response(leave_request),
        message="Leave request retrieved successfully"
    )


@router.post("/requests/{request_id}/approve-level1", response_model=APIResponse[LeaveRequestResponse])
async def approve_leave_level1(
    request_id: UUID,
    approval_data: LeaveApproval,
    current_user: User = Depends(require_team_lead_or_above),
    db: AsyncSession = Depends(get_db)
):
    """Approve leave request (Level 1 - Team Lead). Team Lead+ required."""
    leave_service = LeaveService(db)
    
    if approval_data.action == "approve":
        leave_request, error = await leave_service.approve_level1(
            current_user, request_id, approval_data.notes
        )
    else:
        if not approval_data.rejection_reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rejection reason is required"
            )
        leave_request, error = await leave_service.reject_leave(
            current_user, request_id, approval_data.rejection_reason
        )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return create_response(
        data=build_leave_request_response(leave_request),
        message=f"Leave request {approval_data.action}d successfully"
    )


@router.post("/requests/{request_id}/approve-final", response_model=APIResponse[LeaveRequestResponse])
async def approve_leave_final(
    request_id: UUID,
    approval_data: LeaveApproval,
    current_user: User = Depends(require_manager_or_above),
    db: AsyncSession = Depends(get_db)
):
    """Final approval for leave request. Manager+ required."""
    leave_service = LeaveService(db)
    
    if approval_data.action == "approve":
        leave_request, error = await leave_service.approve_final(
            current_user, request_id, approval_data.notes
        )
    else:
        if not approval_data.rejection_reason:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rejection reason is required"
            )
        leave_request, error = await leave_service.reject_leave(
            current_user, request_id, approval_data.rejection_reason
        )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return create_response(
        data=build_leave_request_response(leave_request),
        message=f"Leave request {approval_data.action}d successfully"
    )


@router.post("/requests/{request_id}/cancel", response_model=APIResponse[LeaveRequestResponse])
async def cancel_leave_request(
    request_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a leave request."""
    leave_service = LeaveService(db)
    leave_request, error = await leave_service.cancel_leave(current_user, request_id)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return create_response(
        data=build_leave_request_response(leave_request),
        message="Leave request cancelled successfully"
    )


@router.get("/balance", response_model=APIResponse[List[LeaveBalanceResponse]])
async def get_my_leave_balance(
    year: int = Query(default=None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's leave balance."""
    from datetime import datetime
    
    if year is None:
        year = datetime.now().year
    
    leave_service = LeaveService(db)
    
    # Initialize balance if not exists - use user_code
    await leave_service.initialize_leave_balance(current_user.user_code, year)
    
    balances = await leave_service.get_all_balances(current_user.user_code, year)
    
    balance_responses = []
    for balance in balances:
        resp = LeaveBalanceResponse(
            id=balance.id,
            user_code=balance.user_code,
            leave_type=balance.leave_type.code if balance.leave_type else None,
            year=balance.year,
            total_days=balance.total_days,
            used_days=balance.used_days,
            pending_days=balance.pending_days,
            available_days=balance.available_days
        )
        balance_responses.append(resp)
    
    return create_response(
        data=balance_responses,
        message="Leave balance retrieved successfully"
    )


@router.get("/balance/{user_id}", response_model=APIResponse[List[LeaveBalanceResponse]])
async def get_user_leave_balance(
    user_id: UUID,
    year: int = Query(default=None),
    current_user: User = Depends(require_manager_or_above),
    db: AsyncSession = Depends(get_db)
):
    """Get a user's leave balance. Manager+ required."""
    from datetime import datetime
    from sqlalchemy import select
    from ....models.user import User as UserModel
    
    if year is None:
        year = datetime.now().year
    
    # Lookup user by UUID to get user_code
    user_result = await db.execute(
        select(UserModel).where(UserModel.id == user_id)
    )
    target_user = user_result.scalar_one_or_none()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    leave_service = LeaveService(db)
    balances = await leave_service.get_all_balances(target_user.user_code, year)
    
    balance_responses = []
    for balance in balances:
        resp = LeaveBalanceResponse(
            id=balance.id,
            user_code=balance.user_code,
            leave_type=balance.leave_type.code if balance.leave_type else None,
            year=balance.year,
            total_days=balance.total_days,
            used_days=balance.used_days,
            pending_days=balance.pending_days,
            available_days=balance.available_days
        )
        balance_responses.append(resp)
    
    return create_response(
        data=balance_responses,
        message="Leave balance retrieved successfully"
    )