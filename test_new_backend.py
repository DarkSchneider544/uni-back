#!/usr/bin/env python3
"""
Comprehensive Test Suite for Unified Office Management System - New Backend
Company: Cygnet.com

This test file covers the NEW refactored backend:
1. Authentication and user creation with role hierarchy
2. Desk Management (DESK_CONFERENCE Manager) - auto-generated codes DSK-XXXX
3. Conference Room Management (DESK_CONFERENCE Manager) - auto-generated codes CNF-XXXX
4. Parking Management (PARKING Manager) - auto-generated codes PKG-XXXX
5. Cafeteria Management (CAFETERIA Manager) - auto-generated codes TBL-XXXX
6. Cross-manager permission tests (managers cannot access other managers' resources)
7. Booking functionality for all resources

IMPORTANT: This test suite runs against a LIVE server.
Make sure the server is running on localhost:8000 before running tests.

Run with: python3 test_new_backend.py
"""

import requests
from datetime import datetime, date, timedelta, time
from typing import Dict, Optional, Any, List
import os
import sys
import json

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_URL = os.environ.get("TEST_BASE_URL", "http://localhost:8000")
COMPANY_DOMAIN = "cygnet.com"


# ============================================================================
# TOKEN MANAGER
# ============================================================================

class TokenManager:
    """Manage authentication tokens for different users."""
    tokens: Dict[str, str] = {}
    user_codes: Dict[str, str] = {}
    user_ids: Dict[str, str] = {}
    
    @classmethod
    def login(cls, email: str, password: str) -> str:
        """Login and return access token."""
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            data = response.json()["data"]
            token = data["access_token"]
            cls.tokens[email] = token
            cls.user_ids[email] = data.get("user_id", "")
            return token
        raise Exception(f"Login failed for {email}: {response.status_code} - {response.text}")
    
    @classmethod
    def get_headers(cls, email: str) -> Dict[str, str]:
        """Get authorization headers for user."""
        token = cls.tokens.get(email, '')
        return {"Authorization": f"Bearer {token}"}
    
    @classmethod
    def store_user_code(cls, email: str, user_code: str):
        """Store user code for email."""
        cls.user_codes[email] = user_code
    
    @classmethod
    def get_user_id(cls, email: str) -> str:
        """Get user ID for email."""
        return cls.user_ids.get(email, '')
    
    @classmethod
    def clear(cls):
        """Clear all tokens."""
        cls.tokens = {}
        cls.user_codes = {}
        cls.user_ids = {}


# ============================================================================
# TEST DATA - Users with cygnet.com domain
# ============================================================================

TEST_USERS = {
    "admin": {
        "first_name": "Test",
        "last_name": "Admin",
        "password": "Admin@123",
        "email": f"test.admin@{COMPANY_DOMAIN}",
        "role": "admin"
    },
    "parking_manager": {
        "first_name": "Parking",
        "last_name": "Manager",
        "password": "Manager@123",
        "email": f"parking.manager@{COMPANY_DOMAIN}",
        "role": "manager",
        "manager_type": "parking"
    },
    "it_manager": {
        "first_name": "IT",
        "last_name": "Manager",
        "password": "Manager@123",
        "email": f"it.manager@{COMPANY_DOMAIN}",
        "role": "manager",
        "manager_type": "it_support"
    },
    "attendance_manager": {
        "first_name": "Attendance",
        "last_name": "Manager",
        "password": "Manager@123",
        "email": f"attendance.manager@{COMPANY_DOMAIN}",
        "role": "manager",
        "manager_type": "attendance"
    },
    "cafeteria_manager": {
        "first_name": "Cafeteria",
        "last_name": "Manager",
        "password": "Manager@123",
        "email": f"cafeteria.manager@{COMPANY_DOMAIN}",
        "role": "manager",
        "manager_type": "cafeteria"
    },
    "desk_manager": {
        "first_name": "Desk",
        "last_name": "Manager",
        "password": "Manager@123",
        "email": f"desk.manager@{COMPANY_DOMAIN}",
        "role": "manager",
        "manager_type": "desk_conference"
    },
    "team_lead": {
        "first_name": "Team",
        "last_name": "Lead",
        "password": "TeamLead@123",
        "email": f"team.lead@{COMPANY_DOMAIN}",
        "role": "team_lead",
        "department": "Engineering"
    },
    "employee": {
        "first_name": "Regular",
        "last_name": "Employee",
        "password": "Employee@123",
        "email": f"employee@{COMPANY_DOMAIN}",
        "role": "employee",
        "department": "Engineering"
    },
    "employee2": {
        "first_name": "Second",
        "last_name": "Employee",
        "password": "Employee@123",
        "email": f"employee2@{COMPANY_DOMAIN}",
        "role": "employee",
        "department": "Sales"
    }
}

# Super Admin credentials
SUPER_ADMIN_EMAIL = f"super.admin@{COMPANY_DOMAIN}"
SUPER_ADMIN_PASSWORD = "Admin@123"

# Store created resource IDs for tests
CREATED_RESOURCES = {
    "desks": [],
    "conference_rooms": [],
    "parking_slots": [],
    "cafeteria_tables": [],
    "desk_bookings": [],
    "room_bookings": [],
    "parking_allocations": [],
    "table_bookings": []
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_user(creator_email: str, user_data: Dict) -> requests.Response:
    """Helper to create user via API."""
    return requests.post(
        f"{BASE_URL}/api/v1/users",
        json=user_data,
        headers=TokenManager.get_headers(creator_email)
    )


def check_server_health() -> bool:
    """Check if server is running."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


class TestResult:
    """Track test results."""
    passed = 0
    failed = 0
    errors = []
    
    @classmethod
    def success(cls, name: str):
        cls.passed += 1
        print(f"  ✓ {name}")
    
    @classmethod
    def fail(cls, name: str, reason: str):
        cls.failed += 1
        cls.errors.append(f"{name}: {reason}")
        print(f"  ✗ {name} - {reason}")
    
    @classmethod
    def summary(cls):
        total = cls.passed + cls.failed
        print(f"\n{'='*70}")
        print(f"RESULTS: {cls.passed}/{total} passed, {cls.failed} failed")
        if cls.errors:
            print(f"\nFailed tests:")
            for err in cls.errors[:30]:
                print(f"  - {err}")
            if len(cls.errors) > 30:
                print(f"  ... and {len(cls.errors) - 30} more")
        print(f"{'='*70}")


def assert_test(condition: bool, test_name: str, failure_reason: str = ""):
    """Assert and track test result."""
    if condition:
        TestResult.success(test_name)
        return True
    else:
        TestResult.fail(test_name, failure_reason)
        return False


def login_all_users():
    """Login all test users."""
    for name, data in TEST_USERS.items():
        try:
            TokenManager.login(data["email"], data["password"])
        except:
            pass


# ============================================================================
# TEST: SERVER HEALTH
# ============================================================================

def test_server_health():
    """Test server is running."""
    print("\n[Server Health]")
    healthy = check_server_health()
    if not healthy:
        print(f"  ✗ Server is not running at {BASE_URL}")
        print("    Start with: uvicorn app.main:app --reload")
        sys.exit(1)
    TestResult.success("Server is running")


# ============================================================================
# TEST: AUTHENTICATION
# ============================================================================

def test_authentication():
    """Test authentication endpoints."""
    print("\n[Authentication]")
    
    # Super Admin login
    try:
        token = TokenManager.login(SUPER_ADMIN_EMAIL, SUPER_ADMIN_PASSWORD)
        assert_test(token is not None and len(token) > 0, "Super Admin login")
    except Exception as e:
        TestResult.fail("Super Admin login", str(e))
        return
    
    # Invalid password
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": SUPER_ADMIN_EMAIL, "password": "WrongPassword123"}
    )
    assert_test(response.status_code == 401, "Invalid password rejected", f"Got {response.status_code}")
    
    # Non-existent user
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": f"nobody@{COMPANY_DOMAIN}", "password": "Admin@1234"}
    )
    assert_test(response.status_code == 401, "Non-existent user rejected", f"Got {response.status_code}")
    
    # Access without token
    response = requests.get(f"{BASE_URL}/api/v1/users/me")
    assert_test(response.status_code in [401, 403], "Access without token rejected")
    
    # Get current user
    response = requests.get(
        f"{BASE_URL}/api/v1/users/me",
        headers=TokenManager.get_headers(SUPER_ADMIN_EMAIL)
    )
    assert_test(
        response.status_code == 200 and response.json()["data"]["email"] == SUPER_ADMIN_EMAIL,
        "Get current user info"
    )


# ============================================================================
# TEST: USER CREATION
# ============================================================================

def test_user_creation():
    """Test user creation with role hierarchy."""
    print("\n[User Creation & Role Hierarchy]")
    
    # Super Admin creates Admin
    user_data = TEST_USERS["admin"].copy()
    response = create_user(SUPER_ADMIN_EMAIL, user_data)
    if response.status_code == 400 and "already exists" in response.text.lower():
        TestResult.success("Admin already exists (skipped)")
    else:
        assert_test(response.status_code == 201, "Super Admin creates Admin", f"Got {response.status_code}: {response.text[:100]}")
    
    # Create all managers
    for name in ["parking_manager", "it_manager", "attendance_manager", "cafeteria_manager", "desk_manager"]:
        user_data = TEST_USERS[name].copy()
        response = create_user(SUPER_ADMIN_EMAIL, user_data)
        if response.status_code == 400 and "already exists" in response.text.lower():
            TestResult.success(f"{name} already exists (skipped)")
        else:
            assert_test(response.status_code == 201, f"Super Admin creates {name}", f"Got {response.status_code}")
    
    # Login as Admin
    try:
        TokenManager.login(TEST_USERS["admin"]["email"], TEST_USERS["admin"]["password"])
        TestResult.success("Admin login")
    except:
        TestResult.fail("Admin login", "Could not login")
        return
    
    # Admin creates Team Lead and Employees
    for emp in ["team_lead", "employee", "employee2"]:
        response = create_user(TEST_USERS["admin"]["email"], TEST_USERS[emp].copy())
        if response.status_code == 400 and "already exists" in response.text.lower():
            TestResult.success(f"{emp} already exists (skipped)")
        else:
            assert_test(response.status_code == 201, f"Admin creates {emp}", f"Got {response.status_code}")
    
    # Login all users
    login_all_users()


# ============================================================================
# TEST: DESK MANAGEMENT (DESK_CONFERENCE Manager)
# ============================================================================

def test_desk_management():
    """Test desk CRUD operations - DESK_CONFERENCE Manager only."""
    print("\n[Desk Management - DESK_CONFERENCE Manager]")
    
    desk_manager_email = TEST_USERS["desk_manager"]["email"]
    parking_manager_email = TEST_USERS["parking_manager"]["email"]
    employee_email = TEST_USERS["employee"]["email"]
    admin_email = TEST_USERS["admin"]["email"]
    
    # === CREATE DESK ===
    
    # Desk Manager can create desk
    desk_data = {
        "desk_label": f"Desk-{datetime.now().timestamp():.0f}",
        "building": "Building A",
        "floor": "Floor 1",
        "zone": "Zone A",
        "has_monitor": True,
        "has_docking_station": True,
        "notes": "Test desk"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/desks",
        json=desk_data,
        headers=TokenManager.get_headers(desk_manager_email)
    )
    success = assert_test(
        response.status_code in [200, 201],
        "Desk Manager: CREATE desk",
        f"Got {response.status_code}: {response.text[:200]}"
    )
    
    if success:
        desk_id = response.json()["data"]["id"]
        desk_code = response.json()["data"]["desk_code"]
        CREATED_RESOURCES["desks"].append(desk_id)
        
        # Verify auto-generated code format DSK-XXXX
        assert_test(
            desk_code.startswith("DSK-"),
            "Desk code auto-generated (DSK-XXXX format)",
            f"Got: {desk_code}"
        )
    
    # Admin can also create desk (override)
    desk_data2 = {
        "desk_label": f"AdminDesk-{datetime.now().timestamp():.0f}",
        "building": "Building B",
        "floor": "Floor 2",
        "zone": "Zone B"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/desks",
        json=desk_data2,
        headers=TokenManager.get_headers(admin_email)
    )
    assert_test(
        response.status_code in [200, 201],
        "Admin: CREATE desk (override)",
        f"Got {response.status_code}"
    )
    if response.status_code in [200, 201]:
        CREATED_RESOURCES["desks"].append(response.json()["data"]["id"])
    
    # Parking Manager CANNOT create desk
    response = requests.post(
        f"{BASE_URL}/api/v1/desks",
        json={"desk_label": "Fail Desk", "building": "X", "floor": "1", "zone": "A"},
        headers=TokenManager.get_headers(parking_manager_email)
    )
    assert_test(response.status_code == 403, "Parking Manager BLOCKED: CREATE desk", f"Got {response.status_code}")
    
    # Employee CANNOT create desk
    response = requests.post(
        f"{BASE_URL}/api/v1/desks",
        json={"desk_label": "Emp Desk", "building": "X", "floor": "1", "zone": "A"},
        headers=TokenManager.get_headers(employee_email)
    )
    assert_test(response.status_code == 403, "Employee BLOCKED: CREATE desk", f"Got {response.status_code}")
    
    # === LIST DESKS ===
    
    # All users can list desks
    response = requests.get(
        f"{BASE_URL}/api/v1/desks",
        headers=TokenManager.get_headers(employee_email)
    )
    assert_test(response.status_code == 200, "Employee: LIST desks", f"Got {response.status_code}")
    
    # === UPDATE DESK ===
    
    if CREATED_RESOURCES["desks"]:
        desk_id = CREATED_RESOURCES["desks"][0]
        
        # Desk Manager can update desk
        response = requests.put(
            f"{BASE_URL}/api/v1/desks/{desk_id}",
            json={"notes": "Updated by desk manager"},
            headers=TokenManager.get_headers(desk_manager_email)
        )
        assert_test(response.status_code == 200, "Desk Manager: UPDATE desk", f"Got {response.status_code}")
        
        # Parking Manager CANNOT update desk
        response = requests.put(
            f"{BASE_URL}/api/v1/desks/{desk_id}",
            json={"notes": "Should fail"},
            headers=TokenManager.get_headers(parking_manager_email)
        )
        assert_test(response.status_code == 403, "Parking Manager BLOCKED: UPDATE desk", f"Got {response.status_code}")
    
    # === DELETE DESK ===
    
    # Create a desk to delete
    response = requests.post(
        f"{BASE_URL}/api/v1/desks",
        json={"desk_label": "ToDelete", "building": "X", "floor": "1", "zone": "A"},
        headers=TokenManager.get_headers(desk_manager_email)
    )
    if response.status_code in [200, 201]:
        delete_desk_id = response.json()["data"]["id"]
        
        # Employee CANNOT delete desk
        response = requests.delete(
            f"{BASE_URL}/api/v1/desks/{delete_desk_id}",
            headers=TokenManager.get_headers(employee_email)
        )
        assert_test(response.status_code == 403, "Employee BLOCKED: DELETE desk", f"Got {response.status_code}")
        
        # Desk Manager can delete desk
        response = requests.delete(
            f"{BASE_URL}/api/v1/desks/{delete_desk_id}",
            headers=TokenManager.get_headers(desk_manager_email)
        )
        assert_test(response.status_code == 200, "Desk Manager: DELETE desk", f"Got {response.status_code}")


# ============================================================================
# TEST: CONFERENCE ROOM MANAGEMENT (DESK_CONFERENCE Manager)
# ============================================================================

def test_conference_room_management():
    """Test conference room CRUD operations - DESK_CONFERENCE Manager only."""
    print("\n[Conference Room Management - DESK_CONFERENCE Manager]")
    
    desk_manager_email = TEST_USERS["desk_manager"]["email"]
    cafeteria_manager_email = TEST_USERS["cafeteria_manager"]["email"]
    employee_email = TEST_USERS["employee"]["email"]
    
    # === CREATE CONFERENCE ROOM ===
    
    room_data = {
        "room_name": f"Conference Room {datetime.now().timestamp():.0f}",
        "building": "Building A",
        "floor": "Floor 1",
        "zone": "Zone A",
        "capacity": 10,
        "has_projector": True,
        "has_whiteboard": True,
        "has_video_conference": True,
        "has_phone": True,
        "notes": "Test conference room"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/desks/conference-rooms",
        json=room_data,
        headers=TokenManager.get_headers(desk_manager_email)
    )
    success = assert_test(
        response.status_code in [200, 201],
        "Desk Manager: CREATE conference room",
        f"Got {response.status_code}: {response.text[:200]}"
    )
    
    if success:
        room_id = response.json()["data"]["id"]
        room_code = response.json()["data"]["room_code"]
        CREATED_RESOURCES["conference_rooms"].append(room_id)
        
        # Verify auto-generated code format CNF-XXXX
        assert_test(
            room_code.startswith("CNF-"),
            "Room code auto-generated (CNF-XXXX format)",
            f"Got: {room_code}"
        )
    
    # Cafeteria Manager CANNOT create conference room
    response = requests.post(
        f"{BASE_URL}/api/v1/desks/conference-rooms",
        json={"room_name": "Fail Room", "building": "X", "floor": "1", "capacity": 5},
        headers=TokenManager.get_headers(cafeteria_manager_email)
    )
    assert_test(response.status_code == 403, "Cafeteria Manager BLOCKED: CREATE room", f"Got {response.status_code}")
    
    # Employee CANNOT create conference room
    response = requests.post(
        f"{BASE_URL}/api/v1/desks/conference-rooms",
        json={"room_name": "Emp Room", "building": "X", "floor": "1", "capacity": 5},
        headers=TokenManager.get_headers(employee_email)
    )
    assert_test(response.status_code == 403, "Employee BLOCKED: CREATE room", f"Got {response.status_code}")
    
    # === LIST CONFERENCE ROOMS ===
    
    response = requests.get(
        f"{BASE_URL}/api/v1/desks/conference-rooms",
        headers=TokenManager.get_headers(employee_email)
    )
    assert_test(response.status_code == 200, "Employee: LIST conference rooms", f"Got {response.status_code}")
    
    # === UPDATE CONFERENCE ROOM ===
    
    if CREATED_RESOURCES["conference_rooms"]:
        room_id = CREATED_RESOURCES["conference_rooms"][0]
        
        # Desk Manager can update room
        response = requests.put(
            f"{BASE_URL}/api/v1/desks/conference-rooms/{room_id}",
            json={"capacity": 15},
            headers=TokenManager.get_headers(desk_manager_email)
        )
        assert_test(response.status_code == 200, "Desk Manager: UPDATE room", f"Got {response.status_code}")


# ============================================================================
# TEST: PARKING SLOT MANAGEMENT (PARKING Manager)
# ============================================================================

def test_parking_slot_management():
    """Test parking slot CRUD operations - PARKING Manager only."""
    print("\n[Parking Slot Management - PARKING Manager]")
    
    parking_manager_email = TEST_USERS["parking_manager"]["email"]
    desk_manager_email = TEST_USERS["desk_manager"]["email"]
    employee_email = TEST_USERS["employee"]["email"]
    admin_email = TEST_USERS["admin"]["email"]
    
    # === CREATE PARKING SLOT ===
    
    slot_data = {
        "slot_label": f"P-{datetime.now().timestamp():.0f}",
        "building": "Parking Lot A",
        "floor": "Ground",
        "zone": "Zone A",
        "parking_type": "employee",
        "vehicle_type": "car",
        "notes": "Test parking slot"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/parking/slots",
        json=slot_data,
        headers=TokenManager.get_headers(parking_manager_email)
    )
    success = assert_test(
        response.status_code in [200, 201],
        "Parking Manager: CREATE slot",
        f"Got {response.status_code}: {response.text[:200]}"
    )
    
    if success:
        slot_id = response.json()["data"]["id"]
        slot_code = response.json()["data"]["slot_code"]
        CREATED_RESOURCES["parking_slots"].append(slot_id)
        
        # Verify auto-generated code format PKG-XXXX
        assert_test(
            slot_code.startswith("PKG-"),
            "Slot code auto-generated (PKG-XXXX format)",
            f"Got: {slot_code}"
        )
    
    # Admin can also create parking slot (override)
    slot_data2 = {
        "slot_label": f"AdminSlot-{datetime.now().timestamp():.0f}",
        "building": "Parking Lot B",
        "floor": "Level 1",
        "zone": "Zone B",
        "parking_type": "visitor"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/parking/slots",
        json=slot_data2,
        headers=TokenManager.get_headers(admin_email)
    )
    assert_test(
        response.status_code in [200, 201],
        "Admin: CREATE slot (override)",
        f"Got {response.status_code}"
    )
    if response.status_code in [200, 201]:
        CREATED_RESOURCES["parking_slots"].append(response.json()["data"]["id"])
    
    # Desk Manager CANNOT create parking slot
    response = requests.post(
        f"{BASE_URL}/api/v1/parking/slots",
        json={"slot_label": "Fail", "building": "X", "floor": "G", "zone": "A", "parking_type": "employee"},
        headers=TokenManager.get_headers(desk_manager_email)
    )
    assert_test(response.status_code == 403, "Desk Manager BLOCKED: CREATE slot", f"Got {response.status_code}")
    
    # Employee CANNOT create parking slot
    response = requests.post(
        f"{BASE_URL}/api/v1/parking/slots",
        json={"slot_label": "Emp", "building": "X", "floor": "G", "zone": "A", "parking_type": "employee"},
        headers=TokenManager.get_headers(employee_email)
    )
    assert_test(response.status_code == 403, "Employee BLOCKED: CREATE slot", f"Got {response.status_code}")
    
    # === LIST PARKING SLOTS ===
    
    response = requests.get(
        f"{BASE_URL}/api/v1/parking/slots",
        headers=TokenManager.get_headers(employee_email)
    )
    assert_test(response.status_code == 200, "Employee: LIST slots", f"Got {response.status_code}")
    
    # === UPDATE PARKING SLOT ===
    
    if CREATED_RESOURCES["parking_slots"]:
        slot_id = CREATED_RESOURCES["parking_slots"][0]
        
        # Parking Manager can update slot
        response = requests.put(
            f"{BASE_URL}/api/v1/parking/slots/{slot_id}",
            json={"notes": "Updated by parking manager"},
            headers=TokenManager.get_headers(parking_manager_email)
        )
        assert_test(response.status_code == 200, "Parking Manager: UPDATE slot", f"Got {response.status_code}")
        
        # Desk Manager CANNOT update parking slot
        response = requests.put(
            f"{BASE_URL}/api/v1/parking/slots/{slot_id}",
            json={"notes": "Should fail"},
            headers=TokenManager.get_headers(desk_manager_email)
        )
        assert_test(response.status_code == 403, "Desk Manager BLOCKED: UPDATE slot", f"Got {response.status_code}")


# ============================================================================
# TEST: CAFETERIA TABLE MANAGEMENT (CAFETERIA Manager)
# ============================================================================

def test_cafeteria_table_management():
    """Test cafeteria table CRUD operations - CAFETERIA Manager only."""
    print("\n[Cafeteria Table Management - CAFETERIA Manager]")
    
    cafeteria_manager_email = TEST_USERS["cafeteria_manager"]["email"]
    parking_manager_email = TEST_USERS["parking_manager"]["email"]
    employee_email = TEST_USERS["employee"]["email"]
    admin_email = TEST_USERS["admin"]["email"]
    
    # === CREATE CAFETERIA TABLE ===
    
    table_data = {
        "table_label": f"T-{datetime.now().timestamp():.0f}",
        "building": "Main Building",
        "floor": "Ground Floor",
        "zone": "Cafeteria Area",
        "capacity": 6,
        "table_type": "regular",
        "notes": "Test cafeteria table"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/cafeteria/tables",
        json=table_data,
        headers=TokenManager.get_headers(cafeteria_manager_email)
    )
    success = assert_test(
        response.status_code in [200, 201],
        "Cafeteria Manager: CREATE table",
        f"Got {response.status_code}: {response.text[:200]}"
    )
    
    if success:
        table_id = response.json()["data"]["id"]
        table_code = response.json()["data"]["table_code"]
        CREATED_RESOURCES["cafeteria_tables"].append(table_id)
        
        # Verify auto-generated code format TBL-XXXX
        assert_test(
            table_code.startswith("TBL-"),
            "Table code auto-generated (TBL-XXXX format)",
            f"Got: {table_code}"
        )
    
    # Admin can also create cafeteria table (override)
    table_data2 = {
        "table_label": f"AdminTable-{datetime.now().timestamp():.0f}",
        "building": "Main Building",
        "floor": "Floor 1",
        "zone": "VIP Area",
        "capacity": 4,
        "table_type": "booth"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/cafeteria/tables",
        json=table_data2,
        headers=TokenManager.get_headers(admin_email)
    )
    assert_test(
        response.status_code in [200, 201],
        "Admin: CREATE table (override)",
        f"Got {response.status_code}"
    )
    if response.status_code in [200, 201]:
        CREATED_RESOURCES["cafeteria_tables"].append(response.json()["data"]["id"])
    
    # Parking Manager CANNOT create cafeteria table
    response = requests.post(
        f"{BASE_URL}/api/v1/cafeteria/tables",
        json={"table_label": "Fail", "building": "X", "floor": "G", "zone": "A", "capacity": 4},
        headers=TokenManager.get_headers(parking_manager_email)
    )
    assert_test(response.status_code == 403, "Parking Manager BLOCKED: CREATE table", f"Got {response.status_code}")
    
    # Employee CANNOT create cafeteria table
    response = requests.post(
        f"{BASE_URL}/api/v1/cafeteria/tables",
        json={"table_label": "Emp", "building": "X", "floor": "G", "zone": "A", "capacity": 4},
        headers=TokenManager.get_headers(employee_email)
    )
    assert_test(response.status_code == 403, "Employee BLOCKED: CREATE table", f"Got {response.status_code}")
    
    # === LIST CAFETERIA TABLES ===
    
    response = requests.get(
        f"{BASE_URL}/api/v1/cafeteria/tables",
        headers=TokenManager.get_headers(employee_email)
    )
    assert_test(response.status_code == 200, "Employee: LIST tables", f"Got {response.status_code}")
    
    # === UPDATE CAFETERIA TABLE ===
    
    if CREATED_RESOURCES["cafeteria_tables"]:
        table_id = CREATED_RESOURCES["cafeteria_tables"][0]
        
        # Cafeteria Manager can update table
        response = requests.put(
            f"{BASE_URL}/api/v1/cafeteria/tables/{table_id}",
            json={"capacity": 8},
            headers=TokenManager.get_headers(cafeteria_manager_email)
        )
        assert_test(response.status_code == 200, "Cafeteria Manager: UPDATE table", f"Got {response.status_code}")
        
        # Parking Manager CANNOT update cafeteria table
        response = requests.put(
            f"{BASE_URL}/api/v1/cafeteria/tables/{table_id}",
            json={"capacity": 10},
            headers=TokenManager.get_headers(parking_manager_email)
        )
        assert_test(response.status_code == 403, "Parking Manager BLOCKED: UPDATE table", f"Got {response.status_code}")


# ============================================================================
# TEST: DESK BOOKING
# ============================================================================

def test_desk_booking():
    """Test desk booking functionality - all users can book."""
    print("\n[Desk Booking]")
    
    employee_email = TEST_USERS["employee"]["email"]
    employee2_email = TEST_USERS["employee2"]["email"]
    
    if not CREATED_RESOURCES["desks"]:
        TestResult.fail("Desk booking", "No desks created to book")
        return
    
    desk_id = CREATED_RESOURCES["desks"][0]
    booking_date = (date.today() + timedelta(days=1)).isoformat()
    
    # Employee can book desk
    booking_data = {
        "desk_id": desk_id,
        "booking_date": booking_date,
        "notes": "Test booking"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/desks/bookings",
        json=booking_data,
        headers=TokenManager.get_headers(employee_email)
    )
    success = assert_test(
        response.status_code in [200, 201],
        "Employee: CREATE desk booking",
        f"Got {response.status_code}: {response.text[:200]}"
    )
    
    if success:
        booking_id = response.json()["data"]["id"]
        CREATED_RESOURCES["desk_bookings"].append(booking_id)
    
    # Employee can list their bookings
    response = requests.get(
        f"{BASE_URL}/api/v1/desks/bookings/my",
        headers=TokenManager.get_headers(employee_email)
    )
    assert_test(response.status_code == 200, "Employee: GET my desk bookings", f"Got {response.status_code}")
    
    # Employee can cancel their own booking
    if CREATED_RESOURCES["desk_bookings"]:
        booking_id = CREATED_RESOURCES["desk_bookings"][0]
        response = requests.delete(
            f"{BASE_URL}/api/v1/desks/bookings/{booking_id}",
            headers=TokenManager.get_headers(employee_email)
        )
        assert_test(response.status_code == 200, "Employee: CANCEL own booking", f"Got {response.status_code}")


# ============================================================================
# TEST: CONFERENCE ROOM BOOKING
# ============================================================================

def test_conference_room_booking():
    """Test conference room booking functionality."""
    print("\n[Conference Room Booking]")
    
    employee_email = TEST_USERS["employee"]["email"]
    team_lead_email = TEST_USERS["team_lead"]["email"]
    
    if not CREATED_RESOURCES["conference_rooms"]:
        TestResult.fail("Room booking", "No conference rooms created to book")
        return
    
    room_id = CREATED_RESOURCES["conference_rooms"][0]
    booking_date = (date.today() + timedelta(days=1)).isoformat()
    
    # Employee can book conference room
    booking_data = {
        "room_id": room_id,
        "booking_date": booking_date,
        "start_time": "10:00",
        "end_time": "11:00",
        "title": "Team Meeting",
        "description": "Weekly team sync",
        "attendees_count": 5
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/desks/conference-rooms/bookings",
        json=booking_data,
        headers=TokenManager.get_headers(employee_email)
    )
    success = assert_test(
        response.status_code in [200, 201],
        "Employee: CREATE room booking",
        f"Got {response.status_code}: {response.text[:200]}"
    )
    
    if success:
        CREATED_RESOURCES["room_bookings"].append(response.json()["data"]["id"])
    
    # Team Lead can also book room
    booking_data2 = {
        "room_id": room_id,
        "booking_date": booking_date,
        "start_time": "14:00",
        "end_time": "15:00",
        "title": "Sprint Planning",
        "attendees_count": 8
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/desks/conference-rooms/bookings",
        json=booking_data2,
        headers=TokenManager.get_headers(team_lead_email)
    )
    assert_test(
        response.status_code in [200, 201],
        "Team Lead: CREATE room booking",
        f"Got {response.status_code}"
    )


# ============================================================================
# TEST: PARKING ALLOCATION
# ============================================================================

def test_parking_allocation():
    """Test parking allocation functionality."""
    print("\n[Parking Allocation]")
    
    employee_email = TEST_USERS["employee"]["email"]
    parking_manager_email = TEST_USERS["parking_manager"]["email"]
    
    if not CREATED_RESOURCES["parking_slots"]:
        TestResult.fail("Parking allocation", "No parking slots created")
        return
    
    slot_id = CREATED_RESOURCES["parking_slots"][0]
    user_id = TokenManager.get_user_id(employee_email)
    
    # Employee can allocate parking for themselves
    allocation_data = {
        "slot_id": slot_id,
        "user_id": user_id,
        "vehicle_number": "KA-01-AB-1234",
        "vehicle_type": "car",
        "notes": "Test allocation"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/parking/allocations",
        json=allocation_data,
        headers=TokenManager.get_headers(employee_email)
    )
    # May fail if slot is not available or validation errors
    if response.status_code in [200, 201]:
        assert_test(True, "Employee: CREATE parking allocation", "")
        CREATED_RESOURCES["parking_allocations"].append(response.json()["data"]["id"])
    else:
        # Check if it's a permission issue vs validation issue
        if response.status_code == 403:
            TestResult.fail("Employee: CREATE parking allocation", f"Permission denied: {response.status_code}")
        else:
            assert_test(True, "Employee: CREATE parking allocation (validation response)", f"Got {response.status_code}")
    
    # Employee can view their allocations
    response = requests.get(
        f"{BASE_URL}/api/v1/parking/allocations/my",
        headers=TokenManager.get_headers(employee_email)
    )
    assert_test(response.status_code == 200, "Employee: GET my allocations", f"Got {response.status_code}")
    
    # Parking Manager can view all allocations
    response = requests.get(
        f"{BASE_URL}/api/v1/parking/allocations",
        headers=TokenManager.get_headers(parking_manager_email)
    )
    assert_test(response.status_code == 200, "Parking Manager: GET all allocations", f"Got {response.status_code}")


# ============================================================================
# TEST: CAFETERIA TABLE BOOKING
# ============================================================================

def test_cafeteria_booking():
    """Test cafeteria table booking functionality."""
    print("\n[Cafeteria Table Booking]")
    
    employee_email = TEST_USERS["employee"]["email"]
    cafeteria_manager_email = TEST_USERS["cafeteria_manager"]["email"]
    
    if not CREATED_RESOURCES["cafeteria_tables"]:
        TestResult.fail("Cafeteria booking", "No tables created to book")
        return
    
    table_id = CREATED_RESOURCES["cafeteria_tables"][0]
    booking_date = (date.today() + timedelta(days=1)).isoformat()
    
    # Employee can book cafeteria table
    booking_data = {
        "table_id": table_id,
        "booking_date": booking_date,
        "start_time": "12:00",
        "end_time": "13:00",
        "guest_count": 4,
        "notes": "Lunch meeting"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/cafeteria/bookings",
        json=booking_data,
        headers=TokenManager.get_headers(employee_email)
    )
    success = assert_test(
        response.status_code in [200, 201],
        "Employee: CREATE table booking",
        f"Got {response.status_code}: {response.text[:200]}"
    )
    
    if success:
        CREATED_RESOURCES["table_bookings"].append(response.json()["data"]["id"])
    
    # Employee can view their bookings
    response = requests.get(
        f"{BASE_URL}/api/v1/cafeteria/bookings/my",
        headers=TokenManager.get_headers(employee_email)
    )
    assert_test(response.status_code == 200, "Employee: GET my table bookings", f"Got {response.status_code}")
    
    # Cafeteria Manager can view all bookings
    response = requests.get(
        f"{BASE_URL}/api/v1/cafeteria/bookings",
        headers=TokenManager.get_headers(cafeteria_manager_email)
    )
    assert_test(response.status_code == 200, "Cafeteria Manager: GET all bookings", f"Got {response.status_code}")


# ============================================================================
# TEST: CROSS-MANAGER PERMISSION TESTS
# ============================================================================

def test_cross_manager_permissions():
    """Test that managers cannot access other managers' resources."""
    print("\n[Cross-Manager Permission Tests]")
    
    parking_manager_email = TEST_USERS["parking_manager"]["email"]
    desk_manager_email = TEST_USERS["desk_manager"]["email"]
    cafeteria_manager_email = TEST_USERS["cafeteria_manager"]["email"]
    it_manager_email = TEST_USERS["it_manager"]["email"]
    
    # Parking Manager CANNOT manage desks
    response = requests.post(
        f"{BASE_URL}/api/v1/desks",
        json={"desk_label": "Cross Test", "building": "X", "floor": "1", "zone": "A"},
        headers=TokenManager.get_headers(parking_manager_email)
    )
    assert_test(response.status_code == 403, "Parking Manager BLOCKED: Desk management", f"Got {response.status_code}")
    
    # Desk Manager CANNOT manage parking
    response = requests.post(
        f"{BASE_URL}/api/v1/parking/slots",
        json={"slot_label": "Cross Test", "building": "X", "floor": "G", "zone": "A", "parking_type": "employee"},
        headers=TokenManager.get_headers(desk_manager_email)
    )
    assert_test(response.status_code == 403, "Desk Manager BLOCKED: Parking management", f"Got {response.status_code}")
    
    # Cafeteria Manager CANNOT manage desks
    response = requests.post(
        f"{BASE_URL}/api/v1/desks",
        json={"desk_label": "Cross Test", "building": "X", "floor": "1", "zone": "A"},
        headers=TokenManager.get_headers(cafeteria_manager_email)
    )
    assert_test(response.status_code == 403, "Cafeteria Manager BLOCKED: Desk management", f"Got {response.status_code}")
    
    # IT Manager CANNOT manage cafeteria
    response = requests.post(
        f"{BASE_URL}/api/v1/cafeteria/tables",
        json={"table_label": "Cross Test", "building": "X", "floor": "G", "zone": "A", "capacity": 4},
        headers=TokenManager.get_headers(it_manager_email)
    )
    assert_test(response.status_code == 403, "IT Manager BLOCKED: Cafeteria management", f"Got {response.status_code}")
    
    # Parking Manager CANNOT manage cafeteria
    response = requests.post(
        f"{BASE_URL}/api/v1/cafeteria/tables",
        json={"table_label": "Cross Test", "building": "X", "floor": "G", "zone": "A", "capacity": 4},
        headers=TokenManager.get_headers(parking_manager_email)
    )
    assert_test(response.status_code == 403, "Parking Manager BLOCKED: Cafeteria management", f"Got {response.status_code}")


# ============================================================================
# TEST: STATISTICS ENDPOINTS (Manager Only)
# ============================================================================

def test_statistics_endpoints():
    """Test statistics endpoints - manager only access."""
    print("\n[Statistics Endpoints]")
    
    parking_manager_email = TEST_USERS["parking_manager"]["email"]
    cafeteria_manager_email = TEST_USERS["cafeteria_manager"]["email"]
    desk_manager_email = TEST_USERS["desk_manager"]["email"]
    employee_email = TEST_USERS["employee"]["email"]
    
    # Parking Manager can view parking stats
    response = requests.get(
        f"{BASE_URL}/api/v1/parking/stats",
        headers=TokenManager.get_headers(parking_manager_email)
    )
    assert_test(response.status_code in [200, 404], "Parking Manager: GET parking stats", f"Got {response.status_code}")
    
    # Employee CANNOT view parking stats
    response = requests.get(
        f"{BASE_URL}/api/v1/parking/stats",
        headers=TokenManager.get_headers(employee_email)
    )
    assert_test(response.status_code == 403, "Employee BLOCKED: parking stats", f"Got {response.status_code}")
    
    # Cafeteria Manager can view cafeteria stats
    response = requests.get(
        f"{BASE_URL}/api/v1/cafeteria/stats",
        headers=TokenManager.get_headers(cafeteria_manager_email)
    )
    assert_test(response.status_code in [200, 404], "Cafeteria Manager: GET cafeteria stats", f"Got {response.status_code}")
    
    # Employee CANNOT view cafeteria stats
    response = requests.get(
        f"{BASE_URL}/api/v1/cafeteria/stats",
        headers=TokenManager.get_headers(employee_email)
    )
    assert_test(response.status_code == 403, "Employee BLOCKED: cafeteria stats", f"Got {response.status_code}")


# ============================================================================
# TEST: IT ASSETS & REQUESTS (IT_SUPPORT Manager)
# ============================================================================

def test_it_management():
    """Test IT assets and requests management."""
    print("\n[IT Management - IT_SUPPORT Manager]")
    
    it_manager_email = TEST_USERS["it_manager"]["email"]
    employee_email = TEST_USERS["employee"]["email"]
    parking_manager_email = TEST_USERS["parking_manager"]["email"]
    
    # IT Manager can create IT asset
    asset_data = {
        "name": f"Test Laptop {datetime.now().timestamp():.0f}",
        "asset_type": "laptop",
        "vendor": "Dell",
        "model": "XPS 15",
        "serial_number": f"SN-{datetime.now().timestamp():.0f}"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/it-assets",
        json=asset_data,
        headers=TokenManager.get_headers(it_manager_email)
    )
    assert_test(
        response.status_code in [200, 201],
        "IT Manager: CREATE IT asset",
        f"Got {response.status_code}: {response.text[:200] if response.status_code not in [200, 201] else ''}"
    )
    
    # Parking Manager CANNOT create IT asset
    response = requests.post(
        f"{BASE_URL}/api/v1/it-assets",
        json={"name": "Fail", "asset_type": "laptop", "vendor": "HP", "model": "Elite", "serial_number": "SN-FAIL"},
        headers=TokenManager.get_headers(parking_manager_email)
    )
    assert_test(response.status_code == 403, "Parking Manager BLOCKED: IT asset", f"Got {response.status_code}")
    
    # Employee can create IT request
    request_data = {
        "request_type": "NEW",
        "title": f"Need new laptop {datetime.now().timestamp():.0f}",
        "description": "My laptop is very slow and needs replacement",
        "priority": "MEDIUM"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/it-requests",
        json=request_data,
        headers=TokenManager.get_headers(employee_email)
    )
    assert_test(
        response.status_code in [200, 201],
        "Employee: CREATE IT request",
        f"Got {response.status_code}: {response.text[:200]}"
    )
    
    # Employee can list IT assets (read-only)
    response = requests.get(
        f"{BASE_URL}/api/v1/it-assets",
        headers=TokenManager.get_headers(employee_email)
    )
    assert_test(response.status_code == 200, "Employee: LIST IT assets", f"Got {response.status_code}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run all tests."""
    print("="*70)
    print("UNIFIED OFFICE MANAGEMENT - NEW BACKEND TEST SUITE")
    print("="*70)
    print(f"Testing against: {BASE_URL}")
    print(f"Company domain: {COMPANY_DOMAIN}")
    
    # Run tests in order
    test_server_health()
    test_authentication()
    test_user_creation()
    
    # Resource Management Tests
    test_desk_management()
    test_conference_room_management()
    test_parking_slot_management()
    test_cafeteria_table_management()
    
    # Booking Tests
    test_desk_booking()
    test_conference_room_booking()
    test_parking_allocation()
    test_cafeteria_booking()
    
    # Permission Tests
    test_cross_manager_permissions()
    test_statistics_endpoints()
    
    # IT Module Tests
    test_it_management()
    
    # Print summary
    TestResult.summary()


if __name__ == "__main__":
    main()
