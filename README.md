# Unified Office Management System

A comprehensive, production-ready backend for managing office operations including parking, desk booking, cafeteria, attendance, leave management, IT assets, and project management.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [User Roles & Hierarchy](#user-roles--hierarchy)
- [API Endpoints Documentation](#api-endpoints-documentation)
  - [Authentication](#1-authentication-endpoints)
  - [User Management](#2-user-management-endpoints)
  - [Attendance](#3-attendance-endpoints)
  - [Leave Management](#4-leave-management-endpoints)
  - [Parking](#5-parking-endpoints)
  - [Desk & Conference Rooms](#6-desk--conference-room-endpoints)
  - [Cafeteria & Food](#7-cafeteria--food-ordering-endpoints)
  - [IT Assets](#8-it-asset-management-endpoints)
  - [IT Requests](#9-it-request-endpoints)
  - [Projects](#10-project-management-endpoints)
  - [Holidays](#11-holiday-management-endpoints)
  - [Search](#12-semantic-search-endpoints)
- [Testing](#testing)
- [Environment Variables](#environment-variables)

## Features

- **Authentication & Authorization**: JWT-based auth with role-based access control (RBAC)
- **User Management**: 5-tier hierarchical user system (Super Admin → Admin → Manager → Team Lead → Employee)
- **Parking Management**: Employee parking slot allocation and tracking
- **Desk & Conference Room Booking**: Time-based desk and meeting room reservations
- **Cafeteria Management**: Table booking and food ordering system
- **Attendance Tracking**: Check-in/out with hierarchical approval workflow
- **Leave Management**: Multi-level leave request and approval system
- **IT Asset Management**: Hardware inventory, tracking, and assignment
- **IT Support Requests**: IT request lifecycle from submission to resolution
- **Project Management**: Team lead project request and approval
- **Holiday Management**: Company holiday calendar
- **Semantic Search**: AI-powered vector search for food items and IT assets

## Tech Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with pgvector extension
- **ORM**: SQLAlchemy 2.0 (Async)
- **Migrations**: Alembic
- **Authentication**: OAuth2 with JWT (HS256)
- **AI/ML**: Sentence Transformers for semantic embeddings
- **Containerization**: Docker + Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- PostgreSQL 15+ with pgvector extension

### Running with Docker

```bash
# Clone the repository
git clone <repository-url>
cd unified-office-management

# Start the application
docker compose up --build

# The API will be available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### Default Credentials

**Super Admin**
- Email: `super.admin@company.com`
- Password: `Admin@123`
- Role: Full system access

**Admin**
- Email: `admin@company.com`
- Password: `Admin@123`
- Role: User and system management

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your PostgreSQL connection string

# Run migrations
alembic upgrade head

# Seed initial data (creates super admin and sample users)
python scripts/seed_hierarchy.py

# Start the server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## User Roles & Hierarchy

### Role Structure

```
┌─────────────────────────────────────────────────────────────────┐
│  SUPER_ADMIN (super.admin@company.com)                          │
│       │ creates & manages                                        │
│       ▼                                                          │
│    ADMIN (admin@company.com)                                     │
│       │ creates & manages                                        │
│       ▼                                                          │
│  MANAGER (5 types):                                              │
│    - Parking Manager (parking.manager@company.com)               │
│    - Attendance Manager (attendance.manager@company.com)         │
│    - Desk & Conference Manager (desk.manager@company.com)        │
│    - Cafeteria Manager (cafeteria.manager@company.com)           │
│    - IT Support Manager (it.manager@company.com)                 │
│       │ creates & manages                                        │
│       ▼                                                          │
│  TEAM_LEAD (Department-wise: Dev, Sales, AI, HR, etc.)          │
│       │ manages team members                                     │
│       ▼                                                          │
│  EMPLOYEE (Regular employees)                                    │
└─────────────────────────────────────────────────────────────────┘
```

### Role Permissions

| Role | Can Create | Can Approve | Special Permissions |
|------|-----------|-------------|---------------------|
| **SUPER_ADMIN** | ADMIN | Admin's requests | Full system access, change any password |
| **ADMIN** | MANAGER, TEAM_LEAD, EMPLOYEE | Manager's requests | Manage users, toggle user status |
| **MANAGER** | EMPLOYEE (varies by type) | Team Lead's requests | Domain-specific management (Parking, IT, etc.) |
| **TEAM_LEAD** | None | Employee's requests | Approve team attendance/leave, create projects |
| **EMPLOYEE** | None | None | Self-service: parking, desks, cafeteria, attendance, leave |

### Manager Types & Responsibilities

1. **Parking Manager** (`ManagerType.PARKING`)
   - Manage parking slots
   - View all parking allocations
   - Track entry/exit logs

2. **Attendance Manager** (`ManagerType.ATTENDANCE`)
   - View ALL company-wide attendance
   - Approve/override any attendance
   - Create department-wise Team Leads
   - Generate attendance reports

3. **Desk & Conference Manager** (`ManagerType.DESK_CONFERENCE`)
   - Manage desks and conference rooms
   - View all bookings
   - Configure room availability

4. **Cafeteria Manager** (`ManagerType.CAFETERIA`)
   - Manage cafeteria tables
   - Manage food menu items
   - View all orders and bookings

5. **IT Support Manager** (`ManagerType.IT_SUPPORT`)
   - Manage IT asset inventory
   - Assign/unassign IT equipment
   - Approve IT requests
   - Track asset lifecycle

### Approval Hierarchy

All attendance and leave requests follow this approval chain:

```
EMPLOYEE submits
    ↓
TEAM_LEAD approves (Level 1)
    ↓
MANAGER approves (Level 2 - if Team Lead submits)
    ↓
ADMIN approves (if Manager submits)
    ↓
SUPER_ADMIN approves (if Admin submits)
```

## API Endpoints Documentation

**Base URL**: `http://localhost:8000/api/v1`

**Authentication**: All endpoints (except login) require JWT Bearer token in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

**Standard Response Format**:
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful",
  "timestamp": "2026-02-11T10:30:00Z"
}
```

**Paginated Response Format**:
```json
{
  "success": true,
  "data": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "message": "Retrieved successfully",
  "timestamp": "2026-02-11T10:30:00Z"
}
```

---

## 1. Authentication Endpoints

### `POST /auth/login`
**Description**: Authenticate user and receive JWT tokens

**Access**: Public (no authentication required)

**Request Body**:
```json
{
  "email": "admin@company.com",
  "password": "Admin@123"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user_id": "uuid",
    "role": "admin",
    "manager_type": null
  },
  "message": "Login successful"
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid credentials
- `403 Forbidden`: User is inactive

---

### `POST /auth/refresh`
**Description**: Refresh access token using refresh token

**Request Body**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response**: Same as login response

---

### `POST /auth/change-password`
**Description**: Change own password

**Authentication**: Required

**Request Body**:
```json
{
  "current_password": "OldPass@123",
  "new_password": "NewPass@123"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

---

### `GET /auth/me`
**Description**: Get current authenticated user's information

**Authentication**: Required

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "user_code": "AB1234",
    "email": "user@company.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "employee",
    "manager_type": null,
    "department": "Engineering",
    "team_lead_code": "TL0001",
    "manager_code": "MG0001",
    "is_active": true,
    "created_at": "2026-01-01T00:00:00Z"
  }
}
```

---

## 2. User Management Endpoints

### `POST /users`
**Description**: Create a new user

**Access**: ADMIN or SUPER_ADMIN only

**Request Body**:
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@company.com",  // Optional - auto-generated if not provided
  "password": "SecurePass@123",
  "role": "employee",  // employee | team_lead | manager | admin
  "phone": "1234567890",  // Optional
  "department": "Engineering",  // Required for team_lead
  "manager_type": "attendance",  // Required for manager role
  "team_lead_code": "TL0001",  // Optional - assigns employee to team
  "manager_code": "MG0001",  // Optional - auto-assigned
  "vehicle_number": "ABC123",  // Optional
  "vehicle_type": "car"  // Optional: car | bike | two_wheeler
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "user_code": "AB1234",  // Auto-generated 6-char code
    "email": "john.doe@company.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "employee",
    "department": "Engineering",
    "team_lead_code": "TL0001",
    "is_active": true
  },
  "message": "User created successfully"
}
```

**Validation Rules**:
- Email must be unique
- Password min 8 characters
- `manager_type` required if role is "manager"
- `department` required if role is "team_lead"
- SUPER_ADMIN cannot be created via API

---

### `GET /users`
**Description**: List all users (paginated)

**Access**: ADMIN+ can see all, Team Lead sees team, others see self only

**Query Parameters**:
- `page` (int, default: 1)
- `page_size` (int, default: 20, max: 100)
- `role` (optional): Filter by role
- `department` (optional): Filter by department
- `is_active` (optional): Filter active/inactive users

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "user_code": "AB1234",
      "email": "user@company.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "employee",
      "department": "Engineering",
      "is_active": true
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 20
}
```

---

### `GET /users/me`
**Description**: Get current user's profile

**Authentication**: Required

**Response**: Same as GET /auth/me

---

### `GET /users/{user_id}`
**Description**: Get specific user by ID

**Access**: ADMIN+ can view any, others can only view self

**Response**: Single user object (same structure as list)

---

### `PUT /users/{user_id}`
**Description**: Update user details

**Access**: ADMIN+ can update any, users can update limited fields for self

**Request Body** (all fields optional):
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "phone": "9876543210",
  "department": "Sales",
  "team_lead_code": "TL0002",  // Admin/superior only
  "manager_code": "MG0001",  // Admin/superior only
  "is_active": true,  // Admin+ only
  "vehicle_number": "XYZ789",
  "vehicle_type": "bike"
}
```

**Response**: Updated user object

---

### `DELETE /users/{user_id}`
**Description**: Soft delete a user (marks as deleted, doesn't remove from DB)

**Access**: ADMIN or SUPER_ADMIN only

**Response**:
```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

---

### `POST /users/{user_id}/toggle-active`
**Description**: Activate or deactivate a user

**Access**: ADMIN or SUPER_ADMIN only

**Response**: Updated user object with new `is_active` status

---

### `POST /users/{user_id}/change-password`
**Description**: Admin changes any user's password

**Access**: SUPER_ADMIN only

**Request Body**:
```json
{
  "new_password": "NewSecurePass@123"
}
```

---

### `POST /users/{user_id}/change-role`
**Description**: Change user's role

**Access**: SUPER_ADMIN only

**Request Body**:
```json
{
  "new_role": "team_lead",
  "department": "Engineering",  // Required if changing to team_lead
  "manager_type": "attendance",  // Required if changing to manager
  "team_lead_code": "TL0001",  // Required if changing to employee
  "manager_code": "MG0001"  // Required if changing to employee or team_lead
}
```

---

## 3. Attendance Endpoints

### `POST /attendance/check-in`
**Description**: 🕐 **Simple check-in - just click the button!**

**Authentication**: Required (all roles)

**Request Body**: None needed!

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "user_code": "AB1234",
    "date": "2026-02-11",
    "status": "draft",
    "first_check_in": "09:00:00",
    "last_check_out": null,
    "total_hours": null,
    "entries": [
      {
        "id": "uuid",
        "check_in": "2026-02-11T09:00:00Z",
        "check_out": null,
        "entry_type": "regular",
        "duration_hours": null
      }
    ]
  },
  "message": "Check-in recorded successfully"
}
```

**How it works**:
- Creates attendance record for today automatically
- Multiple check-ins/check-outs allowed per day
- Returns error if already checked in (must check out first)

---

### `POST /attendance/check-out`
**Description**: 🕐 **Simple check-out - just click the button!**

**Authentication**: Required (all roles)

**Request Body**: None needed!

**Response**: Updated attendance record with calculated duration

**How it works**:
- Auto-finds your open check-in entry
- Calculates and records work duration
- Updates total hours for the day
- Returns error if not checked in

---

### `POST /attendance/{attendance_id}/submit`
**Description**: Submit attendance for approval

**Authentication**: Required

**Response**: Attendance with status changed to "pending_approval"

**Business Logic**:
- Changes status from "draft" to "pending_approval"
- Sets `submitted_at` timestamp
- Auto-assigns approver based on hierarchy

---

### `POST /attendance/{attendance_id}/approve`
**Description**: Approve or reject attendance

**Access**: TEAM_LEAD or above

**Request Body**:
```json
{
  "action": "approve",  // "approve" or "reject"
  "notes": "Approved - all good",  // Optional for approve
  "rejection_reason": "Missing check-out times"  // Required if action is "reject"
}
```

**Response**: Updated attendance with new status

**Business Logic**:
- Team Lead can approve their team members' attendance
- Manager can approve Team Lead's attendance
- Admin can approve Manager's attendance
- Attendance Manager can approve/view ALL attendance

---

### `GET /attendance/my`
**Description**: Get current user's attendance records

**Query Parameters**:
- `page` (int, default: 1)
- `page_size` (int, default: 20)
- `start_date` (date, optional): Filter from date
- `end_date` (date, optional): Filter to date

**Response**: Paginated list of attendance records

---

### `GET /attendance/pending-approvals`
**Description**: Get attendance records pending approval

**Access**: TEAM_LEAD or above

**Query Parameters**: Same as `/my`

**Response**: Paginated list of attendance awaiting approval

**Business Logic**:
- Team Lead sees their team's pending attendance
- Manager sees Team Leads' pending attendance
- Attendance Manager sees ALL pending attendance

---

### `GET /attendance`
**Description**: List all attendance records (filtered by permissions)

**Query Parameters**:
- `page`, `page_size`
- `user_id` (uuid, optional): Filter by specific user
- `status` (optional): draft | pending_approval | approved | rejected
- `start_date`, `end_date`

**Access**:
- Attendance Manager: ALL records
- Team Lead: Team members' records
- Others: Only own records

---

### `GET /attendance/{attendance_id}`
**Description**: Get specific attendance record

**Access**: Owner or superior in hierarchy

---

## 4. Leave Management Endpoints

### `POST /leave/requests`
**Description**: Create a leave request

**Authentication**: Required

**Request Body**:
```json
{
  "leave_type": "casual",  // casual | sick | privilege | unpaid
  "start_date": "2026-02-15",
  "end_date": "2026-02-16",
  "reason": "Personal work",
  "is_half_day": false,  // Optional
  "half_day_type": null  // "first_half" or "second_half" if is_half_day is true
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "user_code": "AB1234",
    "leave_type": "casual",
    "start_date": "2026-02-15",
    "end_date": "2026-02-16",
    "total_days": 2.0,
    "status": "pending_level1",  // pending_level1 | approved_level1 | approved_final | rejected
    "reason": "Personal work",
    "created_at": "2026-02-11T10:00:00Z"
  },
  "message": "Leave request created successfully"
}
```

**Validation**:
- Cannot request leave for past dates
- Cannot overlap with existing approved leave
- Checks available leave balance

---

### `GET /leave/requests`
**Description**: List leave requests

**Query Parameters**:
- `page`, `page_size`
- `user_id` (optional): Filter by user (Admin+ only)
- `status` (optional): Filter by status
- `leave_type` (optional)
- `start_date`, `end_date`: Date range filter

**Access**:
- ADMIN+: All requests
- Team Lead: Team members' requests
- Others: Own requests only

---

### `GET /leave/requests/my`
**Description**: Get current user's leave requests

---

### `GET /leave/requests/pending-level1`
**Description**: Get requests pending Team Lead approval

**Access**: TEAM_LEAD or above

---

### `GET /leave/requests/pending-final`
**Description**: Get requests pending Manager approval

**Access**: MANAGER or above

---

### `POST /leave/requests/{request_id}/approve-level1`
**Description**: Team Lead approves leave (Level 1 approval)

**Access**: TEAM_LEAD or above

**Request Body**:
```json
{
  "action": "approve",  // "approve" or "reject"
  "notes": "Approved by team lead",
  "rejection_reason": "Not enough coverage"  // Required if reject
}
```

**Response**: Updated leave request

**Business Logic**:
- Changes status from "pending_level1" to "approved_level1"
- For single-day leave, may auto-approve to "approved_final"

---

### `POST /leave/requests/{request_id}/approve-final`
**Description**: Manager final approval (Level 2)

**Access**: MANAGER or above

**Request Body**: Same as level1

**Business Logic**:
- Changes status to "approved_final"
- Deducts from user's leave balance
- Can only approve if Level 1 is already approved

---

### `POST /leave/requests/{request_id}/cancel`
**Description**: Cancel own leave request

**Access**: Request owner (before approval) or ADMIN

**Response**: Leave request with status "cancelled"

---

### `GET /leave/balance`
**Description**: Get current user's leave balance

**Response**:
```json
{
  "success": true,
  "data": {
    "user_code": "AB1234",
    "casual_leave": 8.0,
    "sick_leave": 10.0,
    "privilege_leave": 15.0,
    "total_available": 33.0
  }
}
```

---

### `GET /leave/balance/{user_id}`
**Description**: Get specific user's leave balance

**Access**: ADMIN or above

---

## 5. Parking Endpoints

Parking is now simple and easy! Everyone can use parking (allocate/release their slot), while Parking Managers, Admins, and Super Admins have full access to manage slots.

### **User Operations (Everyone)**

### `POST /parking/allocate`
**Description**: 🅿️ **Get a parking slot - just click the button!**

**Authentication**: Required

**Request Body**: None (everything auto-filled!)

**Response**:
```json
{
  "success": true,
  "data": {
    "message": "Parking allocated successfully",
    "slot_code": "A-01",
    "vehicle_number": "ABC123",
    "vehicle_type": "car",
    "entry_time": "2026-02-11T09:00:00Z"
  },
  "message": "Parking allocated successfully"
}
```

**How it works**:
- Auto-assigns first available parking slot
- Uses vehicle info from your profile
- One parking per user at a time

**Error Cases**:
- `400`: Already have active parking or no vehicle number in profile
- `404`: No available parking slots

---

### `POST /parking/release`
**Description**: 🚗 **Release your parking slot - just click the button!**

**Authentication**: Required

**Request Body**: None (everything auto-filled!)

**Response**:
```json
{
  "success": true,
  "data": {
    "message": "Parking released successfully",
    "slot_code": "A-01",
    "vehicle_number": "ABC123",
    "entry_time": "2026-02-11T09:00:00Z",
    "exit_time": "2026-02-11T18:00:00Z",
    "duration_mins": 540
  },
  "message": "Parking released successfully"
}
```

**How it works**:
- Auto-finds your active parking
- Calculates parking duration
- Frees up the slot for others

**Error Cases**:
- `404`: No active parking found

---

### `GET /parking/my-slot`
**Description**: 📍 **Check your current parking status**

**Authentication**: Required

**Response (has parking)**:
```json
{
  "success": true,
  "data": {
    "has_active_parking": true,
    "slot": {"id": "uuid", "slot_code": "A-01"},
    "vehicle": {"vehicle_number": "ABC123", "vehicle_type": "car"},
    "entry_time": "2026-02-11T09:00:00Z"
  },
  "message": "Active parking found"
}
```

**Response (no parking)**:
```json
{
  "success": true,
  "data": {
    "has_active_parking": false,
    "slot": null,
    "vehicle": {"vehicle_number": "ABC123", "vehicle_type": "car"},
    "entry_time": null
  },
  "message": "No active parking"
}
```

---

### **Admin Operations (Parking Manager, Admin, Super Admin)**

### `GET /parking/slots/summary`
**Description**: 📊 Get parking slot statistics

**Response**:
```json
{
  "success": true,
  "data": {
    "total": 15,
    "available": 10,
    "occupied": 5,
    "disabled": 0
  },
  "message": "Parking statistics retrieved"
}
```

---

### `GET /parking/slots/list`
**Description**: 📋 List all parking slots with occupant details

**Query Parameters**:
- `skip` (optional): Offset for pagination (default: 0)
- `limit` (optional): Max results (default: 100)
- `status` (optional): AVAILABLE | OCCUPIED | DISABLED

**Response**:
```json
{
  "success": true,
  "data": {
    "total": 15,
    "slots": [
      {
        "id": "uuid",
        "slot_code": "A-01",
        "status": "available",
        "current_occupant": null,
        "vehicle_number": null
      }
    ]
  },
  "message": "Slots retrieved successfully"
}
```

---

### `POST /parking/slots/create`
**Description**: ➕ Create a new parking slot

**Access**: Parking Manager, Admin, Super Admin only

**Query Parameters**:
- `slot_code` (required): Unique slot code (e.g., A-01, B-05)

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "slot_code": "A-01",
    "status": "available"
  },
  "message": "Slot created successfully"
}
```

---

### `DELETE /parking/slots/delete/{slot_code}`
**Description**: 🗑️ Delete a parking slot

**Access**: Parking Manager, Admin, Super Admin only

**Note**: Cannot delete occupied slots

---

### `POST /parking/slots/change-status/{slot_code}`
**Description**: 🔄 Change slot status

**Access**: Parking Manager, Admin, Super Admin only

**Query Parameters**:
- `new_status` (required): AVAILABLE | OCCUPIED | DISABLED

**Note**: If changing from OCCUPIED to AVAILABLE, auto-releases parking

---

### `POST /parking/slots/assign-visitor`
**Description**: 👤 Assign a slot to a visitor

**Access**: Parking Manager, Admin, Super Admin only

**Query Parameters**:
- `visitor_name` (required): Visitor's name
- `vehicle_number` (required): Vehicle number
- `vehicle_type` (optional): CAR or BIKE (default: CAR)
- `slot_code` (required): Slot code to assign

**Response**:
```json
{
  "success": true,
  "data": {
    "message": "Visitor assigned to slot successfully",
    "slot_code": "A-01",
    "visitor_name": "John Smith",
    "vehicle_number": "XYZ789"
  },
  "message": "Visitor assigned to slot successfully"
}
```

---

### `GET /parking/logs/list`
**Description**: 📜 Get parking history logs

**Access**: Parking Manager, Admin, Super Admin only

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 20)
- `is_active` (optional): Filter by active/inactive allocations

**Response**:
```json
{
  "success": true,
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "logs": [
      {
        "id": "uuid",
        "user_name": "John Doe",
        "slot_code": "A-01",
        "vehicle_number": "ABC123",
        "entry_time": "2026-02-11T09:00:00Z",
        "exit_time": "2026-02-11T18:00:00Z",
        "duration_mins": 540,
        "is_active": false
      }
    ]
  },
  "message": "Parking logs retrieved"
}
```

---

## 6. Desk & Conference Room Endpoints

### `GET /desks`
**Description**: List all desks

**Access**: Desk Manager or above

**Query Parameters**:
- `page`, `page_size`
- `status` (optional): available | assigned
- `zone` (optional)

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "desk_code": "D-001",
      "desk_label": "Desk 1",
      "status": "available",
      "zone": "Zone A",
      "has_monitor": true,
      "has_docking_station": true,
      "is_active": true
    }
  ]
}
```

---

### `POST /desks`
**Description**: Create a desk

**Access**: Desk Manager only

**Request Body**:
```json
{
  "desk_label": "Desk 25",
  "zone": "Zone B",
  "has_monitor": true,
  "has_docking_station": false,
  "notes": "Near window"
}
```

---

### `GET /desks/rooms`
**Description**: List all conference rooms

**Response**: Similar to desks, includes `capacity` field

---

### `POST /desks/rooms`
**Description**: Create conference room

**Request Body**:
```json
{
  "room_label": "Meeting Room A",
  "capacity": 10,
  "zone": "Zone A",
  "notes": "Projector available"
}
```

---

### `GET /desks/bookings`
**Description**: List desk bookings

**Query Parameters**:
- `page`, `page_size`
- `user_id` (optional)
- `desk_id` (optional)
- `booking_date` (optional)
- `start_date`, `end_date`

---

### `POST /desks/bookings`
**Description**: Book a desk

**Request Body**:
```json
{
  "desk_id": "uuid",
  "booking_date": "2026-02-15",
  "start_time": "09:00:00",
  "end_time": "17:00:00",
  "purpose": "Project work"
}
```

**Validation**:
- Desk must be available
- Cannot overlap with existing bookings
- Cannot book past dates

---

### `GET /desks/bookings/my`
**Description**: Get current user's desk bookings

---

### `DELETE /desks/bookings/{booking_id}`
**Description**: Cancel desk booking

**Access**: Booking owner or Desk Manager

---

### `GET /desks/rooms/bookings`
**Description**: List conference room bookings

---

### `POST /desks/rooms/bookings`
**Description**: Book a conference room

**Request Body**: Same as desk booking with `room_id`

---

## 7. Cafeteria & Food Ordering Endpoints

### `GET /cafeteria/tables`
**Description**: List cafeteria tables

**Access**: Cafeteria Manager or above

---

### `POST /cafeteria/tables`
**Description**: Create cafeteria table

**Access**: Cafeteria Manager only

**Request Body**:
```json
{
  "table_label": "Table 5",
  "capacity": 4,
  "zone": "Zone A",
  "notes": "Window side"
}
```

---

### `GET /cafeteria/bookings`
**Description**: List table bookings

---

### `POST /cafeteria/bookings`
**Description**: Book a cafeteria table

**Request Body**:
```json
{
  "table_id": "uuid",
  "booking_date": "2026-02-15",
  "start_time": "12:00:00",
  "end_time": "13:00:00"
}
```

---

### `GET /food-orders/items`
**Description**: List available food items

**Query Parameters**:
- `page`, `page_size`
- `category` (optional): breakfast | lunch | snacks | beverages
- `is_available` (optional): true/false
- `search` (optional): Text search in name/description

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Chicken Biryani",
      "description": "Aromatic rice with chicken",
      "category": "lunch",
      "price": 120.00,
      "is_vegetarian": false,
      "is_available": true,
      "dietary_info": ["non-veg", "spicy"]
    }
  ]
}
```

---

### `POST /food-orders/items`
**Description**: Create food item

**Access**: Cafeteria Manager only

**Request Body**:
```json
{
  "name": "Paneer Tikka",
  "description": "Grilled cottage cheese",
  "category": "snacks",
  "price": 80.00,
  "is_vegetarian": true,
  "is_available": true,
  "ingredients": ["paneer", "spices", "yogurt"],
  "dietary_info": ["vegetarian"]
}
```

---

### `PUT /food-orders/items/{item_id}`
**Description**: Update food item

**Access**: Cafeteria Manager only

---

### `POST /food-orders/orders`
**Description**: Place a food order

**Request Body**:
```json
{
  "order_items": [
    {
      "item_id": "uuid",
      "quantity": 2,
      "special_instructions": "Less spicy"
    },
    {
      "item_id": "uuid",
      "quantity": 1
    }
  ],
  "delivery_time": "13:00:00",  // Optional
  "notes": "Office cabin 305"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "order_number": "ORD-20260211-001",
    "user_code": "AB1234",
    "status": "pending",  // pending | confirmed | preparing | ready | delivered | cancelled
    "total_amount": 320.00,
    "items": [
      {
        "item_name": "Chicken Biryani",
        "quantity": 2,
        "price": 120.00,
        "subtotal": 240.00
      }
    ],
    "order_date": "2026-02-11",
    "delivery_time": "13:00:00",
    "created_at": "2026-02-11T11:00:00Z"
  },
  "message": "Order placed successfully"
}
```

---

### `GET /food-orders/orders`
**Description**: List food orders

**Query Parameters**:
- `page`, `page_size`
- `user_id` (optional): Cafeteria Manager only
- `status` (optional)
- `order_date` (optional)

---

### `GET /food-orders/orders/my`
**Description**: Get current user's orders

---

### `PUT /food-orders/orders/{order_id}/status`
**Description**: Update order status

**Access**: Cafeteria Manager only

**Request Body**:
```json
{
  "status": "preparing"  // pending | confirmed | preparing | ready | delivered | cancelled
}
```

---

### `DELETE /food-orders/orders/{order_id}`
**Description**: Cancel order

**Access**: Order owner (if pending) or Cafeteria Manager

---

## 8. IT Asset Management Endpoints

### `GET /it-assets`
**Description**: List IT assets

**Access**: IT Manager or above

**Query Parameters**:
- `page`, `page_size`
- `asset_type` (optional): laptop | monitor | keyboard | mouse | headphones
- `status` (optional): available | assigned | under_maintenance | retired
- `assigned_to` (optional): User ID filter

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "asset_code": "LAP-001",
      "asset_name": "Dell Latitude 5520",
      "asset_type": "laptop",
      "status": "assigned",
      "serial_number": "DL12345",
      "purchase_date": "2025-06-15",
      "warranty_until": "2028-06-15",
      "assigned_to": {
        "user_code": "AB1234",
        "name": "John Doe"
      },
      "specifications": {
        "processor": "Intel i7",
        "ram": "16GB",
        "storage": "512GB SSD"
      }
    }
  ]
}
```

---

### `POST /it-assets`
**Description**: Create IT asset

**Access**: IT Manager only

**Request Body**:
```json
{
  "asset_name": "Dell Monitor 27\"",
  "asset_type": "monitor",
  "manufacturer": "Dell",
  "model": "P2722H",
  "serial_number": "MON12345",
  "purchase_date": "2026-01-15",
  "purchase_price": 25000.00,
  "warranty_until": "2029-01-15",
  "specifications": {
    "size": "27 inches",
    "resolution": "1920x1080"
  },
  "notes": "For design team"
}
```

**Note**: `asset_code` is auto-generated (e.g., MON-001)

---

### `PUT /it-assets/{asset_id}`
**Description**: Update IT asset

**Access**: IT Manager only

---

### `DELETE /it-assets/{asset_id}`
**Description**: Delete IT asset

**Access**: IT Manager only

---

### `POST /it-assets/{asset_id}/assign`
**Description**: Assign asset to a user

**Access**: IT Manager only

**Request Body**:
```json
{
  "user_id": "uuid",
  "notes": "Laptop for development work"
}
```

**Response**: Assignment record with assignment date

**Business Logic**:
- Asset status changes to "assigned"
- Creates assignment history record
- Previous assignment (if any) is marked as returned

---

### `POST /it-assets/{asset_id}/unassign`
**Description**: Unassign asset from user

**Access**: IT Manager only

**Response**: Asset status changes to "available"

---

### `GET /it-assets/my`
**Description**: Get assets assigned to current user

**Response**: List of assigned assets

---

### `GET /it-assets/{asset_id}/history`
**Description**: Get assignment history of an asset

**Access**: IT Manager or asset owner

---

## 9. IT Request Endpoints

### `POST /it-requests`
**Description**: Create an IT request

**Request Body**:
```json
{
  "request_type": "hardware",  // hardware | software | access | support
  "item_type": "laptop",  // For hardware: laptop | monitor | keyboard | mouse | headphones
  "title": "Need new laptop",
  "description": "Current laptop is slow, need upgrade for development work",
  "priority": "high",  // low | medium | high | urgent
  "required_by": "2026-02-20"  // Optional
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "request_number": "IT-20260211-001",
    "user_code": "AB1234",
    "request_type": "hardware",
    "item_type": "laptop",
    "title": "Need new laptop",
    "description": "Current laptop is slow...",
    "status": "pending",  // pending | approved | in_progress | completed | rejected | cancelled
    "priority": "high",
    "created_at": "2026-02-11T10:00:00Z"
  },
  "message": "IT request created successfully"
}
```

---

### `GET /it-requests`
**Description**: List IT requests

**Query Parameters**:
- `page`, `page_size`
- `user_id` (optional): IT Manager only
- `status` (optional)
- `request_type` (optional)
- `priority` (optional)

**Access**:
- IT Manager: ALL requests
- Others: Only own requests

---

### `GET /it-requests/my`
**Description**: Get current user's IT requests

---

### `GET /it-requests/pending`
**Description**: Get requests pending approval

**Access**: IT Manager only

---

### `POST /it-requests/{request_id}/approve`
**Description**: Approve or reject IT request

**Access**: IT Manager only

**Request Body**:
```json
{
  "action": "approve",  // "approve" or "reject"
  "notes": "Approved, will assign laptop by Friday",
  "assigned_to_id": "uuid",  // Optional: Assign to specific IT staff
  "rejection_reason": "Not justified"  // Required if action is "reject"
}
```

**Business Logic**:
- Approved requests move to "approved" status
- Can assign to IT staff for fulfillment
- Rejected requests cannot be reopened

---

### `PUT /it-requests/{request_id}/status`
**Description**: Update request status

**Access**: IT Manager only

**Request Body**:
```json
{
  "status": "in_progress",  // approved | in_progress | completed
  "notes": "Working on it"
}
```

---

### `POST /it-requests/{request_id}/complete`
**Description**: Mark request as completed

**Access**: IT Manager only

**Request Body**:
```json
{
  "resolution_notes": "Laptop assigned, asset code: LAP-015",
  "assigned_asset_id": "uuid"  // Optional: Link to assigned asset
}
```

---

### `DELETE /it-requests/{request_id}`
**Description**: Cancel own request

**Access**: Request owner (if pending) or IT Manager

---

## 10. Project Management Endpoints

### `POST /projects`
**Description**: Create a project request

**Access**: TEAM_LEAD only

**Request Body**:
```json
{
  "project_name": "Mobile App Development",
  "description": "Develop iOS and Android apps for customer portal",
  "start_date": "2026-03-01",
  "end_date": "2026-08-31",
  "estimated_budget": 5000000.00,
  "team_size": 8,
  "required_skills": ["React Native", "Node.js", "AWS"],
  "business_justification": "Increase customer engagement by 40%"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "project_code": "PRJ-2026-001",
    "project_name": "Mobile App Development",
    "team_lead_code": "TL0001",
    "status": "pending_approval",  // pending_approval | approved | in_progress | on_hold | completed | cancelled
    "start_date": "2026-03-01",
    "end_date": "2026-08-31",
    "estimated_budget": 5000000.00,
    "created_at": "2026-02-11T10:00:00Z"
  },
  "message": "Project request created successfully"
}
```

---

### `GET /projects`
**Description**: List projects

**Query Parameters**:
- `page`, `page_size`
- `team_lead_id` (optional): Filter by team lead (Admin only)
- `status` (optional)
- `start_date`, `end_date`: Filter by project dates

**Access**:
- ADMIN+: All projects
- TEAM_LEAD: Own projects only

---

### `GET /projects/my`
**Description**: Get current user's projects (for Team Leads)

---

### `GET /projects/pending`
**Description**: Get projects pending approval

**Access**: ADMIN or above

---

### `POST /projects/{project_id}/approve`
**Description**: Approve or reject project request

**Access**: ADMIN or above

**Request Body**:
```json
{
  "action": "approve",  // "approve" or "reject"
  "notes": "Approved with budget cap of 4.5M",
  "approved_budget": 4500000.00,  // Optional: Modify budget
  "rejection_reason": "Insufficient ROI"  // Required if reject
}
```

---

### `PUT /projects/{project_id}/status`
**Description**: Update project status

**Access**: Project's Team Lead or ADMIN

**Request Body**:
```json
{
  "status": "in_progress",  // approved | in_progress | on_hold | completed | cancelled
  "notes": "Kicked off project"
}
```

---

### `PUT /projects/{project_id}`
**Description**: Update project details

**Access**: Project's Team Lead (before approval) or ADMIN

---

### `GET /projects/{project_id}`
**Description**: Get project details

---

## 11. Holiday Management Endpoints

### `GET /holidays`
**Description**: List company holidays

**Query Parameters**:
- `year` (optional): Filter by year
- `is_mandatory` (optional): true/false

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "holiday_name": "Republic Day",
      "holiday_date": "2026-01-26",
      "is_mandatory": true,
      "description": "National holiday",
      "created_at": "2026-01-01T00:00:00Z"
    }
  ]
}
```

---

### `POST /holidays`
**Description**: Create a holiday

**Access**: ADMIN or above

**Request Body**:
```json
{
  "holiday_name": "Diwali",
  "holiday_date": "2026-10-24",
  "is_mandatory": true,
  "description": "Festival of lights"
}
```

---

### `PUT /holidays/{holiday_id}`
**Description**: Update holiday

**Access**: ADMIN or above

---

### `DELETE /holidays/{holiday_id}`
**Description**: Delete holiday

**Access**: ADMIN or above

---

## 12. Semantic Search Endpoints

### `POST /search`
**Description**: AI-powered semantic search for food items and IT assets

**Request Body**:
```json
{
  "query": "spicy vegetarian food",
  "search_type": "food",  // "food" or "it_assets"
  "limit": 10  // Optional, default: 10
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "item": {
          "id": "uuid",
          "name": "Paneer Tikka",
          "description": "Spicy grilled cottage cheese",
          "category": "snacks",
          "price": 80.00,
          "is_vegetarian": true
        },
        "similarity_score": 0.87
      }
    ],
    "query": "spicy vegetarian food",
    "total_results": 5
  }
}
```

**How it works**:
- Uses sentence transformer embeddings (all-MiniLM-L6-v2)
- Searches by semantic meaning, not just keywords
- Returns results ranked by similarity

**Example queries**:
- Food: "healthy breakfast", "non-veg spicy lunch", "quick snacks"
- IT Assets: "high performance laptop", "external monitor", "gaming peripherals"

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api_comprehensive.py -v

# Run specific test function
pytest tests/test_auth.py::test_login -v
```

## Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql+asyncpg://office_admin:office_password@localhost:5432/office_management
DATABASE_URL_SYNC=postgresql://office_admin:office_password@localhost:5432/office_management

# Security
SECRET_KEY=your-super-secret-key-change-in-production-minimum-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
APP_NAME=Unified Office Management System
DEBUG=True
API_V1_PREFIX=/api/v1

# Company
COMPANY_DOMAIN=company.com

# Vector Search (Semantic Search)
EMBEDDING_MODEL=all-MiniLM-L6-v2
VECTOR_DIMENSION=384
```

## Project Structure

```
unified-office-management/
├── app/
│   ├── main.py                    # FastAPI application entry point
│   ├── core/
│   │   ├── config.py              # Settings and environment variables
│   │   ├── database.py            # Database connection and session
│   │   ├── security.py            # JWT and password hashing
│   │   └── dependencies.py        # FastAPI dependencies and auth
│   ├── api/v1/
│   │   ├── router.py              # Main API router
│   │   └── endpoints/             # API endpoint modules
│   │       ├── auth.py            # Authentication endpoints
│   │       ├── users.py           # User management
│   │       ├── attendance.py      # Attendance tracking
│   │       ├── leave.py           # Leave management
│   │       ├── parking.py         # Parking management
│   │       ├── desks.py           # Desk & conference rooms
│   │       ├── cafeteria.py       # Cafeteria table bookings
│   │       ├── food_orders.py     # Food ordering
│   │       ├── it_assets.py       # IT asset management
│   │       ├── it_requests.py     # IT support requests
│   │       ├── projects.py        # Project management
│   │       ├── holidays.py        # Holiday calendar
│   │       └── search.py          # Semantic search
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── attendance.py
│   │   ├── leave.py
│   │   ├── parking.py
│   │   ├── desk.py
│   │   ├── cafeteria.py
│   │   ├── food.py
│   │   ├── it_asset.py
│   │   ├── it_request.py
│   │   ├── project.py
│   │   ├── holiday.py
│   │   ├── enums.py               # Enum definitions
│   │   └── base.py                # Base model classes
│   ├── schemas/                   # Pydantic schemas (request/response)
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── attendance.py
│   │   └── ...
│   ├── services/                  # Business logic layer
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── attendance_service.py
│   │   ├── embedding_service.py   # AI embeddings for search
│   │   └── ...
│   ├── middleware/
│   │   └── response_middleware.py # Request logging and formatting
│   └── utils/                     # Utility functions
│       ├── response.py            # Response formatters
│       └── validators.py          # Custom validators
├── alembic/                       # Database migrations
│   ├── versions/                  # Migration files
│   └── env.py
├── scripts/
│   ├── seed_hierarchy.py          # Seed initial users
│   └── seed_data.py               # Seed sample data
├── tests/                         # Test suite
│   ├── conftest.py                # Pytest fixtures
│   ├── test_auth.py
│   ├── test_api_comprehensive.py
│   └── test_edge_cases.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── alembic.ini
├── pytest.ini
└── README.md
```

## Interactive API Documentation

Once the server is running, access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔄 Complete System Workflows

This section details the complete end-to-end workflows for all major features in the system.

### 1. User Management Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ User Onboarding & Management                                     │
└─────────────────────────────────────────────────────────────────┘

SUPER_ADMIN creates ADMIN
    ↓
ADMIN creates MANAGER (with manager_type)
    ↓
ADMIN creates TEAM_LEAD (with department)
    ↓
MANAGER/ADMIN creates EMPLOYEE (with team_lead_code)

Each user automatically gets:
✓ Unique user_code (auto-generated)
✓ Email (auto-generated if not provided: firstname.lastname@company.com)
✓ Hierarchical relationship (team_lead_code, manager_code, admin_code)
✓ Login credentials
```

**Workflow Steps:**

1. **Create User** → `POST /api/v1/users`
   - ADMIN provides: name, role, department (for team lead), manager_type (for manager)
   - System auto-generates: user_code, email, hierarchical codes

2. **User Login** → `POST /api/v1/auth/login`
   - User provides: email, password
   - System returns: JWT access token + refresh token

3. **Update Profile** → `PUT /api/v1/users/{user_id}`
   - Users can update: name, phone, vehicle details
   - ADMIN can update: role, department, hierarchy

4. **Deactivate User** → `POST /api/v1/users/{user_id}/toggle-active`
   - ADMIN deactivates user (prevents login)
   - User data retained for reporting

---

### 2. Attendance Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ Daily Attendance Tracking                                        │
└─────────────────────────────────────────────────────────────────┘

EMPLOYEE arrives at office
    ↓
Check-in (POST /attendance/check-in)
    ↓ [System creates attendance record with status: draft]
    ↓
Work during the day (Multiple check-ins/check-outs allowed)
    ↓
Check-out (POST /attendance/check-out)
    ↓ [System calculates duration, updates total hours]
    ↓
End of day: Submit for approval (POST /attendance/{id}/submit)
    ↓ [Status: draft → pending_approval]
    ↓
TEAM_LEAD reviews (GET /attendance/pending-approvals)
    ↓
TEAM_LEAD approves (POST /attendance/{id}/approve)
    ↓ [Status: pending_approval → approved]
    ↓
Attendance record finalized ✓
```

**Key Features:**
- **Multiple Check-ins**: Employees can check-in/out multiple times per day (lunch breaks, meetings outside office)
- **Auto Calculation**: Total hours automatically calculated
- **Flexible Submission**: Can submit at end of day or later
- **Hierarchical Approval**: Team Lead → Manager → Admin (based on who's attendance it is)
- **Attendance Manager**: Can view and approve ALL company attendance

**Special Cases:**
- **Team Lead Attendance**: Requires Manager approval
- **Manager Attendance**: Requires Admin approval
- **Forgot to Check-out**: TEAM_LEAD can manually add check-out time
- **Attendance Override**: Attendance Manager can override any attendance

---

### 3. Leave Management Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ Leave Request & Approval Process                                 │
└─────────────────────────────────────────────────────────────────┘

EMPLOYEE creates leave request
    ↓ [POST /leave/requests]
    ↓ System checks: leave balance, overlap, past dates
    ↓ Status: pending_level1
    ↓
TEAM_LEAD reviews pending requests
    ↓ [GET /leave/requests/pending-level1]
    ↓
TEAM_LEAD approves Level 1
    ↓ [POST /leave/requests/{id}/approve-level1]
    ↓ Status: approved_level1
    ↓
If multi-day leave OR team lead's leave:
    ↓
    MANAGER reviews
    ↓ [GET /leave/requests/pending-final]
    ↓
    MANAGER final approval
    ↓ [POST /leave/requests/{id}/approve-final]
    ↓ Status: approved_final
    ↓ Leave balance deducted
    ↓
Leave approved and recorded ✓
```

**Leave Types & Balances:**
- **Casual Leave**: 10 days/year
- **Sick Leave**: 12 days/year
- **Privilege Leave**: 15 days/year
- **Unpaid Leave**: Unlimited (no balance deduction)

**Business Rules:**
- Cannot request leave for past dates
- Cannot overlap with existing approved leave
- Half-day leave counts as 0.5 days
- Two-level approval for multi-day leave
- Single-level approval for single-day casual leave (Team Lead only)

**Rejection Flow:**
```
At any approval level:
    Approver rejects → Status: rejected
    Employee can create new request (original cannot be modified)
```

**Cancellation Flow:**
```
EMPLOYEE cancels own leave (if pending)
    ↓ [POST /leave/requests/{id}/cancel]
    ↓ Status: cancelled
    ↓ Balance restored (if already deducted)
```

---

### 4. Parking Management Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ Parking Slot Allocation                                          │
└─────────────────────────────────────────────────────────────────┘

Setup (One-time by Parking Manager):
    Parking Manager creates slots
    ↓ [POST /parking/slots/create?slot_code=A-01]
    ↓ Slots status: AVAILABLE

Daily Usage (All Employees):
    EMPLOYEE arrives with vehicle
    ↓ [POST /parking/allocate] - No input needed!
    ↓ System finds first available slot
    ↓ Assigns to employee using profile vehicle info
    ↓ Slot status: OCCUPIED
    ↓ Creates parking log with entry time
    ↓
    EMPLOYEE leaves office
    ↓ [POST /parking/release] - No input needed!
    ↓ System finds employee's active parking
    ↓ Records exit time, calculates duration
    ↓ Slot status: AVAILABLE
    ↓ Parking log completed ✓

Visitor Parking (Parking Manager):
    Guest arrives
    ↓ [POST /parking/slots/assign-visitor]
    ↓ Parking Manager assigns slot to visitor
    ↓ Records visitor name, vehicle number
    ↓
    Guest leaves
    ↓ [POST /parking/slots/change-status/{slot_code}?new_status=AVAILABLE]
    ↓ Slot freed for next user
```

**Management Operations:**
- **View Summary**: `GET /parking/slots/summary` - Total, available, occupied counts
- **List All Slots**: `GET /parking/slots/list` - All slots with occupant details
- **View Logs**: `GET /parking/logs/list` - Complete parking history
- **Disable Slot**: `POST /parking/slots/change-status` - Mark for maintenance

**Error Handling:**
- No vehicle in profile → Cannot allocate parking
- Already has active parking → Must release first
- No available slots → Shows error, try later

---

### 5. Desk & Conference Room Booking Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ Desk Booking (Date-Range Based)                                 │
└─────────────────────────────────────────────────────────────────┘

Setup:
    Desk Manager creates desks/rooms
    ↓ [POST /desks or POST /desks/rooms]
    ↓ Desk/Room available for booking

Employee Booking:
    EMPLOYEE needs workspace for project
    ↓ Views available desks [GET /desks]
    ↓ Creates booking [POST /desks/bookings]
    ↓ Provides: desk_id, start_date, end_date, purpose
    ↓ System validates: no overlap, desk available
    ↓ Booking confirmed immediately (status: CONFIRMED)
    ↓ Can work at desk during booked dates ✓

Cancellation:
    EMPLOYEE cancels booking
    ↓ [DELETE /desks/bookings/{booking_id}]
    ↓ Only future bookings can be cancelled
    ↓ Desk becomes available immediately
```

```
┌─────────────────────────────────────────────────────────────────┐
│ Conference Room Booking (Approval Required)                     │
└─────────────────────────────────────────────────────────────────┘

EMPLOYEE needs meeting room
    ↓ Views available rooms [GET /desks/rooms]
    ↓ Creates booking [POST /desks/rooms/bookings]
    ↓ Provides: room_id, start_date, end_date, purpose
    ↓ Status: PENDING (awaiting approval)
    ↓
Desk Manager reviews pending requests
    ↓ [GET /desks/rooms/bookings/pending]
    ↓
Desk Manager approves or rejects
    ↓ [POST /desks/rooms/bookings/{id}/approve]
    ↓ [POST /desks/rooms/bookings/{id}/reject]
    ↓
If approved: Status → CONFIRMED
    Employee can use room ✓
If rejected: Status → REJECTED
    Employee notified with reason
```

**Business Rules:**
- Desk bookings: Immediately confirmed (no approval needed)
- Conference room bookings: Require Desk Manager approval
- Cannot book past dates
- Cannot overlap with existing confirmed bookings
- Can view own bookings: `GET /desks/bookings/my`

---

### 6. Cafeteria & Food Ordering Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ Food Ordering System (Cart-Based)                               │
└─────────────────────────────────────────────────────────────────┘

Setup:
    Cafeteria Manager creates menu items
    ↓ [POST /food-orders/items]
    ↓ Items available for ordering

Employee Orders Food:
    EMPLOYEE browses menu
    ↓ [GET /food-orders/items] - Can filter by category, search
    ↓ Selects multiple items (builds cart in frontend)
    ↓
    Places order with multiple items
    ↓ [POST /food-orders/orders]
    ↓ Request body:
    {
      "order_items": [
        {"item_id": "...", "quantity": 2, "special_instructions": "Less spicy"},
        {"item_id": "...", "quantity": 1}
      ],
      "delivery_time": "13:00:00",
      "notes": "Cabin 305"
    }
    ↓ System calculates total amount
    ↓ Order created with status: PENDING
    ↓ Order number auto-generated: ORD-20260211-001
    ↓
Cafeteria staff processes:
    ↓ [PUT /food-orders/orders/{id}/status]
    ↓ Status progression:
    PENDING → CONFIRMED → PREPARING → READY → DELIVERED
    ↓
Order completed ✓
```

**Order Management:**
- **View Menu**: All users see all food items
- **Own Orders Only**: Users see only their orders (RBAC enforced)
- **Cancel Order**: Only if status is PENDING
- **Manager View**: Cafeteria Manager sees ALL orders

**Table Booking (Optional):**
```
EMPLOYEE wants to reserve table
    ↓ [GET /cafeteria/tables] - View available tables
    ↓ [POST /cafeteria/bookings]
    ↓ Provides: table_id, booking_date, start_time, end_time
    ↓ Table reserved ✓
```

---

### 7. IT Asset Management Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ IT Asset Lifecycle                                               │
└─────────────────────────────────────────────────────────────────┘

Asset Procurement:
    IT Manager adds new asset to inventory
    ↓ [POST /it-assets]
    ↓ Provides: name, type, serial number, purchase details
    ↓ System auto-generates asset_code (e.g., LAP-001)
    ↓ Status: AVAILABLE
    ↓
Asset Assignment:
    Employee needs laptop
    ↓ IT Manager assigns asset
    ↓ [POST /it-assets/{asset_id}/assign]
    ↓ Provides: user_id, assignment notes
    ↓ Status: ASSIGNED
    ↓ Assignment history created
    ↓ Employee receives asset ✓
    ↓
Employee views assigned assets:
    ↓ [GET /it-assets/my]
    ↓ Sees all currently assigned equipment
    ↓
Asset Return:
    Employee returns asset (leaving company, upgrade, etc.)
    ↓ IT Manager unassigns
    ↓ [POST /it-assets/{asset_id}/unassign]
    ↓ Status: AVAILABLE
    ↓ Asset ready for reassignment
    ↓
Asset Maintenance:
    Asset needs repair
    ↓ IT Manager updates status
    ↓ [PUT /it-assets/{asset_id}]
    ↓ Status: UNDER_MAINTENANCE
    ↓ After repair: Status → AVAILABLE
    ↓
Asset Retirement:
    Asset too old/damaged
    ↓ IT Manager retires asset
    ↓ Status: RETIRED
    ↓ Kept in system for historical records
```

**Asset Types:**
- Laptop, Monitor, Keyboard, Mouse, Headphones, Docking Station, etc.

**Tracking Features:**
- **Assignment History**: `GET /it-assets/{asset_id}/history`
- **Warranty Tracking**: warranty_until field
- **Specifications**: JSON field for detailed specs
- **Search**: Semantic search by description

---

### 8. IT Request Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ IT Support Request Lifecycle                                     │
└─────────────────────────────────────────────────────────────────┘

EMPLOYEE has IT issue/need
    ↓ Creates IT request
    ↓ [POST /it-requests]
    ↓ Provides: request_type, title, description, priority
    ↓ Request types: NEW, NEW_ASSET, REPAIR, REPLACEMENT,
    │                 SOFTWARE_INSTALL, ACCESS_REQUEST,
    │                 NETWORK_ISSUE, OTHER
    ↓ System auto-generates request_number: REQ-20260211-001
    ↓ Status: PENDING
    ↓
IT Manager reviews requests
    ↓ [GET /it-requests] - Sees all pending requests
    ↓ Views request details
    ↓
IT Manager approves or rejects
    ↓ [POST /it-requests/{id}/approve]
    ↓ Request body:
    {
      "action": "approve",  // or "reject"
      "notes": "Will provide laptop by Friday",
      "assigned_to_code": "IT5001",  // Optional: assign to IT staff
      "rejection_reason": "Not justified"  // If rejecting
    }
    ↓
If approved:
    ↓ Status: APPROVED
    ↓ IT staff (assigned_to) fulfills request
    ↓ For NEW_ASSET: Creates asset and assigns to requester
    ↓ For REPAIR: Updates asset status to UNDER_MAINTENANCE
    ↓ Request marked complete
    ↓
If rejected:
    ↓ Status: REJECTED
    ↓ Employee notified with rejection reason
    ↓ Can create new request with more details
```

**IT Request Types:**
1. **NEW**: General IT request
2. **NEW_ASSET**: Need new equipment (laptop, monitor, etc.)
3. **REPAIR**: Fix existing asset
4. **REPLACEMENT**: Replace broken/old asset
5. **SOFTWARE_INSTALL**: Install software on machine
6. **ACCESS_REQUEST**: Network/system access
7. **NETWORK_ISSUE**: Network connectivity problems
8. **OTHER**: Other IT support needs

**Simplified Workflow (Approval Only):**
- No separate "start" or "complete" endpoints
- IT Manager approves → Request fulfilled
- Status: PENDING → APPROVED/REJECTED (final states)

---

### 9. Project Management Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ Project Request & Approval                                       │
└─────────────────────────────────────────────────────────────────┘

TEAM_LEAD has project idea
    ↓ Creates project request
    ↓ [POST /projects]
    ↓ Provides: project_name, description, dates,
    │           budget, team_size, required_skills,
    │           business_justification
    ↓ System auto-generates project_code: PRJ-2026-001
    ↓ Status: PENDING_APPROVAL
    ↓
ADMIN reviews pending projects
    ↓ [GET /projects/pending]
    ↓ Evaluates business case, budget, ROI
    ↓
ADMIN approves or rejects
    ↓ [POST /projects/{id}/approve]
    ↓ Request body:
    {
      "action": "approve",  // or "reject"
      "notes": "Approved with conditions",
      "approved_budget": 4500000.00,  // Can modify budget
      "rejection_reason": "Insufficient ROI"
    }
    ↓
If approved:
    ↓ Status: APPROVED
    ↓ TEAM_LEAD starts project
    ↓ [PUT /projects/{id}/status] → IN_PROGRESS
    ↓ Team works on project
    ↓ Progress updates via status changes
    ↓ Final status: COMPLETED
    ↓
If rejected:
    ↓ Status: REJECTED
    ↓ Team Lead notified with reason
    ↓ Can submit revised proposal
```

**Project Status Lifecycle:**
```
PENDING_APPROVAL → APPROVED → IN_PROGRESS → COMPLETED
                 ↓           ↓
              REJECTED    ON_HOLD → IN_PROGRESS
                          CANCELLED
```

**Business Rules:**
- Only TEAM_LEAD can create projects
- Only ADMIN can approve projects
- Budget can be modified during approval
- Projects can be put on hold and resumed
- Status updates restricted to project owner or ADMIN

---

### 10. Holiday Management Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ Company Holiday Calendar                                         │
└─────────────────────────────────────────────────────────────────┘

ADMIN manages holidays:
    ↓ Creates holiday [POST /holidays]
    ↓ Provides: holiday_name, holiday_date,
    │           is_mandatory, description
    ↓ Holiday added to calendar
    ↓
All employees view holidays:
    ↓ [GET /holidays]
    ↓ Can filter by year
    ↓ See mandatory vs optional holidays
    ↓
Leave system integration:
    ↓ Leave requests automatically skip holidays
    ↓ Holiday dates don't count toward leave days
    ↓
ADMIN can update/delete:
    ↓ [PUT /holidays/{id}] - Modify holiday
    ↓ [DELETE /holidays/{id}] - Remove holiday
```

---

### 11. Semantic Search Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ AI-Powered Search                                                │
└─────────────────────────────────────────────────────────────────┘

Setup (Automatic):
    System generates embeddings for:
    ✓ Food items (name + description + category)
    ✓ IT assets (name + description + specifications)
    ↓ Uses: sentence-transformers/all-MiniLM-L6-v2
    ↓ Stores: 384-dimensional vectors in pgvector
    ↓
User performs search:
    ↓ [POST /search]
    ↓ Request body:
    {
      "query": "spicy vegetarian lunch",
      "search_type": "food",
      "limit": 10
    }
    ↓ System converts query to embedding
    ↓ Performs cosine similarity search
    ↓ Returns ranked results with similarity scores
    ↓
Results:
    [
      {"item": {...}, "similarity_score": 0.87},
      {"item": {...}, "similarity_score": 0.82},
      ...
    ]
```

**Search Examples:**
- **Food**: "healthy breakfast", "non-veg spicy", "quick snacks", "beverages"
- **IT Assets**: "high performance laptop", "4K monitor", "wireless peripherals"

**Advantages:**
- Understands semantic meaning (not just keywords)
- Finds similar items even with different wording
- Ranks results by relevance

---

## 🧪 Testing Guide

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Start PostgreSQL database (required for tests)
docker compose up -d db

# Run all tests
pytest test_all.py -v

# Run with coverage report
pytest test_all.py --cov=app --cov-report=html

# Run specific test
pytest test_all.py::test_complete_attendance_workflow -v
```

### Test Database Setup

Tests require a PostgreSQL database. Set the connection string:

```bash
export TEST_DATABASE_URL="postgresql+asyncpg://office_admin:office_password@localhost:5432/office_management_test"
```

Or use the default database (ensure it's running):

```bash
docker compose up -d db
```

### Test Coverage

The `test_all.py` file provides comprehensive testing for:
- ✅ All authentication flows
- ✅ User management and hierarchy
- ✅ Attendance workflows (check-in/out, approval)
- ✅ Leave management (creation, approval, cancellation)
- ✅ Parking operations (allocate, release)
- ✅ Desk and conference room booking
- ✅ Food ordering (multi-item cart)
- ✅ IT asset lifecycle
- ✅ IT request approval workflow
- ✅ Project management
- ✅ Holiday management
- ✅ RBAC enforcement
- ✅ Error handling and edge cases

**For detailed testing instructions, see [TEST_README.md](TEST_README.md)**

---

## License

MIT License

## Support

For issues and questions, please create an issue in the repository.