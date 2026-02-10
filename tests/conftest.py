"""
Pytest configuration and shared fixtures for API tests.
"""
import os
import pytest
import httpx

# Test configuration
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")
API_V1 = f"{BASE_URL}/api/v1"

# Default super admin credentials
SUPER_ADMIN_EMAIL = "super.admin@company.com"
SUPER_ADMIN_PASSWORD = "Admin@123"


@pytest.fixture(scope="session")
def base_url():
    """Base URL for API tests."""
    return BASE_URL


@pytest.fixture(scope="session")
def api_v1_url():
    """API v1 URL."""
    return API_V1


@pytest.fixture(scope="session")
def http_client():
    """Shared HTTP client for session."""
    client = httpx.Client(timeout=30.0)
    yield client
    client.close()


@pytest.fixture(scope="session")
def super_admin_token(http_client, api_v1_url):
    """Get super admin authentication token."""
    response = http_client.post(
        f"{api_v1_url}/auth/login",
        json={"email": SUPER_ADMIN_EMAIL, "password": SUPER_ADMIN_PASSWORD}
    )
    if response.status_code == 200:
        return response.json().get("data", {}).get("access_token")
    pytest.fail("Failed to get super admin token")


@pytest.fixture(scope="session")
def auth_headers(super_admin_token):
    """Authentication headers with super admin token."""
    return {"Authorization": f"Bearer {super_admin_token}"}


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "edge_case: mark test as edge case test")
    config.addinivalue_line("markers", "access_control: mark test as access control test")


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on markers."""
    # Add markers based on test file names
    for item in items:
        if "access_control" in item.nodeid:
            item.add_marker(pytest.mark.access_control)
        if "edge_case" in item.nodeid:
            item.add_marker(pytest.mark.edge_case)
