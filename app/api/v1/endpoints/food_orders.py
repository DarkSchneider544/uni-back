from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID

from ....core.database import get_db
from ....core.dependencies import get_current_active_user, require_admin_or_above
from ....models.user import User
from ....models.enums import OrderStatus, UserRole, ManagerType
from ....schemas.food import (
    FoodItemCreate, FoodItemUpdate, FoodItemResponse,
    FoodOrderCreate, FoodOrderResponse, FoodOrderStatusUpdate
)
from ....schemas.base import APIResponse, PaginatedResponse
from ....services.food_service import FoodService
from ....utils.response import create_response, create_paginated_response

router = APIRouter()


def require_cafeteria_manager(user: User) -> None:
    """Check if user is Cafeteria Manager, Admin, or Super Admin."""
    if user.role == UserRole.SUPER_ADMIN:
        return
    if user.role == UserRole.ADMIN:
        return
    if user.role == UserRole.MANAGER and user.manager_type == ManagerType.CAFETERIA:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only Cafeteria Manager can perform this action"
    )


# Food Items
@router.post("/items", response_model=APIResponse[FoodItemResponse])
async def create_food_item(
    item_data: FoodItemCreate,
    current_user: User = Depends(require_admin_or_above),
    db: AsyncSession = Depends(get_db)
):
    """Create a new food item. Cafeteria Admin only."""
    require_cafeteria_manager(current_user)
    food_service = FoodService(db)
    item, error = await food_service.create_food_item(item_data, current_user)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return create_response(
        data=FoodItemResponse.model_validate(item),
        message="Food item created successfully"
    )


@router.get("/items", response_model=PaginatedResponse[FoodItemResponse])
async def list_food_items(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    is_available: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List food items."""
    food_service = FoodService(db)
    items, total = await food_service.list_food_items(
        category=category,
        is_available=is_available,
        page=page,
        page_size=page_size
    )
    
    return create_paginated_response(
        data=[FoodItemResponse.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        message="Food items retrieved successfully"
    )


@router.get("/items/{item_id}", response_model=APIResponse[FoodItemResponse])
async def get_food_item(
    item_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get food item by ID."""
    food_service = FoodService(db)
    item = await food_service.get_food_item_by_id(item_id)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food item not found"
        )
    
    return create_response(
        data=FoodItemResponse.model_validate(item),
        message="Food item retrieved successfully"
    )


@router.put("/items/{item_id}", response_model=APIResponse[FoodItemResponse])
async def update_food_item(
    item_id: UUID,
    item_data: FoodItemUpdate,
    current_user: User = Depends(require_admin_or_above),
    db: AsyncSession = Depends(get_db)
):
    """Update a food item. Cafeteria Admin only."""
    require_cafeteria_manager(current_user)
    food_service = FoodService(db)
    item, error = await food_service.update_food_item(item_id, item_data)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return create_response(
        data=FoodItemResponse.model_validate(item),
        message="Food item updated successfully"
    )


# Orders
@router.get("/my-orders", response_model=PaginatedResponse[FoodOrderResponse])
async def get_my_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[OrderStatus] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's food orders."""
    food_service = FoodService(db)
    orders, total = await food_service.list_orders(
        user_code=current_user.user_code,
        status=status,
        page=page,
        page_size=page_size
    )
    
    return create_paginated_response(
        data=[FoodOrderResponse.model_validate(o) for o in orders],
        total=total,
        page=page,
        page_size=page_size,
        message="Your orders retrieved successfully"
    )


@router.post("/orders", response_model=APIResponse[FoodOrderResponse])
async def create_food_order(
    order_data: FoodOrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new food order."""
    food_service = FoodService(db)
    order, error = await food_service.create_order(order_data, current_user)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return create_response(
        data=FoodOrderResponse.model_validate(order),
        message="Food order created successfully"
    )


@router.get("/orders", response_model=PaginatedResponse[FoodOrderResponse])
async def list_food_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_code: Optional[str] = None,
    status: Optional[OrderStatus] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """List food orders. Regular users can only see their own orders."""
    # Only Super Admin, Admin, and Cafeteria Manager can see all orders
    # Regular users (Employee, Team Lead) can only see their own orders
    is_cafeteria_manager = (
        current_user.role == UserRole.SUPER_ADMIN or
        current_user.role == UserRole.ADMIN or
        (current_user.role == UserRole.MANAGER and current_user.manager_type == ManagerType.CAFETERIA)
    )
    if not is_cafeteria_manager:
        # Regular users can only see their own orders
        user_code = current_user.user_code
    
    food_service = FoodService(db)
    orders, total = await food_service.list_orders(
        user_code=user_code,
        status=status,
        page=page,
        page_size=page_size
    )
    
    return create_paginated_response(
        data=[FoodOrderResponse.model_validate(o) for o in orders],
        total=total,
        page=page,
        page_size=page_size,
        message="Food orders retrieved successfully"
    )


@router.get("/orders/{order_id}", response_model=APIResponse[FoodOrderResponse])
async def get_food_order(
    order_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get food order by ID. Users can only view their own orders unless they are admin/manager."""
    food_service = FoodService(db)
    order = await food_service.get_order_by_id(order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food order not found"
        )
    
    # RBAC check - regular users can only see their own orders
    is_cafeteria_manager = (
        current_user.role == UserRole.SUPER_ADMIN or
        current_user.role == UserRole.ADMIN or
        (current_user.role == UserRole.MANAGER and current_user.manager_type == ManagerType.CAFETERIA)
    )
    if not is_cafeteria_manager and order.user_code != current_user.user_code:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own orders"
        )
    
    return create_response(
        data=FoodOrderResponse.model_validate(order),
        message="Food order retrieved successfully"
    )


@router.post("/orders/{order_id}/cancel", response_model=APIResponse[FoodOrderResponse])
async def cancel_my_order(
    order_id: UUID,
    cancellation_reason: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel own food order. Users can only cancel orders that are still PENDING."""
    food_service = FoodService(db)
    order = await food_service.get_order_by_id(order_id)
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food order not found"
        )
    
    # Users can only cancel their own orders
    if order.user_code != current_user.user_code:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own orders"
        )
    
    # Users can only cancel PENDING orders
    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel order with status '{order.status.value}'. Only PENDING orders can be cancelled."
        )
    
    order, error = await food_service.update_order_status(
        order_id,
        OrderStatus.CANCELLED,
        cancellation_reason=cancellation_reason or "Cancelled by user"
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return create_response(
        data=FoodOrderResponse.model_validate(order),
        message="Order cancelled successfully"
    )


@router.put("/orders/{order_id}/status", response_model=APIResponse[FoodOrderResponse])
async def update_order_status(
    order_id: UUID,
    status_data: FoodOrderStatusUpdate,
    current_user: User = Depends(require_admin_or_above),
    db: AsyncSession = Depends(get_db)
):
    """Update food order status. Cafeteria Admin only."""
    require_cafeteria_manager(current_user)
    
    food_service = FoodService(db)
    order, error = await food_service.update_order_status(
        order_id,
        status_data.status,
        notes=status_data.notes
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return create_response(
        data=FoodOrderResponse.model_validate(order),
        message="Order status updated successfully"
    )


@router.get("/dashboard/stats", response_model=APIResponse[dict])
async def get_cafeteria_stats(
    current_user: User = Depends(require_admin_or_above),
    db: AsyncSession = Depends(get_db)
):
    """Get cafeteria dashboard statistics. Cafeteria Admin only."""
    require_cafeteria_manager(current_user)
    
    food_service = FoodService(db)
    stats = await food_service.get_dashboard_stats()
    
    return create_response(
        data=stats,
        message="Dashboard statistics retrieved successfully"
    )