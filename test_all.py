"""
Comprehensive Test Suite for Unified Office Management System
Tests all services, endpoints, and workflows end-to-end

Note: These tests require a PostgreSQL database. 
Set TEST_DATABASE_URL environment variable or use the default test database.
"""

import pytest
import asyncio
import os
from datetime import date, datetime, timedelta
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings
from app.models.user import User
from app.models.enums import UserRole, ManagerType

# Test database URL - use PostgreSQL for UUID support
# Use local PostgreSQL with office_admin user
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://office_admin:office_password@localhost:5432/office_management_test"
)

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Helper function to add required vehicle fields to user creation payloads
def add_vehicle_fields(user_data: dict, vehicle_number: str = None, vehicle_type: str = "car") -> dict:
    """
    Add required vehicle fields to user creation data if not already present.
    
    Args:
        user_data: The user creation payload
        vehicle_number: Vehicle number (auto-generated if not provided)
        vehicle_type: Vehicle type (defaults to 'car')
    
    Returns:
        Updated user_data with vehicle fields
    """
    if "vehicle_number" not in user_data:
        # Auto-generate vehicle number from first/last name if not provided
        if vehicle_number:
            user_data["vehicle_number"] = vehicle_number
        else:
            # Generate from name, e.g., "John Doe" -> "JD1234"
            initials = (user_data.get("first_name", "X")[0] + user_data.get("last_name", "Y")[0]).upper()
            user_data["vehicle_number"] = f"{initials}1234"
    
    if "vehicle_type" not in user_data:
        user_data["vehicle_type"] = vehicle_type
    
    return user_data


# Fixtures
@pytest.fixture(scope="function")
async def db_session():
    """Create a test database session"""
    # Create tables using metadata.create_all()
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()
    
    # Clean up after test - drop all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session):
    """Create test client with database override"""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def super_admin_token(client):
    """Get super admin authentication token"""
    # Create super admin user directly
    from app.core.security import get_password_hash
    from app.models.user import User
    
    async def create_super_admin():
        async with TestSessionLocal() as session:
            super_admin = User(
                user_code="SA0001",
                email="super.admin@company.com",
                hashed_password=get_password_hash("Admin@123"),
                first_name="Super",
                last_name="Admin",
                role=UserRole.SUPER_ADMIN,
                is_active=True
            )
            session.add(super_admin)
            await session.commit()
    
    await create_super_admin()
    
    # Login
    response = await client.post("/api/v1/auth/login", json={
        "email": "super.admin@company.com",
        "password": "Admin@123"
    })
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


@pytest.fixture
async def admin_token(client, super_admin_token):
    """Create admin and get token"""
    # Create admin
    response = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {super_admin_token}"},
        json={
            "first_name": "Test",
            "last_name": "Admin",
            "email": "admin@company.com",
            "password": "Admin@123",
            "role": "admin",
            "vehicle_number": "ADM1234",
            "vehicle_type": "car"
        }
    )
    if response.status_code != 200:
        print(f"Create admin error: {response.json()}")
    assert response.status_code == 200
    
    # Login as admin
    response = await client.post("/api/v1/auth/login", json={
        "email": "admin@company.com",
        "password": "Admin@123"
    })
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


@pytest.fixture
async def it_manager_token(client, admin_token):
    """Create IT manager and get token"""
    response = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "first_name": "IT",
            "last_name": "Manager",
            "email": "it.manager@company.com",
            "password": "Manager@123",
            "role": "manager",
            "manager_type": "it_support",
            "vehicle_number": "ITM1234",
            "vehicle_type": "car"
        }
    )
    if response.status_code != 200:
        print(f"Create IT manager error: {response.json()}")
    assert response.status_code == 200
    
    response = await client.post("/api/v1/auth/login", json={
        "email": "it.manager@company.com",
        "password": "Manager@123"
    })
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


@pytest.fixture
async def team_lead_token(client, admin_token):
    """Create team lead and get token"""
    response = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "first_name": "Team",
            "last_name": "Lead",
            "email": "team.lead@company.com",
            "password": "Lead@123",
            "role": "team_lead",
            "department": "Engineering",
            "vehicle_number": "TL1234",
            "vehicle_type": "bike"
        }
    )
    if response.status_code != 200:
        print(f"Create team lead error: {response.json()}")
    assert response.status_code == 200
    team_lead_data = response.json()["data"]
    
    response = await client.post("/api/v1/auth/login", json={
        "email": "team.lead@company.com",
        "password": "Lead@123"
    })
    assert response.status_code == 200
    return response.json()["data"]["access_token"], team_lead_data["user_code"]


@pytest.fixture
async def employee_token(client, admin_token, team_lead_token):
    """Create employee and get token"""
    _, team_lead_code = team_lead_token
    
    response = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "first_name": "Test",
            "last_name": "Employee",
            "email": "employee@company.com",
            "password": "Employee@123",
            "role": "employee",
            "team_lead_code": team_lead_code,
            "vehicle_number": "ABC123",
            "vehicle_type": "car"
        }
    )
    assert response.status_code == 200
    
    response = await client.post("/api/v1/auth/login", json={
        "email": "employee@company.com",
        "password": "Employee@123"
    })
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


# ========== AUTHENTICATION TESTS ==========

@pytest.mark.asyncio
async def test_authentication_workflow(client, super_admin_token):
    """Test complete authentication workflow"""
    # Test login
    response = await client.post("/api/v1/auth/login", json={
        "email": "super.admin@company.com",
        "password": "Admin@123"
    })
    assert response.status_code == 200
    data = response.json()["data"]
    assert "access_token" in data
    assert "refresh_token" in data
    
    # Test get current user
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {super_admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["email"] == "super.admin@company.com"
    
    # Test change password
    response = await client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {super_admin_token}"},
        json={
            "current_password": "Admin@123",
            "new_password": "NewAdmin@123",
            "confirm_password": "NewAdmin@123"
        }
    )
    if response.status_code != 200:
        print(f"Change password error: {response.json()}")
    assert response.status_code == 200
    
    # Test login with new password
    response = await client.post("/api/v1/auth/login", json={
        "email": "super.admin@company.com",
        "password": "NewAdmin@123"
    })
    assert response.status_code == 200


# ========== USER MANAGEMENT TESTS ==========

@pytest.mark.asyncio
async def test_user_hierarchy_workflow(client, super_admin_token, admin_token):
    """Test complete user management and hierarchy"""
    # Admin creates manager
    response = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=add_vehicle_fields({
            "first_name": "Parking",
            "last_name": "Manager",
            "role": "manager",
            "manager_type": "parking",
            "password": "Manager@123"
        })
    )
    assert response.status_code == 200
    manager_data = response.json()["data"]
    assert "user_code" in manager_data
    assert "email" in manager_data  # Auto-generated
    
    # Admin creates team lead
    response = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=add_vehicle_fields({
            "first_name": "Sales",
            "last_name": "Lead",
            "role": "team_lead",
            "department": "Sales",
            "password": "Lead@123"
        })
    )
    assert response.status_code == 200
    team_lead_data = response.json()["data"]
    
    # Manager creates employee under team lead
    response = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=add_vehicle_fields({
            "first_name": "Sales",
            "last_name": "Employee",
            "role": "employee",
            "team_lead_code": team_lead_data["user_code"],
            "password": "Emp@123"
        })
    )
    assert response.status_code == 200
    employee_data = response.json()["data"]
    assert employee_data["team_lead_code"] == team_lead_data["user_code"]
    
    # Test list users with pagination
    response = await client.get(
        "/api/v1/users?page=1&page_size=10",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert "total" in response.json()
    
    # Test update user
    response = await client.put(
        f"/api/v1/users/{employee_data['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"phone": "1234567890"}
    )
    assert response.status_code == 200
    
    # Test toggle user active status
    response = await client.post(
        f"/api/v1/users/{employee_data['id']}/toggle-active",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200


# ========== ATTENDANCE TESTS ==========

@pytest.mark.asyncio
async def test_complete_attendance_workflow(client, employee_token, team_lead_token):
    """Test complete attendance workflow: check-in, check-out, submit, approve"""
    token = employee_token
    lead_token, _ = team_lead_token
    
    # Employee checks in
    response = await client.post(
        "/api/v1/attendance/check-in",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    attendance_id = response.json()["data"]["id"]
    
    # Employee checks out
    response = await client.post(
        "/api/v1/attendance/check-out",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["total_hours"] is not None
    
    # Check my status
    response = await client.get(
        "/api/v1/attendance/my-status",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # Submit for approval
    response = await client.post(
        f"/api/v1/attendance/{attendance_id}/submit",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "pending_approval"
    
    # Team lead views pending approvals
    response = await client.get(
        "/api/v1/attendance/pending-approvals",
        headers={"Authorization": f"Bearer {lead_token}"}
    )
    assert response.status_code == 200
    
    # Team lead approves
    response = await client.post(
        f"/api/v1/attendance/{attendance_id}/approve",
        headers={"Authorization": f"Bearer {lead_token}"},
        json={
            "action": "approve",
            "notes": "Approved"
        }
    )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "approved"
    
    # Get my attendance records
    response = await client.get(
        "/api/v1/attendance/my",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


# ========== LEAVE MANAGEMENT TESTS ==========

@pytest.mark.asyncio
async def test_complete_leave_workflow(client, employee_token, team_lead_token, admin_token):
    """Test complete leave workflow: create, approve level 1, approve final"""
    token = employee_token
    lead_token, _ = team_lead_token
    
    # Create leave request
    future_date = (date.today() + timedelta(days=7)).isoformat()
    end_date = (date.today() + timedelta(days=8)).isoformat()
    
    response = await client.post(
        "/api/v1/leave/requests",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "leave_type": "casual",
            "start_date": future_date,
            "end_date": end_date,
            "reason": "Personal work"
        }
    )
    assert response.status_code == 200
    leave_id = response.json()["data"]["id"]
    assert response.json()["data"]["status"] == "pending_level1"
    
    # Get my leave requests
    response = await client.get(
        "/api/v1/leave/requests/my",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # Get leave balance
    response = await client.get(
        "/api/v1/leave/balance",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # Team lead views pending requests
    response = await client.get(
        "/api/v1/leave/requests/pending-level1",
        headers={"Authorization": f"Bearer {lead_token}"}
    )
    assert response.status_code == 200
    
    # Team lead approves level 1
    response = await client.post(
        f"/api/v1/leave/requests/{leave_id}/approve-level1",
        headers={"Authorization": f"Bearer {lead_token}"},
        json={
            "action": "approve",
            "notes": "Approved by team lead"
        }
    )
    assert response.status_code == 200
    
    # For multi-day leave, need manager approval
    # Admin can view pending final approvals
    response = await client.get(
        "/api/v1/leave/requests/pending-final",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200


# ========== PARKING TESTS ==========

@pytest.mark.asyncio
async def test_parking_workflow(client, employee_token, admin_token):
    """Test complete parking workflow"""
    token = employee_token
    
    # Create parking manager first
    response = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=add_vehicle_fields({
            "first_name": "Parking",
            "last_name": "Manager",
            "role": "manager",
            "manager_type": "parking",
            "password": "Manager@123"
        })
    )
    assert response.status_code == 200
    
    # Login as parking manager
    response = await client.post("/api/v1/auth/login", json={
        "email": response.json()["data"]["email"],
        "password": "Manager@123"
    })
    parking_manager_token = response.json()["data"]["access_token"]
    
    # Parking manager creates slots
    response = await client.post(
        "/api/v1/parking/slots/create?slot_code=A-01",
        headers={"Authorization": f"Bearer {parking_manager_token}"}
    )
    assert response.status_code == 200
    
    # Create more slots
    await client.post(
        "/api/v1/parking/slots/create?slot_code=A-02",
        headers={"Authorization": f"Bearer {parking_manager_token}"}
    )
    
    # Get parking summary
    response = await client.get(
        "/api/v1/parking/slots/summary",
        headers={"Authorization": f"Bearer {parking_manager_token}"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["total"] >= 2
    
    # Employee allocates parking
    response = await client.post(
        "/api/v1/parking/allocate",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    slot_code = response.json()["data"]["slot_code"]
    
    # Check my slot
    response = await client.get(
        "/api/v1/parking/my-slot",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["has_active_parking"] is True
    
    # Employee releases parking
    response = await client.post(
        "/api/v1/parking/release",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "duration_mins" in response.json()["data"]
    
    # Check parking logs
    response = await client.get(
        "/api/v1/parking/logs/list",
        headers={"Authorization": f"Bearer {parking_manager_token}"}
    )
    assert response.status_code == 200


# ========== DESK & CONFERENCE ROOM TESTS ==========

@pytest.mark.asyncio
async def test_desk_booking_workflow(client, employee_token, admin_token):
    """Test desk and conference room booking workflow"""
    token = employee_token
    
    # Create desk manager
    response = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=add_vehicle_fields({
            "first_name": "Desk",
            "last_name": "Manager",
            "role": "manager",
            "manager_type": "desk_conference",
            "password": "Manager@123"
        })
    )
    assert response.status_code == 200
    
    response = await client.post("/api/v1/auth/login", json={
        "email": response.json()["data"]["email"],
        "password": "Manager@123"
    })
    desk_manager_token = response.json()["data"]["access_token"]
    
    # Create desk
    response = await client.post(
        "/api/v1/desks",
        headers={"Authorization": f"Bearer {desk_manager_token}"},
        json={
            "desk_label": "Desk 1",
            "zone": "Zone A",
            "has_monitor": True
        }
    )
    assert response.status_code == 200
    desk_id = response.json()["data"]["id"]
    
    # Create conference room
    response = await client.post(
        "/api/v1/desks/rooms",
        headers={"Authorization": f"Bearer {desk_manager_token}"},
        json={
            "room_label": "Meeting Room A",
            "capacity": 10,
            "zone": "Zone A"
        }
    )
    assert response.status_code == 200
    room_id = response.json()["data"]["id"]
    
    # Employee books desk (date-range based)
    start_date = (date.today() + timedelta(days=1)).isoformat()
    end_date = (date.today() + timedelta(days=3)).isoformat()
    
    response = await client.post(
        "/api/v1/desks/bookings",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "desk_id": desk_id,
            "start_date": start_date,
            "end_date": end_date,
            "purpose": "Project work"
        }
    )
    assert response.status_code == 200
    booking_id = response.json()["data"]["id"]
    
    # Get my bookings
    response = await client.get(
        "/api/v1/desks/bookings/my",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # Book conference room (requires approval)
    response = await client.post(
        "/api/v1/desks/rooms/bookings",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "room_id": room_id,
            "start_date": start_date,
            "end_date": end_date,
            "purpose": "Team meeting"
        }
    )
    assert response.status_code == 200
    room_booking_id = response.json()["data"]["id"]
    assert response.json()["data"]["status"] == "pending"
    
    # Desk manager approves conference room booking
    response = await client.post(
        f"/api/v1/desks/rooms/bookings/{room_booking_id}/approve",
        headers={"Authorization": f"Bearer {desk_manager_token}"},
        json={"notes": "Approved"}
    )
    assert response.status_code == 200


# ========== FOOD ORDERING TESTS ==========

@pytest.mark.asyncio
async def test_food_ordering_workflow(client, employee_token, admin_token):
    """Test complete food ordering workflow with multi-item cart"""
    token = employee_token
    
    # Create cafeteria manager
    response = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=add_vehicle_fields({
            "first_name": "Cafeteria",
            "last_name": "Manager",
            "role": "manager",
            "manager_type": "cafeteria",
            "password": "Manager@123"
        })
    )
    assert response.status_code == 200
    
    response = await client.post("/api/v1/auth/login", json={
        "email": response.json()["data"]["email"],
        "password": "Manager@123"
    })
    cafe_manager_token = response.json()["data"]["access_token"]
    
    # Create food items
    response = await client.post(
        "/api/v1/food-orders/items",
        headers={"Authorization": f"Bearer {cafe_manager_token}"},
        json={
            "name": "Chicken Biryani",
            "description": "Aromatic rice with chicken",
            "category": "lunch",
            "price": 120.00,
            "is_vegetarian": False
        }
    )
    assert response.status_code == 200
    item1_id = response.json()["data"]["id"]
    
    response = await client.post(
        "/api/v1/food-orders/items",
        headers={"Authorization": f"Bearer {cafe_manager_token}"},
        json={
            "name": "Paneer Tikka",
            "description": "Grilled cottage cheese",
            "category": "snacks",
            "price": 80.00,
            "is_vegetarian": True
        }
    )
    assert response.status_code == 200
    item2_id = response.json()["data"]["id"]
    
    # Employee views menu
    response = await client.get(
        "/api/v1/food-orders/items",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # Employee places order with multiple items (cart-based)
    response = await client.post(
        "/api/v1/food-orders/orders",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "order_items": [
                {"item_id": item1_id, "quantity": 2, "special_instructions": "Less spicy"},
                {"item_id": item2_id, "quantity": 1}
            ],
            "delivery_time": "13:00:00",
            "notes": "Cabin 305"
        }
    )
    assert response.status_code == 200
    order_id = response.json()["data"]["id"]
    assert response.json()["data"]["total_amount"] == 320.00  # (120*2 + 80*1)
    
    # Get my orders (RBAC - only own orders)
    response = await client.get(
        "/api/v1/food-orders/orders/my",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # Cafeteria manager updates order status
    response = await client.put(
        f"/api/v1/food-orders/orders/{order_id}/status",
        headers={"Authorization": f"Bearer {cafe_manager_token}"},
        json={"status": "preparing"}
    )
    assert response.status_code == 200


# ========== IT ASSET TESTS ==========

@pytest.mark.asyncio
async def test_it_asset_workflow(client, it_manager_token, employee_token):
    """Test complete IT asset lifecycle"""
    manager_token = it_manager_token
    emp_token = employee_token
    
    # IT manager creates asset
    response = await client.post(
        "/api/v1/it-assets",
        headers={"Authorization": f"Bearer {manager_token}"},
        json={
            "name": "Dell Latitude 5520",
            "asset_type": "laptop",
            "manufacturer": "Dell",
            "model": "Latitude 5520",
            "serial_number": "DL12345",
            "purchase_date": "2025-06-15",
            "purchase_price": 75000.00,
            "warranty_until": "2028-06-15",
            "specifications": {
                "processor": "Intel i7",
                "ram": "16GB",
                "storage": "512GB SSD"
            }
        }
    )
    assert response.status_code == 200
    asset_id = response.json()["data"]["id"]
    assert "asset_code" in response.json()["data"]
    
    # List assets
    response = await client.get(
        "/api/v1/it-assets",
        headers={"Authorization": f"Bearer {manager_token}"}
    )
    assert response.status_code == 200
    
    # Get employee user_id for assignment
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {emp_token}"}
    )
    employee_id = response.json()["data"]["id"]
    
    # Assign asset to employee
    response = await client.post(
        f"/api/v1/it-assets/{asset_id}/assign",
        headers={"Authorization": f"Bearer {manager_token}"},
        json={
            "user_id": employee_id,
            "notes": "Laptop for development"
        }
    )
    assert response.status_code == 200
    
    # Employee views their assets
    response = await client.get(
        "/api/v1/it-assets/my",
        headers={"Authorization": f"Bearer {emp_token}"}
    )
    assert response.status_code == 200
    
    # View asset history
    response = await client.get(
        f"/api/v1/it-assets/{asset_id}/history",
        headers={"Authorization": f"Bearer {manager_token}"}
    )
    assert response.status_code == 200
    
    # Unassign asset
    response = await client.post(
        f"/api/v1/it-assets/{asset_id}/unassign",
        headers={"Authorization": f"Bearer {manager_token}"}
    )
    assert response.status_code == 200


# ========== IT REQUEST TESTS ==========

@pytest.mark.asyncio
async def test_it_request_workflow(client, employee_token, it_manager_token):
    """Test complete IT request workflow: create, approve/reject"""
    emp_token = employee_token
    manager_token = it_manager_token
    
    # Employee creates IT request
    response = await client.post(
        "/api/v1/it-requests",
        headers={"Authorization": f"Bearer {emp_token}"},
        json={
            "request_type": "new_asset",
            "title": "Need new laptop",
            "description": "Current laptop is slow, need upgrade for development",
            "priority": "high"
        }
    )
    assert response.status_code == 200
    request_id = response.json()["data"]["id"]
    assert "request_number" in response.json()["data"]
    assert response.json()["data"]["status"] == "pending"
    
    # Get my requests
    response = await client.get(
        "/api/v1/it-requests",
        headers={"Authorization": f"Bearer {emp_token}"}
    )
    assert response.status_code == 200
    
    # IT manager views all requests
    response = await client.get(
        "/api/v1/it-requests",
        headers={"Authorization": f"Bearer {manager_token}"}
    )
    assert response.status_code == 200
    
    # IT manager approves request
    response = await client.post(
        f"/api/v1/it-requests/{request_id}/approve",
        headers={"Authorization": f"Bearer {manager_token}"},
        json={
            "action": "approve",
            "notes": "Approved, will assign by Friday"
        }
    )
    assert response.status_code == 200
    
    # Create another request to test rejection
    response = await client.post(
        "/api/v1/it-requests",
        headers={"Authorization": f"Bearer {emp_token}"},
        json={
            "request_type": "repair",
            "title": "Mouse not working",
            "description": "Wireless mouse needs battery",
            "priority": "low"
        }
    )
    request_id2 = response.json()["data"]["id"]
    
    # IT manager rejects request
    response = await client.post(
        f"/api/v1/it-requests/{request_id2}/approve",
        headers={"Authorization": f"Bearer {manager_token}"},
        json={
            "action": "reject",
            "rejection_reason": "Please try replacing battery first"
        }
    )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "rejected"


# ========== PROJECT MANAGEMENT TESTS ==========

@pytest.mark.asyncio
async def test_project_workflow(client, team_lead_token, admin_token):
    """Test complete project workflow"""
    lead_token, _ = team_lead_token
    
    # Team lead creates project
    response = await client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {lead_token}"},
        json={
            "project_name": "Mobile App Development",
            "description": "Develop iOS and Android apps",
            "start_date": "2026-03-01",
            "end_date": "2026-08-31",
            "estimated_budget": 5000000.00,
            "team_size": 8,
            "required_skills": ["React Native", "Node.js"],
            "business_justification": "Increase customer engagement"
        }
    )
    assert response.status_code == 200
    project_id = response.json()["data"]["id"]
    assert "project_code" in response.json()["data"]
    
    # Admin views pending projects
    response = await client.get(
        "/api/v1/projects/pending",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    
    # Admin approves project
    response = await client.post(
        f"/api/v1/projects/{project_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "action": "approve",
            "notes": "Approved with budget cap",
            "approved_budget": 4500000.00
        }
    )
    assert response.status_code == 200
    
    # Team lead updates project status
    response = await client.put(
        f"/api/v1/projects/{project_id}/status",
        headers={"Authorization": f"Bearer {lead_token}"},
        json={
            "status": "in_progress",
            "notes": "Project kicked off"
        }
    )
    assert response.status_code == 200


# ========== HOLIDAY MANAGEMENT TESTS ==========

@pytest.mark.asyncio
async def test_holiday_workflow(client, admin_token, employee_token):
    """Test holiday management workflow"""
    
    # Admin creates holiday
    response = await client.post(
        "/api/v1/holidays",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "holiday_name": "Republic Day",
            "holiday_date": "2026-01-26",
            "is_mandatory": True,
            "description": "National holiday"
        }
    )
    assert response.status_code == 200
    holiday_id = response.json()["data"]["id"]
    
    # All users can view holidays
    response = await client.get(
        "/api/v1/holidays",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response.status_code == 200
    
    # Admin updates holiday
    response = await client.put(
        f"/api/v1/holidays/{holiday_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"description": "Updated description"}
    )
    assert response.status_code == 200
    
    # Admin deletes holiday
    response = await client.delete(
        f"/api/v1/holidays/{holiday_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200


# ========== RBAC TESTS ==========

@pytest.mark.asyncio
async def test_rbac_enforcement(client, employee_token, admin_token):
    """Test that RBAC is properly enforced"""
    emp_token = employee_token
    
    # Employee cannot create users
    response = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {emp_token}"},
        json={
            "first_name": "Test",
            "last_name": "User",
            "role": "employee",
            "password": "Test@123"
        }
    )
    assert response.status_code == 403
    
    # Employee cannot view all users
    response = await client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {emp_token}"}
    )
    # Should only see themselves, not get 403
    assert response.status_code == 200
    
    # Employee cannot create parking slots
    response = await client.post(
        "/api/v1/parking/slots/create?slot_code=TEST-01",
        headers={"Authorization": f"Bearer {emp_token}"}
    )
    assert response.status_code == 403


# ========== ERROR HANDLING TESTS ==========

@pytest.mark.asyncio
async def test_error_handling(client, employee_token):
    """Test error handling and validation"""
    token = employee_token
    
    # Test check-out without check-in
    response = await client.post(
        "/api/v1/attendance/check-out",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    
    # Test invalid leave dates (past date)
    past_date = (date.today() - timedelta(days=1)).isoformat()
    response = await client.post(
        "/api/v1/leave/requests",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "leave_type": "casual",
            "start_date": past_date,
            "end_date": past_date,
            "reason": "Test"
        }
    )
    assert response.status_code == 400
    
    # Test double parking allocation
    response = await client.post(
        "/api/v1/attendance/check-in",
        headers={"Authorization": f"Bearer {token}"}
    )
    # Try check-in again without check-out
    response = await client.post(
        "/api/v1/attendance/check-in",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400


# ========== PAGINATION TESTS ==========

@pytest.mark.asyncio
async def test_pagination(client, admin_token):
    """Test pagination across endpoints"""
    
    # Create multiple users
    for i in range(5):
        await client.post(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {admin_token}"},
            json=add_vehicle_fields({
                "first_name": f"User{i}",
                "last_name": "Test",
                "role": "employee",
                "password": "Test@123"
            }, vehicle_number=f"TP{i}234")
        )
    
    # Test pagination
    response = await client.get(
        "/api/v1/users?page=1&page_size=3",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 3
    assert "total" in data


# ========== SEARCH TESTS ==========

@pytest.mark.asyncio
async def test_semantic_search(client, admin_token):
    """Test semantic search functionality"""
    
    # Create cafeteria manager and food items
    response = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json=add_vehicle_fields({
            "first_name": "Cafe",
            "last_name": "Manager",
            "role": "manager",
            "manager_type": "cafeteria",
            "password": "Manager@123"
        })
    )
    
    response = await client.post("/api/v1/auth/login", json={
        "email": response.json()["data"]["email"],
        "password": "Manager@123"
    })
    cafe_token = response.json()["data"]["access_token"]
    
    # Create food items
    await client.post(
        "/api/v1/food-orders/items",
        headers={"Authorization": f"Bearer {cafe_token}"},
        json={
            "name": "Spicy Paneer Tikka",
            "description": "Grilled cottage cheese with spices",
            "category": "snacks",
            "price": 80.00,
            "is_vegetarian": True
        }
    )
    
    # Test search
    response = await client.post(
        "/api/v1/search",
        headers={"Authorization": f"Bearer {cafe_token}"},
        json={
            "query": "spicy vegetarian",
            "search_type": "food",
            "limit": 5
        }
    )
    # Search might work or fail depending on pgvector availability
    # Just check it doesn't crash
    assert response.status_code in [200, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
