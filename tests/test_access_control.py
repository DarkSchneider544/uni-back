"""
Access Control Tests for Unified Office Management System

Tests role-based access control (RBAC) and manager type permissions.
"""
import os
import pytest
import httpx
from uuid import uuid4

BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")
API_V1 = f"{BASE_URL}/api/v1"

# Test user credentials
SUPER_ADMIN = {"email": "super.admin@company.com", "password": "Admin@123"}


class TestClient:
    """HTTP client wrapper."""
    
    def __init__(self):
        self.client = httpx.Client(timeout=30.0)
        self.tokens = {}
        
    def login(self, email: str, password: str) -> dict:
        response = self.client.post(f"{API_V1}/auth/login", json={"email": email, "password": password})
        if response.status_code == 200:
            self.tokens[email] = response.json().get("data", {}).get("access_token")
        return response
    
    def get_headers(self, email: str):
        return {"Authorization": f"Bearer {self.tokens.get(email, '')}"} if email else {}
    
    def get(self, url: str, email: str = None, **kwargs):
        return self.client.get(f"{API_V1}{url}", headers=self.get_headers(email), **kwargs)
    
    def post(self, url: str, email: str = None, **kwargs):
        return self.client.post(f"{API_V1}{url}", headers=self.get_headers(email), **kwargs)
    
    def put(self, url: str, email: str = None, **kwargs):
        return self.client.put(f"{API_V1}{url}", headers=self.get_headers(email), **kwargs)
    
    def delete(self, url: str, email: str = None, **kwargs):
        return self.client.delete(f"{API_V1}{url}", headers=self.get_headers(email), **kwargs)
    
    def close(self):
        self.client.close()


client = TestClient()
test_users = {}


@pytest.fixture(scope="module", autouse=True)
def setup_test_users():
    """Create test users for access control testing."""
    global test_users
    
    # Login as super admin
    client.login(**SUPER_ADMIN)
    
    # Create test users for each role/manager type
    users_to_create = [
        {"role": "admin", "manager_type": None, "key": "admin"},
        {"role": "manager", "manager_type": "parking", "key": "parking_mgr"},
        {"role": "manager", "manager_type": "desk_conference", "key": "desk_mgr"},
        {"role": "manager", "manager_type": "cafeteria", "key": "cafeteria_mgr"},
        {"role": "manager", "manager_type": "it_support", "key": "it_mgr"},
        {"role": "manager", "manager_type": "attendance", "key": "attendance_mgr"},
        {"role": "team_lead", "manager_type": None, "key": "team_lead"},
        {"role": "employee", "manager_type": None, "key": "employee"},
    ]
    
    for user_info in users_to_create:
        suffix = uuid4().hex[:6]
        user_data = {
            "email": f"test_{user_info['key']}_{suffix}@company.com",
            "password": "Test@123",
            "full_name": f"Test {user_info['key'].replace('_', ' ').title()}",
            "role": user_info["role"],
            "department": "Test"
        }
        if user_info["manager_type"]:
            user_data["manager_type"] = user_info["manager_type"]
        
        response = client.post("/users", email=SUPER_ADMIN["email"], json=user_data)
        if response.status_code in [200, 201]:
            test_users[user_info["key"]] = {
                "email": user_data["email"],
                "password": "Test@123",
                "data": response.json().get("data", {})
            }
            client.login(user_data["email"], "Test@123")
    
    yield
    client.close()


# ==============================================================================
# ROLE HIERARCHY TESTS
# ==============================================================================

class TestRoleHierarchy:
    """Test role-based access hierarchy."""
    
    def test_super_admin_can_create_admin(self):
        """Super Admin can create Admin users."""
        user_data = {
            "email": f"new_admin_{uuid4().hex[:6]}@company.com",
            "password": "Admin@123",
            "full_name": "New Admin",
            "role": "admin",
            "department": "IT"
        }
        response = client.post("/users", email=SUPER_ADMIN["email"], json=user_data)
        assert response.status_code in [200, 201]
    
    def test_admin_cannot_create_super_admin(self):
        """Admin cannot create Super Admin users."""
        if "admin" not in test_users:
            pytest.skip("Admin user not created")
        
        user_data = {
            "email": f"fake_super_{uuid4().hex[:6]}@company.com",
            "password": "Admin@123",
            "full_name": "Fake Super Admin",
            "role": "super_admin",
            "department": "IT"
        }
        response = client.post("/users", email=test_users["admin"]["email"], json=user_data)
        assert response.status_code in [400, 403, 422]
    
    def test_manager_cannot_create_admin(self):
        """Manager cannot create Admin users."""
        if "parking_mgr" not in test_users:
            pytest.skip("Parking manager not created")
        
        user_data = {
            "email": f"fake_admin_{uuid4().hex[:6]}@company.com",
            "password": "Admin@123",
            "full_name": "Fake Admin",
            "role": "admin",
            "department": "IT"
        }
        response = client.post("/users", email=test_users["parking_mgr"]["email"], json=user_data)
        assert response.status_code == 403
    
    def test_team_lead_cannot_create_manager(self):
        """Team Lead cannot create Manager users."""
        if "team_lead" not in test_users:
            pytest.skip("Team Lead not created")
        
        user_data = {
            "email": f"fake_mgr_{uuid4().hex[:6]}@company.com",
            "password": "Manager@123",
            "full_name": "Fake Manager",
            "role": "manager",
            "manager_type": "parking",
            "department": "Facilities"
        }
        response = client.post("/users", email=test_users["team_lead"]["email"], json=user_data)
        assert response.status_code == 403
    
    def test_employee_cannot_create_any_user(self):
        """Employee cannot create any users."""
        if "employee" not in test_users:
            pytest.skip("Employee not created")
        
        user_data = {
            "email": f"fake_emp_{uuid4().hex[:6]}@company.com",
            "password": "Emp@123",
            "full_name": "Fake Employee",
            "role": "employee",
            "department": "Test"
        }
        response = client.post("/users", email=test_users["employee"]["email"], json=user_data)
        assert response.status_code == 403


# ==============================================================================
# MANAGER TYPE ACCESS TESTS
# ==============================================================================

class TestManagerTypeAccess:
    """Test manager type specific access."""
    
    # ==================== PARKING MANAGER ====================
    
    def test_parking_manager_can_create_parking_slot(self):
        """Parking manager can create parking slots."""
        if "parking_mgr" not in test_users:
            pytest.skip("Parking manager not created")
        
        slot_data = {"slot_label": f"TestSlot-{uuid4().hex[:6]}"}
        response = client.post("/parking/slots", email=test_users["parking_mgr"]["email"], json=slot_data)
        assert response.status_code in [200, 201]
    
    def test_parking_manager_can_view_parking_stats(self):
        """Parking manager can view parking statistics."""
        if "parking_mgr" not in test_users:
            pytest.skip("Parking manager not created")
        
        response = client.get("/parking/stats", email=test_users["parking_mgr"]["email"])
        assert response.status_code == 200
    
    def test_parking_manager_cannot_create_desk(self):
        """Parking manager cannot create desks."""
        if "parking_mgr" not in test_users:
            pytest.skip("Parking manager not created")
        
        desk_data = {"desk_label": f"UnauthorizedDesk-{uuid4().hex[:6]}"}
        response = client.post("/desks", email=test_users["parking_mgr"]["email"], json=desk_data)
        assert response.status_code == 403
    
    def test_parking_manager_cannot_create_cafeteria_table(self):
        """Parking manager cannot create cafeteria tables."""
        if "parking_mgr" not in test_users:
            pytest.skip("Parking manager not created")
        
        table_data = {"table_label": f"UnauthorizedTable-{uuid4().hex[:6]}", "capacity": 4}
        response = client.post("/cafeteria/tables", email=test_users["parking_mgr"]["email"], json=table_data)
        assert response.status_code == 403
    
    # ==================== DESK/CONFERENCE MANAGER ====================
    
    def test_desk_manager_can_create_desk(self):
        """Desk manager can create desks."""
        if "desk_mgr" not in test_users:
            pytest.skip("Desk manager not created")
        
        desk_data = {"desk_label": f"TestDesk-{uuid4().hex[:6]}"}
        response = client.post("/desks", email=test_users["desk_mgr"]["email"], json=desk_data)
        assert response.status_code in [200, 201]
    
    def test_desk_manager_can_create_conference_room(self):
        """Desk manager can create conference rooms."""
        if "desk_mgr" not in test_users:
            pytest.skip("Desk manager not created")
        
        room_data = {"room_name": f"TestRoom-{uuid4().hex[:6]}", "capacity": 10}
        response = client.post("/desks/conference-rooms", email=test_users["desk_mgr"]["email"], json=room_data)
        assert response.status_code in [200, 201]
    
    def test_desk_manager_cannot_create_parking_slot(self):
        """Desk manager cannot create parking slots."""
        if "desk_mgr" not in test_users:
            pytest.skip("Desk manager not created")
        
        slot_data = {"slot_label": f"UnauthorizedSlot-{uuid4().hex[:6]}"}
        response = client.post("/parking/slots", email=test_users["desk_mgr"]["email"], json=slot_data)
        assert response.status_code == 403
    
    # ==================== CAFETERIA MANAGER ====================
    
    def test_cafeteria_manager_can_create_table(self):
        """Cafeteria manager can create tables."""
        if "cafeteria_mgr" not in test_users:
            pytest.skip("Cafeteria manager not created")
        
        table_data = {"table_label": f"TestTable-{uuid4().hex[:6]}", "capacity": 4}
        response = client.post("/cafeteria/tables", email=test_users["cafeteria_mgr"]["email"], json=table_data)
        assert response.status_code in [200, 201]
    
    def test_cafeteria_manager_can_view_cafeteria_stats(self):
        """Cafeteria manager can view cafeteria statistics."""
        if "cafeteria_mgr" not in test_users:
            pytest.skip("Cafeteria manager not created")
        
        response = client.get("/cafeteria/stats", email=test_users["cafeteria_mgr"]["email"])
        assert response.status_code == 200
    
    def test_cafeteria_manager_cannot_create_desk(self):
        """Cafeteria manager cannot create desks."""
        if "cafeteria_mgr" not in test_users:
            pytest.skip("Cafeteria manager not created")
        
        desk_data = {"desk_label": f"UnauthorizedDesk-{uuid4().hex[:6]}"}
        response = client.post("/desks", email=test_users["cafeteria_mgr"]["email"], json=desk_data)
        assert response.status_code == 403
    
    # ==================== IT MANAGER ====================
    
    def test_it_manager_can_create_it_asset(self):
        """IT manager can create IT assets."""
        if "it_mgr" not in test_users:
            pytest.skip("IT manager not created")
        
        asset_data = {
            "asset_tag": f"IT-{uuid4().hex[:8]}",
            "asset_type": "laptop",
            "brand": "Dell",
            "model": "XPS 15"
        }
        response = client.post("/it-assets", email=test_users["it_mgr"]["email"], json=asset_data)
        assert response.status_code in [200, 201]
    
    def test_it_manager_cannot_create_parking_slot(self):
        """IT manager cannot create parking slots."""
        if "it_mgr" not in test_users:
            pytest.skip("IT manager not created")
        
        slot_data = {"slot_label": f"UnauthorizedSlot-{uuid4().hex[:6]}"}
        response = client.post("/parking/slots", email=test_users["it_mgr"]["email"], json=slot_data)
        assert response.status_code == 403


# ==============================================================================
# EMPLOYEE ACCESS TESTS
# ==============================================================================

class TestEmployeeAccess:
    """Test employee access permissions."""
    
    def test_employee_can_view_desks(self):
        """Employee can view desks."""
        if "employee" not in test_users:
            pytest.skip("Employee not created")
        
        response = client.get("/desks", email=test_users["employee"]["email"])
        assert response.status_code == 200
    
    def test_employee_can_view_parking_slots(self):
        """Employee can view parking slots."""
        if "employee" not in test_users:
            pytest.skip("Employee not created")
        
        response = client.get("/parking/slots", email=test_users["employee"]["email"])
        assert response.status_code == 200
    
    def test_employee_can_view_cafeteria_tables(self):
        """Employee can view cafeteria tables."""
        if "employee" not in test_users:
            pytest.skip("Employee not created")
        
        response = client.get("/cafeteria/tables", email=test_users["employee"]["email"])
        assert response.status_code == 200
    
    def test_employee_cannot_create_desk(self):
        """Employee cannot create desks."""
        if "employee" not in test_users:
            pytest.skip("Employee not created")
        
        desk_data = {"desk_label": "EmpDesk"}
        response = client.post("/desks", email=test_users["employee"]["email"], json=desk_data)
        assert response.status_code == 403
    
    def test_employee_cannot_create_parking_slot(self):
        """Employee cannot create parking slots."""
        if "employee" not in test_users:
            pytest.skip("Employee not created")
        
        slot_data = {"slot_label": "EmpSlot"}
        response = client.post("/parking/slots", email=test_users["employee"]["email"], json=slot_data)
        assert response.status_code == 403
    
    def test_employee_cannot_create_cafeteria_table(self):
        """Employee cannot create cafeteria tables."""
        if "employee" not in test_users:
            pytest.skip("Employee not created")
        
        table_data = {"table_label": "EmpTable", "capacity": 4}
        response = client.post("/cafeteria/tables", email=test_users["employee"]["email"], json=table_data)
        assert response.status_code == 403
    
    def test_employee_cannot_view_parking_stats(self):
        """Employee cannot view parking statistics."""
        if "employee" not in test_users:
            pytest.skip("Employee not created")
        
        response = client.get("/parking/stats", email=test_users["employee"]["email"])
        assert response.status_code == 403
    
    def test_employee_cannot_view_cafeteria_stats(self):
        """Employee cannot view cafeteria statistics."""
        if "employee" not in test_users:
            pytest.skip("Employee not created")
        
        response = client.get("/cafeteria/stats", email=test_users["employee"]["email"])
        assert response.status_code == 403
    
    def test_employee_cannot_delete_resources(self):
        """Employee cannot delete any resources."""
        if "employee" not in test_users:
            pytest.skip("Employee not created")
        
        fake_id = str(uuid4())
        
        response = client.delete(f"/desks/{fake_id}", email=test_users["employee"]["email"])
        assert response.status_code in [403, 404]
        
        response = client.delete(f"/parking/slots/{fake_id}", email=test_users["employee"]["email"])
        assert response.status_code in [403, 404]
        
        response = client.delete(f"/cafeteria/tables/{fake_id}", email=test_users["employee"]["email"])
        assert response.status_code in [403, 404]


# ==============================================================================
# SUPER ADMIN FULL ACCESS TESTS
# ==============================================================================

class TestSuperAdminAccess:
    """Test super admin has full access to everything."""
    
    def test_super_admin_can_manage_all_resources(self):
        """Super admin can create all resource types."""
        # Create desk
        desk_data = {"desk_label": f"SADesk-{uuid4().hex[:6]}"}
        response = client.post("/desks", email=SUPER_ADMIN["email"], json=desk_data)
        assert response.status_code in [200, 201]
        
        # Create parking slot
        slot_data = {"slot_label": f"SASlot-{uuid4().hex[:6]}"}
        response = client.post("/parking/slots", email=SUPER_ADMIN["email"], json=slot_data)
        assert response.status_code in [200, 201]
        
        # Create cafeteria table
        table_data = {"table_label": f"SATable-{uuid4().hex[:6]}", "capacity": 4}
        response = client.post("/cafeteria/tables", email=SUPER_ADMIN["email"], json=table_data)
        assert response.status_code in [200, 201]
    
    def test_super_admin_can_view_all_stats(self):
        """Super admin can view all statistics."""
        response = client.get("/parking/stats", email=SUPER_ADMIN["email"])
        assert response.status_code == 200
        
        response = client.get("/cafeteria/stats", email=SUPER_ADMIN["email"])
        assert response.status_code == 200
    
    def test_super_admin_can_manage_users(self):
        """Super admin can manage all users."""
        response = client.get("/users", email=SUPER_ADMIN["email"])
        assert response.status_code == 200


# ==============================================================================
# CROSS-MANAGER ISOLATION TESTS
# ==============================================================================

class TestCrossManagerIsolation:
    """Test that managers cannot access each other's resources."""
    
    def test_parking_manager_cannot_update_desk(self):
        """Parking manager cannot update desks created by desk manager."""
        if "parking_mgr" not in test_users:
            pytest.skip("Parking manager not created")
        
        # First create a desk as super admin
        desk_data = {"desk_label": f"TestDesk-{uuid4().hex[:6]}"}
        create_response = client.post("/desks", email=SUPER_ADMIN["email"], json=desk_data)
        
        if create_response.status_code in [200, 201]:
            desk_id = create_response.json().get("data", {}).get("id")
            
            # Try to update as parking manager
            update_data = {"desk_label": "Hacked Desk"}
            response = client.put(f"/desks/{desk_id}", email=test_users["parking_mgr"]["email"], json=update_data)
            assert response.status_code == 403
    
    def test_cafeteria_manager_cannot_delete_parking_slot(self):
        """Cafeteria manager cannot delete parking slots."""
        if "cafeteria_mgr" not in test_users:
            pytest.skip("Cafeteria manager not created")
        
        # First create a parking slot as super admin
        slot_data = {"slot_label": f"TestSlot-{uuid4().hex[:6]}"}
        create_response = client.post("/parking/slots", email=SUPER_ADMIN["email"], json=slot_data)
        
        if create_response.status_code in [200, 201]:
            slot_id = create_response.json().get("data", {}).get("id")
            
            # Try to delete as cafeteria manager
            response = client.delete(f"/parking/slots/{slot_id}", email=test_users["cafeteria_mgr"]["email"])
            assert response.status_code == 403
    
    def test_desk_manager_cannot_update_cafeteria_table(self):
        """Desk manager cannot update cafeteria tables."""
        if "desk_mgr" not in test_users:
            pytest.skip("Desk manager not created")
        
        # First create a table as super admin
        table_data = {"table_label": f"TestTable-{uuid4().hex[:6]}", "capacity": 4}
        create_response = client.post("/cafeteria/tables", email=SUPER_ADMIN["email"], json=table_data)
        
        if create_response.status_code in [200, 201]:
            table_id = create_response.json().get("data", {}).get("id")
            
            # Try to update as desk manager
            update_data = {"table_label": "Hacked Table"}
            response = client.put(f"/cafeteria/tables/{table_id}", email=test_users["desk_mgr"]["email"], json=update_data)
            assert response.status_code == 403


# ==============================================================================
# UNAUTHENTICATED ACCESS TESTS
# ==============================================================================

class TestUnauthenticatedAccess:
    """Test that unauthenticated requests are rejected."""
    
    def test_cannot_access_desks_without_auth(self):
        """Cannot access desks without authentication."""
        response = httpx.get(f"{API_V1}/desks", timeout=10)
        assert response.status_code in [401, 403]
    
    def test_cannot_access_parking_without_auth(self):
        """Cannot access parking without authentication."""
        response = httpx.get(f"{API_V1}/parking/slots", timeout=10)
        assert response.status_code in [401, 403]
    
    def test_cannot_access_cafeteria_without_auth(self):
        """Cannot access cafeteria without authentication."""
        response = httpx.get(f"{API_V1}/cafeteria/tables", timeout=10)
        assert response.status_code in [401, 403]
    
    def test_cannot_access_users_without_auth(self):
        """Cannot access users without authentication."""
        response = httpx.get(f"{API_V1}/users", timeout=10)
        assert response.status_code in [401, 403]
    
    def test_cannot_create_resources_without_auth(self):
        """Cannot create resources without authentication."""
        desk_data = {"desk_label": "Unauthorized"}
        response = httpx.post(f"{API_V1}/desks", json=desk_data, timeout=10)
        assert response.status_code in [401, 403]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
