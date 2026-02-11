# Testing Guide

## Prerequisites

The test suite requires a PostgreSQL database with the pgvector extension. You can use the same database as development or create a separate test database.

## Setup Test Database

### Option 1: Use Docker Compose (Recommended)

The easiest way is to use the existing Docker Compose setup:

```bash
# Start PostgreSQL database
docker compose up -d db

# The database will be available at:
# Host: localhost
# Port: 5432
# Database: office_management
# User: office_admin
# Password: office_password
```

### Option 2: Manual PostgreSQL Setup

Create a test database manually:

```sql
CREATE DATABASE office_management_test;
CREATE USER office_admin WITH PASSWORD 'office_password';
GRANT ALL PRIVILEGES ON DATABASE office_management_test TO office_admin;

-- Connect to the database and enable pgvector
\c office_management_test
CREATE EXTENSION IF NOT EXISTS vector;
```

## Running Tests

### Run all tests

```bash
# Using pytest
pytest test_all.py -v

# With coverage report
pytest test_all.py -v --cov=app --cov-report=html

# Run specific test
pytest test_all.py::test_authentication_workflow -v
```

### Environment Variables

Set the test database URL (optional, defaults to localhost):

```bash
export TEST_DATABASE_URL="postgresql+asyncpg://office_admin:office_password@localhost:5432/office_management_test"
```

Or create a `.env.test` file:

```env
TEST_DATABASE_URL=postgresql+asyncpg://office_admin:office_password@localhost:5432/office_management_test
```

## Test Structure

The `test_all.py` file contains comprehensive tests for:

### 1. Authentication Tests
- User login
- Token refresh
- Password change
- Get current user

### 2. User Management Tests
- User hierarchy creation
- CRUD operations
- Role-based access control

### 3. Attendance Tests
- Check-in/check-out workflow
- Multiple check-ins per day
- Submission and approval process

### 4. Leave Management Tests
- Leave request creation
- Two-level approval workflow
- Leave balance tracking
- Cancellation

### 5. Parking Tests
- Slot creation and management
- Allocation and release
- Visitor parking
- Parking logs

### 6. Desk & Conference Room Tests
- Desk booking (date-range based)
- Conference room booking with approval
- Booking cancellation

### 7. Food Ordering Tests
- Multi-item cart functionality
- Order lifecycle
- RBAC enforcement (users see only own orders)

### 8. IT Asset Tests
- Asset creation
- Assignment and unassignment
- Asset history tracking

### 9. IT Request Tests
- Request creation (8 types)
- Approval/rejection workflow

### 10. Project Management Tests
- Project proposal creation
- Admin approval workflow

### 11. Holiday Management Tests
- Holiday CRUD operations
- Calendar management

### 12. RBAC Tests
- Permission enforcement across all roles
- Access control validation

### 13. Error Handling Tests
- Validation errors
- Business rule violations
- Edge cases

### 14. Pagination Tests
- Paginated responses
- Page size limits

### 15. Search Tests
- Semantic search functionality
- AI-powered search

## Test Database Cleanup

The tests automatically:
- Create all tables before each test
- Drop all tables after each test
- Ensure isolation between tests

## Troubleshooting

### Database Connection Error

If you get connection errors:

```bash
# Check if PostgreSQL is running
docker compose ps

# Restart PostgreSQL
docker compose restart db

# Check logs
docker compose logs db
```

### Permission Errors

If you get permission errors:

```sql
-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE office_management_test TO office_admin;
GRANT ALL ON SCHEMA public TO office_admin;
```

### UUID Type Error

If you see UUID type errors, ensure you're using PostgreSQL (not SQLite). The application uses PostgreSQL-specific UUID types.

## CI/CD Integration

For CI/CD pipelines, use the Docker Compose setup:

```yaml
# .github/workflows/test.yml example
services:
  postgres:
    image: ankane/pgvector:latest
    env:
      POSTGRES_DB: office_management_test
      POSTGRES_USER: office_admin
      POSTGRES_PASSWORD: office_password
    ports:
      - 5432:5432
```

## Quick Start

```bash
# 1. Start database
docker compose up -d db

# 2. Run tests
pytest test_all.py -v

# 3. View coverage report
pytest test_all.py --cov=app --cov-report=html
open htmlcov/index.html  # Opens coverage report in browser
```

## Test Output

Successful test output should look like:

```
test_all.py::test_authentication_workflow PASSED
test_all.py::test_user_hierarchy_workflow PASSED
test_all.py::test_complete_attendance_workflow PASSED
test_all.py::test_complete_leave_workflow PASSED
test_all.py::test_parking_workflow PASSED
test_all.py::test_desk_booking_workflow PASSED
test_all.py::test_food_ordering_workflow PASSED
test_all.py::test_it_asset_workflow PASSED
test_all.py::test_it_request_workflow PASSED
test_all.py::test_project_workflow PASSED
test_all.py::test_holiday_workflow PASSED
test_all.py::test_rbac_enforcement PASSED
test_all.py::test_error_handling PASSED
test_all.py::test_pagination PASSED
test_all.py::test_semantic_search PASSED

================ 15 passed in 45.23s ================
```
