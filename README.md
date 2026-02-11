# 🏢 Unified Office Management System

A **comprehensive, production-ready backend API** for managing all office operations including parking, desk booking, cafeteria, attendance, leave management, IT assets, and project management. Built with **FastAPI**, **PostgreSQL**, and **AI-powered semantic search**.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [User Roles & Hierarchy](#user-roles--hierarchy)
- [API Endpoints Documentation](#api-endpoints-documentation)
- [Complete Workflows](#-complete-system-workflows)
- [Database Schema](#database-schema)
- [Development Guide](#development-guide)
- [Testing](#testing)
- [Deployment](#deployment)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The **Unified Office Management System** is a modern, scalable backend solution designed to digitize and streamline all office operations. It provides a RESTful API with role-based access control, hierarchical approval workflows, and AI-powered features.

### Key Highlights

- ✅ **12+ Modules**: Authentication, Users, Attendance, Leave, Parking, Desks, Cafeteria, Food Orders, IT Assets, IT Requests, Projects, Holidays, Semantic Search
- ✅ **5-Tier Hierarchy**: Super Admin → Admin → Manager → Team Lead → Employee
- ✅ **JWT Authentication**: Secure token-based auth with refresh tokens
- ✅ **Role-Based Access Control**: Fine-grained permissions for all operations
- ✅ **Async Architecture**: Built with FastAPI for high performance
- ✅ **PostgreSQL + pgvector**: Robust database with vector search support
- ✅ **AI-Powered Search**: Semantic search using sentence transformers
- ✅ **Production-Ready**: Docker support, migrations, comprehensive testing
- ✅ **Auto-Generated Codes**: User codes, asset codes, request numbers
- ✅ **Approval Workflows**: Multi-level approvals for attendance, leave, projects
- ✅ **Real-time Operations**: Check-in/out, parking allocation, food ordering

---

---

## ✨ Features

### 🔐 Authentication & Authorization
- **JWT-based authentication** with access and refresh tokens
- **OAuth2 password flow** for secure login
- **Role-based access control (RBAC)** at endpoint level
- **Password change** functionality for users and admins
- **Token expiration** handling (24hr access, 7-day refresh)
- **Hierarchical permissions** based on organizational structure

### 👥 User Management
- **5-tier hierarchical structure**: Super Admin → Admin → Manager → Team Lead → Employee
- **Auto-generated user codes**: 6-character unique identifiers (e.g., AB1234)
- **Auto-generated emails**: firstname.lastname@company.com
- **Manager types**: Parking, Attendance, Desk/Conference, Cafeteria, IT Support
- **Department-wise Team Leads**: Engineering, Sales, AI, HR, etc.
- **User lifecycle management**: Create, update, deactivate, delete
- **Vehicle information**: Support for employee vehicles (car/bike)
- **Bulk operations**: Toggle active status, change roles, reset passwords

### 📊 Attendance Tracking
- **Simple check-in/check-out**: One-click operations, no manual data entry
- **Multiple entries per day**: Support for lunch breaks, outside meetings
- **Auto-calculation**: Total work hours computed automatically
- **Draft mode**: Employees can edit before submission
- **Hierarchical approval**: Team Lead → Manager → Admin chain
- **Attendance Manager**: Special role to view/approve ALL attendance
- **Date-based tracking**: Daily attendance records with timestamps
- **History & Reports**: View historical attendance data

### 🏖️ Leave Management
- **Four leave types**: Casual (10 days), Sick (12 days), Privilege (15 days), Unpaid
- **Leave balance tracking**: Auto-deduction on approval
- **Two-level approval**: Level 1 (Team Lead) + Level 2 (Manager)
- **Half-day support**: First half or second half options
- **Date range validation**: Prevent overlaps and past-date requests
- **Leave cancellation**: Cancel pending requests
- **Pending approvals dashboard**: For Team Leads and Managers

### 🅿️ Parking Management
- **Simplified allocation**: One-click allocate/release, no forms
- **Auto-assignment**: First available slot assigned automatically
- **Slot management**: Create, delete, enable/disable slots
- **Entry/exit logging**: Track parking duration
- **Visitor parking**: Manual assignment by Parking Manager
- **Real-time status**: View current parking status
- **Parking history**: Complete logs with duration tracking
- **Slot statistics**: Total, available, occupied counts

### 🪑 Desk & Conference Room Booking
- **Date-range bookings**: Book desks for multiple days
- **Instant confirmation**: Desk bookings auto-confirmed
- **Conference room approval**: Manager approval required
- **Overlap prevention**: Cannot double-book resources
- **Equipment tracking**: Monitor, docking station availability
- **Zone-based organization**: Group desks by zones
- **Booking cancellation**: Cancel future bookings
- **My bookings view**: See personal reservations

### 🍽️ Cafeteria & Food Ordering
- **Multi-item cart**: Order multiple food items in one go
- **Category-based menu**: Breakfast, Lunch, Snacks, Beverages
- **Dietary information**: Vegetarian, non-veg, dietary restrictions
- **Order tracking**: Status progression (Pending → Confirmed → Preparing → Ready → Delivered)
- **Auto-generated order numbers**: ORD-YYYYMMDD-NNN format
- **Special instructions**: Custom notes per item
- **Price calculation**: Auto-compute total amount
- **Table booking**: Reserve cafeteria tables for meetings
- **Order history**: View past orders

### 💻 IT Asset Management
- **Asset lifecycle tracking**: From procurement to retirement
- **Auto-generated asset codes**: LAP-001, MON-002, etc.
- **Multiple asset types**: Laptop, Monitor, Keyboard, Mouse, Headphones, etc.
- **Assignment tracking**: Who has what equipment
- **Assignment history**: Complete audit trail
- **Status management**: Available, Assigned, Under Maintenance, Retired
- **Specifications storage**: JSON field for detailed specs
- **Warranty tracking**: Purchase date and warranty expiry
- **Semantic search**: AI-powered asset discovery

### 🛠️ IT Request Management  
- **Request types**: New Asset, Repair, Replacement, Software Install, Access Request, Network Issue
- **Priority levels**: Low, Medium, High, Urgent
- **Auto-generated request numbers**: REQ-YYYYMMDD-NNN
- **Approval workflow**: IT Manager approval required
- **Assignment**: Assign requests to IT staff
- **Status tracking**: Pending → Approved/Rejected
- **Rejection reasons**: Provide feedback to requesters
- **My requests view**: Users see their own requests

### 📁 Project Management
- **Team Lead project proposals**: Submit project ideas with business case
- **Admin approval**: Budget and resource approval
- **Budget tracking**: Estimated vs approved budget
- **Auto-generated project codes**: PRJ-YYYY-NNN
- **Status lifecycle**: Pending → Approved → In Progress → Completed
- **Team size planning**: Specify required team members
- **Skills tracking**: Required skills for project
- **Business justification**: Capture ROI and business case
- **Project updates**: Change status, add notes

### 📅 Holiday Management
- **Company-wide holidays**: Centralized holiday calendar
- **Mandatory vs optional**: Flag critical holidays
- **Year-based filtering**: View holidays by year
- **Leave integration**: Holidays don't count in leave days
- **CRUD operations**: Admin can create, update, delete holidays
- **Description field**: Add context for each holiday

### 🔍 Semantic Search
- **AI-powered**: Uses sentence-transformers (all-MiniLM-L6-v2)
- **Two search domains**: Food items and IT assets
- **Vector embeddings**: 384-dimensional vectors stored in pgvector
- **Semantic understanding**: Finds results by meaning, not just keywords
- **Ranked results**: Ordered by similarity score (0-1)
- **Example queries**: 
  - Food: "spicy vegetarian lunch", "healthy breakfast"
  - IT: "high performance laptop", "4K monitor"

---

---

## 🛠️ Tech Stack

### Backend Framework
- **FastAPI 0.109.0**: Modern, high-performance Python web framework
- **Uvicorn**: ASGI server with WebSocket support
- **Python 3.11+**: Latest Python features and performance improvements

### Database
- **PostgreSQL 15+**: Robust relational database
- **pgvector**: PostgreSQL extension for vector similarity search
- **SQLAlchemy 2.0**: Async ORM with declarative mapping
- **Asyncpg**: High-performance PostgreSQL driver for async operations
- **Alembic**: Database migration tool for schema versioning

### Authentication & Security
- **Python-JOSE**: JWT token creation and validation
- **Passlib + Bcrypt**: Secure password hashing (cost factor: 12)
- **OAuth2 Password Flow**: Industry-standard authentication
- **CORS Middleware**: Cross-origin resource sharing support

### AI/ML
- **Sentence Transformers 2.2.2**: Pre-trained embedding models
- **PyTorch 2.1.2**: Deep learning framework
- **NumPy 1.26.3**: Numerical computations
- **Model**: all-MiniLM-L6-v2 (384-dim embeddings)

### Validation & Serialization
- **Pydantic 2.5.3**: Data validation using Python type annotations
- **Pydantic Settings**: Environment variable management
- **Email Validation**: Built-in email validation

### Testing
- **Pytest 7.4.4**: Testing framework
- **Pytest-Asyncio 0.23.3**: Async test support
- **Pytest-Cov 4.1.0**: Code coverage reports
- **HTTPX 0.26.0**: Async HTTP client for API testing

### DevOps & Deployment
- **Docker**: Containerization for consistent environments
- **Docker Compose**: Multi-container orchestration
- **Git**: Version control

### Additional Libraries
- **Python-Multipart**: File upload support
- **Aiofiles**: Async file operations
- **Python-Dotenv**: .env file support

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                             │
│  (Web App, Mobile App, Third-party Integrations)                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS/REST API
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                           │
│  FastAPI Application (app/main.py)                               │
│  - CORS Middleware                                               │
│  - Response Middleware (logging, formatting)                     │
│  - Exception Handlers (validation, HTTP, generic)                │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Routing Layer                              │
│  API Router (app/api/v1/router.py)                               │
│  - /auth, /users, /attendance, /leave                            │
│  - /parking, /desks, /cafeteria, /food-orders                    │
│  - /it-assets, /it-requests, /projects, /holidays, /search       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Endpoint Layer                               │
│  Controllers (app/api/v1/endpoints/)                             │
│  - Request validation (Pydantic schemas)                         │
│  - Authentication/Authorization (JWT dependencies)               │
│  - Call service layer methods                                    │
│  - Format standardized responses                                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Service Layer                                │
│  Business Logic (app/services/)                                  │
│  - attendance_service, leave_service, parking_service            │
│  - user_service, auth_service, desk_service                      │
│  - food_service, it_asset_service, it_request_service            │
│  - project_service, search_service, embedding_service            │
│  - Implements business rules and workflows                       │
│  - Validates complex business constraints                        │
│  - Manages transactions                                          │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Data Access Layer                              │
│  ORM Models (app/models/)                                        │
│  - User, Attendance, AttendanceEntry, Leave                      │
│  - ParkingSlot, ParkingAllocation, Desk, DeskBooking             │
│  - CafeteriaTable, FoodItem, FoodOrder, ITAsset                  │
│  - ITRequest, Project, Holiday                                   │
│  - SQLAlchemy async sessions with connection pooling             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Database Layer                               │
│  PostgreSQL 15 + pgvector Extension                              │
│  - Relational tables with proper constraints                     │
│  - Vector columns (food_items.embedding, it_assets.embedding)    │
│  - Indexes (B-tree for queries, IVFFlat for vector similarity)   │
│  - Foreign key constraints for referential integrity             │
└─────────────────────────────────────────────────────────────────┘
```

### Async-First Design
The entire backend is built with async/await patterns for optimal performance:
- **Async SQLAlchemy**: Uses `AsyncSession` with `asyncpg` driver for non-blocking database operations
- **Async Endpoints**: All FastAPI endpoints are async functions
- **Connection Pooling**: Efficient database connection management
- **Non-Blocking I/O**: All database queries and external calls are non-blocking

### Service Layer Pattern
Business logic is separated into service classes:
```
Endpoint (API) → Service (Business Logic) → Model (Database)
```

Each service handles:
- Data validation and transformation
- Relationship loading (using `selectinload` for eager loading)
- Business rule enforcement (approval hierarchies, date validations, etc.)
- Error handling with descriptive messages
- Complex query logic

### Request Flow Example (Attendance Check-in)

```
1. Client: POST /api/v1/attendance/check-in
   Headers: Authorization: Bearer <token>
   ↓
2. Endpoint Layer (attendance.py)
   - JWT middleware validates token
   - Extracts current_user from dependency
   - No request body needed (simplified UX)
   ↓
3. Service Layer (attendance_service.check_in)
   - Check if user already has open check-in today
   - If no attendance record for today, create new Attendance
   - Create AttendanceEntry with check_in timestamp
   - Set entry_type to "regular"
   ↓
4. Data Layer (models/attendance.py)
   - INSERT INTO attendance (user_id, date, status, ...)
   - INSERT INTO attendance_entry (attendance_id, check_in, ...)
   - COMMIT transaction
   ↓
5. Response Formatting
   - Standard JSON response with success, data, message, timestamp
   - Return complete attendance with entries
   ↓
6. Client receives:
   {
     "success": true,
     "data": {...attendance with entries...},
     "message": "Check-in recorded successfully",
     "timestamp": "2026-02-11T09:00:00Z"
   }
```

### Database Design Principles

- **Normalization**: 3NF for most tables to eliminate redundancy
- **Foreign Keys**: Enforce referential integrity between related tables
- **Indexes**: Strategic indexes on frequently queried columns
  - `user_code`, `email` (UNIQUE)
  - `date`, `status`, `booking_date` for filtering
  - Foreign key columns for JOIN optimization
- **Enums**: PostgreSQL enums for type-safe status fields
- **Soft Deletes**: `is_deleted` flag instead of hard deletes for audit trails
- **Timestamps**: `created_at`, `updated_at` on all tables
- **UUIDs**: UUID primary keys for distributed system readiness
- **Vector Columns**: pgvector type for semantic search embeddings
- **Composite Keys**: Where appropriate (e.g., user_code + date for attendance)

---

## 🗄️ Database Schema

### Core Tables Overview

| Table | Purpose | Key Columns | Relationships |
|-------|---------|-------------|---------------|
| **users** | User accounts & hierarchy | user_code, email, role, manager_type | → attendance, leave, parking, etc. |
| **attendance** | Daily attendance records | user_id, date, status | → attendance_entries, ← users |
| **attendance_entries** | Check-in/out entries | attendance_id, check_in, check_out | ← attendance |
| **leave_requests** | Leave applications | user_id, leave_type, dates, status | ← users |
| **parking_slots** | Parking slot inventory | slot_code, status | → parking_allocations |
| **parking_allocations** | Active/historical parking | user_id, slot_id, entry/exit_time | ← users, ← parking_slots |
| **desks** | Desk/room inventory | desk_code, type, status | → desk_bookings |
| **desk_bookings** | Desk/room reservations | user_id, desk_id, dates | ← users, ← desks |
| **cafeteria_tables** | Table inventory | table_code, capacity | → cafeteria_bookings |
| **cafeteria_bookings** | Table reservations | user_id, table_id, time | ← users, ← cafeteria_tables |
| **food_items** | Menu items | name, category, price, embedding | → order_items |
| **food_orders** | Food orders | user_id, order_number, status | ← users, → order_items |
| **order_items** | Order line items | order_id, item_id, quantity | ← food_orders, ← food_items |
| **it_assets** | IT equipment | asset_code, type, status, embedding | → assignments, → it_requests |
| **asset_assignments** | Asset assignment history | asset_id, user_id, dates | ← it_assets, ← users |
| **it_requests** | IT support requests | request_number, user_id, type, status | ← users |
| **projects** | Project proposals | project_code, team_lead_id, budget | ← users |
| **holidays** | Company holidays | holiday_name, holiday_date | (standalone) |

### Users Table (Core Entity)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_code VARCHAR(6) UNIQUE NOT NULL,  -- Auto-generated (AB1234)
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role user_role NOT NULL,  -- enum: super_admin, admin, manager, team_lead, employee
    manager_type manager_type,  -- enum: parking, attendance, desk_conference, cafeteria, it_support
    department VARCHAR(100),  -- For team leads
    phone VARCHAR(20),
    
    -- Hierarchical relationships
    team_lead_code VARCHAR(6),  -- FK to users.user_code (team lead)
    manager_code VARCHAR(6),    -- FK to users.user_code (manager)
    admin_code VARCHAR(6),      -- FK to users.user_code (admin)
    approver_code VARCHAR(6),   -- FK to users.user_code (for attendance/leave)
    
    -- Vehicle info (for parking)
    vehicle_number VARCHAR(20),
    vehicle_type vehicle_type,  -- enum: car, bike, two_wheeler
    
    -- Status flags
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    
    -- Audit timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CHECK (manager_type IS NOT NULL OR role != 'manager'),
    CHECK (department IS NOT NULL OR role != 'team_lead')
);

-- Indexes
CREATE UNIQUE INDEX idx_users_user_code ON users(user_code);
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_team_lead_code ON users(team_lead_code);
```

### Attendance Tables

```sql
-- Main attendance record (one per user per day)
CREATE TABLE attendance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    date DATE NOT NULL,
    status attendance_status NOT NULL DEFAULT 'draft',  -- enum: draft, pending_approval, approved, rejected
    
    -- Calculated fields (auto-updated from entries)
    first_check_in TIME,
    last_check_out TIME,
    total_hours DECIMAL(5,2),  -- Total work hours for the day
    
    -- Approval workflow
    submitted_at TIMESTAMP,
    approver_code VARCHAR(6),  -- Who needs to approve
    approved_at TIMESTAMP,
    approved_by_code VARCHAR(6),
    rejection_reason TEXT,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(user_id, date)  -- One attendance record per user per day
);

-- Individual check-in/check-out entries (multiple per day)
CREATE TABLE attendance_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attendance_id UUID NOT NULL REFERENCES attendance(id) ON DELETE CASCADE,
    check_in TIMESTAMP NOT NULL,
    check_out TIMESTAMP,
    entry_type entry_type DEFAULT 'regular',  -- enum: regular, overtime, break
    duration_hours DECIMAL(5,2),  -- Calculated: check_out - check_in
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_attendance_user_date ON attendance(user_id, date);
CREATE INDEX idx_attendance_status ON attendance(status);
CREATE INDEX idx_attendance_entries_attendance_id ON attendance_entries(attendance_id);
```

### Leave Tables

```sql
CREATE TABLE leave_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    leave_type leave_type NOT NULL,  -- enum: casual, sick, privilege, unpaid
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_days DECIMAL(3,1) NOT NULL,  -- Can be 0.5 for half-day
    
    -- Half-day support
    is_half_day BOOLEAN DEFAULT FALSE,
    half_day_type half_day_type,  -- enum: first_half, second_half
    
    reason TEXT NOT NULL,
    status leave_status NOT NULL DEFAULT 'pending_level1',  -- enum: pending_level1, approved_level1, pending_level2, approved_final, rejected, cancelled
    
    -- Level 1 approval (Team Lead)
    level1_approver_code VARCHAR(6),
    level1_approved_at TIMESTAMP,
    level1_notes TEXT,
    
    -- Level 2 approval (Manager)
    level2_approver_code VARCHAR(6),
    level2_approved_at TIMESTAMP,
    level2_notes TEXT,
    
    rejection_reason TEXT,
    cancelled_at TIMESTAMP,
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CHECK (end_date >= start_date),
    CHECK (total_days > 0)
);

CREATE INDEX idx_leave_user_id ON leave_requests(user_id);
CREATE INDEX idx_leave_status ON leave_requests(status);
CREATE INDEX idx_leave_dates ON leave_requests(start_date, end_date);
```

### Parking Tables

```sql
CREATE TABLE parking_slots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slot_code VARCHAR(10) UNIQUE NOT NULL,  -- e.g., A-01, B-15
    status parking_slot_status NOT NULL DEFAULT 'available',  -- enum: available, occupied, disabled
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE parking_allocations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),  -- Null for visitors
    slot_id UUID NOT NULL REFERENCES parking_slots(id),
    
    -- Vehicle info (denormalized for history)
    vehicle_number VARCHAR(20) NOT NULL,
    vehicle_type vehicle_type NOT NULL,
    
    -- Visitor info
    visitor_name VARCHAR(100),  -- For non-employee parking
    
    -- Time tracking
    entry_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    exit_time TIMESTAMP,
    duration_mins INTEGER,  -- Calculated on exit
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,  -- TRUE = currently parked, FALSE = exited
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_parking_user_id ON parking_allocations(user_id);
CREATE INDEX idx_parking_slot_id ON parking_allocations(slot_id);
CREATE INDEX idx_parking_is_active ON parking_allocations(is_active);
```

### Desk & Conference Room Tables

```sql
CREATE TABLE desks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    desk_code VARCHAR(10) UNIQUE NOT NULL,  -- Auto-generated: D-001, CR-001
    desk_label VARCHAR(100) NOT NULL,  -- Display name: "Desk 25", "Meeting Room A"
    desk_type desk_type NOT NULL,  -- enum: desk, conference_room
    status desk_status NOT NULL DEFAULT 'available',  -- enum: available, assigned, maintenance
    
    -- Location
    zone VARCHAR(50),  -- e.g., "Zone A", "Floor 3"
    
    -- Equipment
    has_monitor BOOLEAN DEFAULT FALSE,
    has_docking_station BOOLEAN DEFAULT FALSE,
    capacity INTEGER,  -- For conference rooms
    
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE desk_bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    desk_id UUID NOT NULL REFERENCES desks(id),
    
    -- Date range booking
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    
    purpose TEXT,
    status booking_status NOT NULL DEFAULT 'confirmed',  -- enum: pending, confirmed, cancelled
    
    -- For conference rooms (approval workflow)
    approved_by_id UUID REFERENCES users(id),
    approved_at TIMESTAMP,
    rejection_reason TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevent overlapping bookings
    EXCLUDE USING gist (
        desk_id WITH =,
        daterange(start_date, end_date, '[]') WITH &&
    )
);

CREATE INDEX idx_desk_bookings_user_id ON desk_bookings(user_id);
CREATE INDEX idx_desk_bookings_desk_id ON desk_bookings(desk_id);
CREATE INDEX idx_desk_bookings_dates ON desk_bookings(start_date, end_date);
```

### Food Ordering Tables

```sql
-- Menu items with embeddings for semantic search
CREATE TABLE food_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category food_category NOT NULL,  -- enum: breakfast, lunch, snacks, beverages, dinner
    price DECIMAL(10,2) NOT NULL,
    
    -- Dietary info
    is_vegetarian BOOLEAN DEFAULT TRUE,
    is_vegan BOOLEAN DEFAULT FALSE,
    ingredients JSONB,  -- Array of ingredients
    dietary_info JSONB,  -- Array of tags: ["gluten-free", "spicy", etc.]
    
    -- Availability
    is_available BOOLEAN DEFAULT TRUE,
    available_days JSONB,  -- Array of days: ["monday", "tuesday"]
    
    -- Semantic search
    embedding vector(384),  -- pgvector column for semantic search
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE food_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    order_number VARCHAR(50) UNIQUE NOT NULL,  -- ORD-20260211-001
    
    status order_status NOT NULL DEFAULT 'pending',  -- enum: pending, confirmed, preparing, ready, delivered, cancelled
    total_amount DECIMAL(10,2) NOT NULL,
    
    order_date DATE NOT NULL,
    delivery_time TIME,
    notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES food_orders(id) ON DELETE CASCADE,
    item_id UUID NOT NULL REFERENCES food_items(id),
    
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price DECIMAL(10,2) NOT NULL,  -- Price at time of order (denormalized)
    subtotal DECIMAL(10,2) NOT NULL,  -- quantity * price
    
    special_instructions TEXT
);

CREATE INDEX idx_food_orders_user_id ON food_orders(user_id);
CREATE INDEX idx_food_orders_order_number ON food_orders(order_number);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
```

### IT Asset Tables

```sql
CREATE TABLE it_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_code VARCHAR(20) UNIQUE NOT NULL,  -- LAP-001, MON-002, etc.
    asset_name VARCHAR(200) NOT NULL,
    asset_type asset_type NOT NULL,  -- enum: laptop, monitor, keyboard, mouse, headphones, docking_station, printer, etc.
    
    status asset_status NOT NULL DEFAULT 'available',  -- enum: available, assigned, under_maintenance, retired
    
    -- Product details
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    serial_number VARCHAR(100),
    specifications JSONB,  -- Flexible JSON for specs
    
    -- Purchase info
    purchase_date DATE,
    purchase_price DECIMAL(12,2),
    warranty_until DATE,
    
    -- Current assignment
    assigned_to_id UUID REFERENCES users(id),
    assigned_at TIMESTAMP,
    
    -- Semantic search
    embedding vector(384),  -- For searching assets by description
    
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE asset_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id UUID NOT NULL REFERENCES it_assets(id),
    user_id UUID NOT NULL REFERENCES users(id),
    
    assigned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    returned_at TIMESTAMP,
    notes TEXT,
    
    is_current BOOLEAN DEFAULT TRUE  -- Only one current assignment per asset
);

CREATE INDEX idx_it_assets_asset_code ON it_assets(asset_code);
CREATE INDEX idx_it_assets_status ON it_assets(status);
CREATE INDEX idx_asset_assignments_asset_id ON asset_assignments(asset_id);
CREATE INDEX idx_asset_assignments_user_id ON asset_assignments(user_id);
```

### IT Request Table

```sql
CREATE TABLE it_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_number VARCHAR(50) UNIQUE NOT NULL,  -- REQ-20260211-001
    user_id UUID NOT NULL REFERENCES users(id),
    
    request_type it_request_type NOT NULL,  -- enum: new, new_asset, repair, replacement, software_install, access_request, network_issue, other
    item_type asset_type,  -- For hardware requests
    
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    priority priority_level NOT NULL DEFAULT 'medium',  -- enum: low, medium, high, urgent
    
    status request_status NOT NULL DEFAULT 'pending',  -- enum: pending, approved, in_progress, completed, rejected, cancelled
    
    required_by DATE,
    
    -- Approval
    approved_by_code VARCHAR(6),
    approved_at TIMESTAMP,
    approval_notes TEXT,
    
    -- Assignment
    assigned_to_code VARCHAR(6),  -- IT staff handling the request
    
    -- Completion
    completed_at TIMESTAMP,
    resolution_notes TEXT,
    assigned_asset_id UUID REFERENCES it_assets(id),  -- For NEW_ASSET requests
    
    rejection_reason TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_it_requests_user_id ON it_requests(user_id);
CREATE INDEX idx_it_requests_status ON it_requests(status);
CREATE INDEX idx_it_requests_request_number ON it_requests(request_number);
```

### Project Table

```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_code VARCHAR(50) UNIQUE NOT NULL,  -- PRJ-2026-001
    project_name VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    
    team_lead_id UUID NOT NULL REFERENCES users(id),
    
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    
    estimated_budget DECIMAL(15,2),
    approved_budget DECIMAL(15,2),
    actual_cost DECIMAL(15,2),
    
    team_size INTEGER,
    required_skills JSONB,  -- Array of skills
    
    status project_status NOT NULL DEFAULT 'pending_approval',  -- enum: pending_approval, approved, in_progress, on_hold, completed, cancelled, rejected
    
    business_justification TEXT,
    
    -- Approval
    approved_by_code VARCHAR(6),
    approved_at TIMESTAMP,
    approval_notes TEXT,
    rejection_reason TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CHECK (end_date >= start_date)
);

CREATE INDEX idx_projects_team_lead_id ON projects(team_lead_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_project_code ON projects(project_code);
```

### Holiday Table

```sql
CREATE TABLE holidays (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    holiday_name VARCHAR(200) NOT NULL,
    holiday_date DATE NOT NULL,
    is_mandatory BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(holiday_date)  -- One holiday per date
);

CREATE INDEX idx_holidays_date ON holidays(holiday_date);
```

### Enums

```sql
-- User-related enums
CREATE TYPE user_role AS ENUM ('super_admin', 'admin', 'manager', 'team_lead', 'employee');
CREATE TYPE manager_type AS ENUM ('parking', 'attendance', 'desk_conference', 'cafeteria', 'it_support');
CREATE TYPE vehicle_type AS ENUM ('car', 'bike', 'two_wheeler');

-- Attendance-related enums
CREATE TYPE attendance_status AS ENUM ('draft', 'pending_approval', 'approved', 'rejected');
CREATE TYPE entry_type AS ENUM ('regular', 'overtime', 'break');

-- Leave-related enums
CREATE TYPE leave_type AS ENUM ('casual', 'sick', 'privilege', 'unpaid');
CREATE TYPE leave_status AS ENUM ('pending_level1', 'approved_level1', 'pending_level2', 'approved_final', 'rejected', 'cancelled');
CREATE TYPE half_day_type AS ENUM ('first_half', 'second_half');

-- Parking-related enums
CREATE TYPE parking_slot_status AS ENUM ('available', 'occupied', 'disabled');

-- Desk-related enums
CREATE TYPE desk_type AS ENUM ('desk', 'conference_room');
CREATE TYPE desk_status AS ENUM ('available', 'assigned', 'maintenance');
CREATE TYPE booking_status AS ENUM ('pending', 'confirmed', 'cancelled');

-- Food-related enums
CREATE TYPE food_category AS ENUM ('breakfast', 'lunch', 'snacks', 'beverages', 'dinner');
CREATE TYPE order_status AS ENUM ('pending', 'confirmed', 'preparing', 'ready', 'delivered', 'cancelled');

-- IT-related enums
CREATE TYPE asset_type AS ENUM ('laptop', 'monitor', 'keyboard', 'mouse', 'headphones', 'docking_station', 'printer', 'scanner', 'tablet', 'phone', 'other');
CREATE TYPE asset_status AS ENUM ('available', 'assigned', 'under_maintenance', 'retired');
CREATE TYPE it_request_type AS ENUM ('new', 'new_asset', 'repair', 'replacement', 'software_install', 'access_request', 'network_issue', 'other');
CREATE TYPE priority_level AS ENUM ('low', 'medium', 'high', 'urgent');
CREATE TYPE request_status AS ENUM ('pending', 'approved', 'in_progress', 'completed', 'rejected', 'cancelled');

-- Project-related enums
CREATE TYPE project_status AS ENUM ('pending_approval', 'approved', 'in_progress', 'on_hold', 'completed', 'cancelled', 'rejected');
```

### Vector Search Setup

```sql
-- Install pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create IVFFlat index for faster similarity search (after data is populated)
CREATE INDEX idx_food_items_embedding ON food_items 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);

CREATE INDEX idx_it_assets_embedding ON it_assets 
USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);
```

---

### Response Formatting
All API responses follow a consistent format:
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful",
  "timestamp": "2026-02-11T10:30:00Z"
}
```

### Relationship Loading
SQLAlchemy relationships are properly loaded using `selectinload` to avoid N+1 query problems and `MissingGreenlet` errors in async contexts:
```python
# Example from IT Request Service
result = await self.db.execute(
    select(ITRequest)
    .options(
        selectinload(ITRequest.user),
        selectinload(ITRequest.asset),
        selectinload(ITRequest.approved_by),
        selectinload(ITRequest.assigned_to)
    )
)
```

---

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

IT Requests follow a simplified workflow: Create → Approve/Reject. No separate "start" or "complete" steps.

### `POST /it-requests`
**Description**: Create an IT request

**Request Body**:
```json
{
  "request_type": "NEW_ASSET",  // NEW, NEW_ASSET, REPAIR, REPLACEMENT, SOFTWARE_INSTALL, ACCESS_REQUEST, NETWORK_ISSUE, OTHER
  "title": "Need new laptop",
  "description": "Current laptop is slow, need upgrade for development work",
  "priority": "HIGH",  // LOW | MEDIUM | HIGH | URGENT
  "related_asset_code": "LAP-001"  // Optional: if request relates to existing asset
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "request_number": "ITR-20260211162603-8B4270",
    "user_code": "1001",
    "user_name": "John Doe",
    "request_type": "NEW_ASSET",
    "related_asset_id": "uuid",
    "related_asset_code": "LAP-001",
    "title": "Need new laptop",
    "description": "Current laptop is slow...",
    "status": "PENDING",
    "priority": "HIGH",
    "approved_by_code": null,
    "approved_by_name": null,
    "approved_at": null,
    "approval_notes": null,
    "assigned_to_code": null,
    "assigned_to_name": null,
    "assigned_at": null,
    "started_at": null,
    "completed_at": null,
    "resolution_notes": null,
    "rejection_reason": null,
    "created_at": "2026-02-11T10:00:00Z",
    "updated_at": "2026-02-11T10:00:00Z"
  },
  "message": "IT request created successfully"
}
```

---

### `GET /it-requests`
**Description**: List IT requests

**Query Parameters**:
- `page`, `page_size`
- `user_code` (optional): Filter by user code (IT Manager only)
- `status` (optional): PENDING | APPROVED | REJECTED | IN_PROGRESS | COMPLETED | CANCELLED
- `request_type` (optional): Filter by request type
- `priority` (optional): Filter by priority

**Access**:
- IT Manager: ALL requests
- Others: Only own requests

---

### `GET /it-requests/my`
**Description**: Get current user's IT requests

---

### `POST /it-requests/{request_id}/approve`
**Description**: Approve or reject IT request

**Access**: IT Support Manager only

**Request Body**:
```json
{
  "action": "approve",  // "approve" or "reject"
  "notes": "Approved, will assign laptop by Friday",
  "assigned_to_code": "IT5001",  // Optional: Assign to specific IT staff user code
  "rejection_reason": "Not justified"  // Required if action is "reject"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "request_number": "ITR-20260211162603-8B4270",
    "user_code": "1001",
    "user_name": "John Doe",
    "request_type": "NEW_ASSET",
    "status": "APPROVED",
    "approved_by_code": "IT5000",
    "approved_by_name": "IT Manager",
    "approved_at": "2026-02-11T11:00:00Z",
    "approval_notes": "Approved, will assign laptop by Friday",
    "assigned_to_code": "IT5001",
    "assigned_to_name": "IT Staff Member",
    "assigned_at": "2026-02-11T11:00:00Z"
  },
  "message": "IT request approved successfully"
}
```

**Business Logic**:
- Approved requests move to "APPROVED" status
- Rejected requests move to "REJECTED" status
- Can optionally assign to IT staff for fulfillment
- All user details (names) are populated from relationships

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

## 💻 Development Guide

### Setting Up Development Environment

#### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd unified-office-management

# Create Python virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

#### 2. Database Setup

```bash
# Option A: Using Docker (Recommended)
docker compose up -d db  # Start PostgreSQL with pgvector

# Option B: Local PostgreSQL
# Install PostgreSQL 15+ and pgvector extension
# Create database manually
createdb office_management
psql office_management -c "CREATE EXTENSION vector;"
```

#### 3. Configure Environment

```bash
# Create .env file
cp .env.example .env

# Edit .env with your settings
nano .env  # or vim, code, etc.
```

Required environment variables:
```env
# Database (adjust for your setup)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/office_management
DATABASE_URL_SYNC=postgresql://postgres:postgres@localhost:5432/office_management

# Security (MUST change in production!)
SECRET_KEY=your-super-secret-key-minimum-32-characters-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
APP_NAME=Unified Office Management System
DEBUG=True  # Set to False in production
API_V1_PREFIX=/api/v1

# Company
COMPANY_DOMAIN=company.com

# AI/Vector Search
EMBEDDING_MODEL=all-MiniLM-L6-v2
VECTOR_DIMENSION=384
```

#### 4. Run Migrations

```bash
# Apply all database migrations
alembic upgrade head

# Check current migration version
alembic current

# View migration history
alembic history
```

#### 5. Seed Initial Data

```bash
# Create super admin and sample hierarchical users
python scripts/seed_hierarchy.py

# This creates:
# - Super Admin (super.admin@company.com / Admin@123)
# - Admin (admin@company.com / Admin@123)
# - 5 Managers (one for each type)
# - Multiple Team Leads
# - Sample employees

# Optional: Seed additional sample data (parking, desks, food items)
python scripts/seed_data.py
```

#### 6. Run Development Server

```bash
# Start with auto-reload
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Or with custom settings
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080 --log-level debug
```

#### 7. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Creating Database Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description of changes"

# Review the generated migration file in alembic/versions/
# Edit if necessary, then apply
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>
```

### Code Organization Best Practices

#### Adding a New Feature Module

1. **Create Model** (`app/models/new_feature.py`)
```python
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
import uuid

class NewFeature(Base):
    __tablename__ = "new_features"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    user_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default="now()")
    
    # Relationships
    user = relationship("User", back_populates="new_features")
```

2. **Create Schemas** (`app/schemas/new_feature.py`)
```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NewFeatureBase(BaseModel):
    name: str

class NewFeatureCreate(NewFeatureBase):
    pass

class NewFeatureResponse(NewFeatureBase):
    id: str
    user_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True
```

3. **Create Service** (`app/services/new_feature_service.py`)
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.new_feature import NewFeature
from app.schemas.new_feature import NewFeatureCreate

class NewFeatureService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: NewFeatureCreate, user_id: str):
        new_item = NewFeature(**data.dict(), user_id=user_id)
        self.db.add(new_item)
        await self.db.commit()
        await self.db.refresh(new_item)
        return new_item
    
    async def get_all(self):
        result = await self.db.execute(
            select(NewFeature).options(selectinload(NewFeature.user))
        )
        return result.scalars().all()
```

4. **Create Endpoints** (`app/api/v1/endpoints/new_feature.py`)
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.new_feature_service import NewFeatureService
from app.schemas.new_feature import NewFeatureCreate, NewFeatureResponse
from app.utils.response import success_response

router = APIRouter(prefix="/new-features", tags=["New Feature"])

@router.post("", response_model=dict)
async def create_new_feature(
    data: NewFeatureCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = NewFeatureService(db)
    result = await service.create(data, current_user.id)
    return success_response(
        data=NewFeatureResponse.from_orm(result).dict(),
        message="Created successfully"
    )
```

5. **Register Router** (`app/api/v1/router.py`)
```python
from app.api.v1.endpoints import new_feature

api_router.include_router(new_feature.router)
```

6. **Create Migration**
```bash
alembic revision --autogenerate -m "add new_feature table"
alembic upgrade head
```

### Testing Guidelines

```bash
# Install test dependencies (if not already installed)
pip install pytest pytest-asyncio pytest-cov httpx

# Run all tests
pytest -v

# Run with coverage
pytest --cov=app --cov-report=term-missing --cov-report=html

# Run specific test file
pytest tests/test_attendance.py -v

# Run specific test function
pytest tests/test_auth.py::test_login_success -v

# Run tests matching pattern
pytest -k "test_parking" -v

# View coverage report
open htmlcov/index.html  # Open coverage HTML report
```

### Debugging

#### Enable Debug Logging

```python
# In app/main.py
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

#### VS Code Launch Configuration (`.vscode/launch.json`)

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "app.main:app",
                "--reload",
                "--host", "127.0.0.1",
                "--port", "8000"
            ],
            "jinja": true,
            "justMyCode": true,
            "env": {
                "DATABASE_URL": "postgresql+asyncpg://postgres:postgres@localhost:5432/office_management"
            }
        }
    ]
}
```

#### Database Query Logging

```python
# In app/core/database.py
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Enable SQL query logging
    future=True
)
```

---

## 🚀 Deployment

### Docker Deployment (Recommended)

#### Using Docker Compose

```bash
# Build and start all services
docker compose up --build

# Run in detached mode
docker compose up -d

# View logs
docker compose logs -f backend

# Stop services
docker compose down

# Stop and remove volumes (WARNING: deletes database data)
docker compose down -v
```

The `docker-compose.yml` includes:
- **PostgreSQL with pgvector**: Database service
- **Backend API**: FastAPI application
- **Auto-migrations**: Runs `alembic upgrade head` on startup
- **Volume persistence**: Database data persisted in Docker volume

#### Custom Docker Build

```bash
# Build image
docker build -t unified-office-backend:latest .

# Run container
docker run -d \
  --name office-backend \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname \
  -e SECRET_KEY=your-secret-key \
  unified-office-backend:latest

# View logs
docker logs -f office-backend

# Stop container
docker stop office-backend

# Remove container
docker rm office-backend
```

### Production Deployment Checklist

#### 1. Environment Configuration

```env
# Production .env file

# Database - Use production PostgreSQL
DATABASE_URL=postgresql+asyncpg://prod_user:secure_password@db.prod.com:5432/office_db
DATABASE_URL_SYNC=postgresql://prod_user:secure_password@db.prod.com:5432/office_db

# Security - CRITICAL: Change these!
SECRET_KEY=<generate-strong-random-secret-min-32-chars>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480  # Shorter expiry for production (8 hours)
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
APP_NAME=Unified Office Management System
DEBUG=False  # MUST be False in production
API_V1_PREFIX=/api/v1

# CORS - Configure allowed origins
ALLOWED_ORIGINS=https://yourapp.com,https://www.yourapp.com

# Company
COMPANY_DOMAIN=yourcompany.com

# Vector Search
EMBEDDING_MODEL=all-MiniLM-L6-v2
VECTOR_DIMENSION=384
```

#### 2. Generate Secure SECRET_KEY

```python
# Python script to generate secure key
import secrets
print(secrets.token_urlsafe(32))
```

Or using command line:
```bash
openssl rand -base64 32
```

#### 3. Database Preparation

```bash
# Create production database
createdb -U postgres office_management

# Enable pgvector extension
psql -U postgres office_management -c "CREATE EXTENSION vector;"

# Run migrations
alembic upgrade head

# Create super admin (production)
python scripts/seed_hierarchy.py  # Or create manually via psql
```

#### 4. Configure Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/office-api

upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.yourcompany.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourcompany.com;
    
    # SSL certificates
    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # Logging
    access_log /var/log/nginx/office-api-access.log;
    error_log /var/log/nginx/office-api-error.log;
    
    # Proxy settings
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # File upload size limit
    client_max_body_size 10M;
}
```

#### 5. Systemd Service (Linux)

```ini
# /etc/systemd/system/office-backend.service

[Unit]
Description=Unified Office Management Backend
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/unified-office-management
Environment="PATH=/var/www/unified-office-management/venv/bin"
ExecStart=/var/www/unified-office-management/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable office-backend
sudo systemctl start office-backend

# Check status
sudo systemctl status office-backend

# View logs
sudo journalctl -u office-backend -f
```

#### 6. Process Manager (Supervisor - Alternative)

```ini
# /etc/supervisor/conf.d/office-backend.conf

[program:office-backend]
command=/var/www/unified-office-management/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
directory=/var/www/unified-office-management
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/office-backend.log
```

```bash
# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start office-backend
```

#### 7. Performance Optimization

```python
# app/main.py - Production settings

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,  # Number of worker processes (2 x CPU cores)
        loop="uvloop",  # Use uvloop for better performance
        http="httptools",  # Use httptools for faster HTTP parsing
        log_level="info",
        access_log=True
    )
```

#### 8. Monitoring & Logging

```bash
# Application logs
tail -f /var/log/office-backend.log

# Nginx logs
tail -f /var/log/nginx/office-api-access.log
tail -f /var/log/nginx/office-api-error.log

# PostgreSQL logs
tail -f /var/log/postgresql/postgresql-15-main.log
```

#### 9. Backup Strategy

```bash
# Database backup script
#!/bin/bash
# /usr/local/bin/backup-office-db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backups/office-db
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U postgres office_management | gzip > $BACKUP_DIR/office_db_$DATE.sql.gz

# Keep only last 30 days of backups
find $BACKUP_DIR -name "office_db_*.sql.gz" -mtime +30 -delete

# Cron job: 0 2 * * * /usr/local/bin/backup-office-db.sh
```

#### 10. Health Check Endpoint

The API includes a health check endpoint at the root:

```bash
# Check if API is running
curl http://localhost:8000/

# Response:
# {"message": "Unified Office Management API is running", "version": "1.0.0"}
```

### Cloud Deployment Examples

#### AWS (EC2 + RDS)

1. **Launch EC2 instance** (Ubuntu 22.04, t3.medium or larger)
2. **Create RDS PostgreSQL** instance (15.x with pgvector extension)
3. **Configure Security Groups**:
   - EC2: Allow inbound 8000 (from Load Balancer), 22 (SSH)
   - RDS: Allow inbound 5432 (from EC2 security group)
4. **Deploy application** using systemd or Docker
5. **Setup Application Load Balancer** (ALB) with SSL certificate
6. **Configure Route 53** for DNS

#### Google Cloud (Cloud Run + Cloud SQL)

```bash
# Build and push Docker image
gcloud builds submit --tag gcr.io/PROJECT_ID/office-backend

# Deploy to Cloud Run
gcloud run deploy office-backend \
  --image gcr.io/PROJECT_ID/office-backend \
  --platform managed \
  --region us-central1 \
  --set-env-vars DATABASE_URL=... \
  --set-env-vars SECRET_KEY=... \
  --allow-unauthenticated
```

#### DigitalOcean (App Platform)

1. Create PostgreSQL database cluster
2. Create App Platform app from GitHub repo
3. Configure environment variables
4. Enable automatic deployments from git

---

## 🧪 Testing

### Running Tests

```bash
# Install test dependencies (if not in requirements.txt)
pip install pytest pytest-asyncio pytest-cov httpx aiosqlite

# Run all tests
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=term-missing --cov-report=html

# Run specific test file
pytest tests/test_attendance.py -v

# Run specific test function
pytest tests/test_auth.py::test_login_success -v

# Run tests matching pattern
pytest -k "attendance" -v

# Run tests in parallel (faster)
pytest -n auto  # requires pytest-xdist
```

### Test Coverage

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Open coverage report in browser
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Test Structure

```
tests/
├── conftest.py              # Pytest fixtures (test database, client)
├── test_auth.py             # Authentication tests
├── test_users.py            # User management tests
├── test_attendance.py       # Attendance workflow tests
├── test_leave.py            # Leave management tests
├── test_parking.py          # Parking operations tests
├── test_desks.py            # Desk booking tests
├── test_food.py             # Food ordering tests
├── test_it_assets.py        # IT asset management tests
├── test_it_requests.py      # IT request workflow tests
├── test_projects.py         # Project management tests
└── test_search.py           # Semantic search tests
```

### Test Database

Tests use a separate SQLite database by default for faster execution:

```python
# conftest.py
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Or use test PostgreSQL database
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/office_test"
```

### Writing Tests

Example test file structure:

```python
# tests/test_my_feature.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_item(client: AsyncClient, employee_token: str):
    """Test creating a new item"""
    response = await client.post(
        "/api/v1/items",
        json={"name": "Test Item"},
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "id" in data["data"]

@pytest.mark.asyncio
async def test_get_items(client: AsyncClient, employee_token: str):
    """Test retrieving items"""
    response = await client.get(
        "/api/v1/items",
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
```

### CI/CD Pipeline Example (GitHub Actions)

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: pgvector/pgvector:pg16
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: office_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/office_test
        run: |
          pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

---

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

## Database Models & Enums

### Core Enums

```python
# User Roles (hierarchical)
class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    TEAM_LEAD = "team_lead"
    EMPLOYEE = "employee"

# Manager Types (specializations)
class ManagerType(str, Enum):
    PARKING = "parking"
    ATTENDANCE = "attendance"
    DESK_CONFERENCE = "desk_conference"
    CAFETERIA = "cafeteria"
    IT_SUPPORT = "it_support"

# IT Request Types
class ITRequestType(str, Enum):
    NEW = "NEW"
    NEW_ASSET = "NEW_ASSET"
    REPAIR = "REPAIR"
    REPLACEMENT = "REPLACEMENT"
    SOFTWARE_INSTALL = "SOFTWARE_INSTALL"
    ACCESS_REQUEST = "ACCESS_REQUEST"
    NETWORK_ISSUE = "NETWORK_ISSUE"
    OTHER = "OTHER"

# IT Request Status
class ITRequestStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

# IT Request Priority
class ITRequestPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

# Leave Types
class LeaveType(str, Enum):
    CASUAL = "casual"
    SICK = "sick"
    PRIVILEGE = "privilege"
    UNPAID = "unpaid"

# Attendance Status
class AttendanceStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"

# Project Status
class ProjectStatus(str, Enum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    IN_PROGRESS = "IN_PROGRESS"
    ON_HOLD = "ON_HOLD"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
```

### Key Model Relationships

```
User
├── created_by (User) - who created this user
├── team_lead (User) - user's team lead
├── manager (User) - user's manager
├── admin (User) - user's admin
└── team_members (List[User]) - users reporting to this user

ITRequest
├── user (User) - who created the request
├── asset (ITAsset) - related IT asset (optional)
├── approved_by (User) - who approved/rejected
└── assigned_to (User) - IT staff assigned to fulfill

ITAsset
├── assignments (List[ITAssetAssignment]) - assignment history
└── requests (List[ITRequest]) - related IT requests

Attendance
├── user (User) - attendance owner
├── entries (List[AttendanceEntry]) - check-in/out entries
└── approved_by (User) - who approved

LeaveRequest
├── user (User) - requester
├── level1_approver (User) - team lead approval
└── level2_approver (User) - manager approval

Project
├── team_lead (User) - project owner
└── approved_by (User) - admin who approved
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
│ IT Support Request Lifecycle (Simplified)                       │
└─────────────────────────────────────────────────────────────────┘

EMPLOYEE has IT issue/need
    ↓ Creates IT request
    ↓ [POST /it-requests]
    ↓ Provides: request_type, title, description, priority
    ↓ Optional: related_asset_code (if request relates to existing asset)
    ↓ Request types: NEW, NEW_ASSET, REPAIR, REPLACEMENT,
    │                 SOFTWARE_INSTALL, ACCESS_REQUEST,
    │                 NETWORK_ISSUE, OTHER
    ↓ System auto-generates request_number: ITR-20260211162603-8B4270
    ↓ Status: PENDING
    ↓
IT Support Manager reviews requests
    ↓ [GET /it-requests] - Sees all requests
    ↓ Views request details with full user information
    ↓
IT Support Manager approves or rejects
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
    ↓ approved_by_code, approved_by_name populated
    ↓ approved_at timestamp set
    ↓ If assigned_to_code provided:
    │   - assigned_to_code, assigned_to_name populated
    │   - assigned_at timestamp set
    ↓ IT staff fulfills request (external to system)
    ↓ Request complete ✓
    ↓
If rejected:
    ↓ Status: REJECTED
    ↓ rejection_reason saved
    ↓ Employee can view rejection reason
    ↓ Can create new request with more details
```

**IT Request Types:**
| Type | Description |
|------|-------------|
| `NEW` | General IT request |
| `NEW_ASSET` | Need new equipment (laptop, monitor, etc.) |
| `REPAIR` | Fix existing asset |
| `REPLACEMENT` | Replace broken/old asset |
| `SOFTWARE_INSTALL` | Install software on machine |
| `ACCESS_REQUEST` | Network/system access |
| `NETWORK_ISSUE` | Network connectivity problems |
| `OTHER` | Other IT support needs |

**Priority Levels:**
| Priority | Description |
|----------|-------------|
| `LOW` | Can wait, no urgency |
| `MEDIUM` | Normal priority |
| `HIGH` | Important, needs attention soon |
| `URGENT` | Critical, needs immediate attention |

**Simplified Workflow Benefits:**
- ✅ Single approval step (no complex state machine)
- ✅ IT Manager approves → Request is done
- ✅ Optional assignment to IT staff for tracking
- ✅ Full user name resolution in responses (user_name, approved_by_name, assigned_to_name)
- ✅ Related asset linking via asset_code

**Response Format:**
All IT request responses include:
- User details: `user_code`, `user_name`
- Approval details: `approved_by_code`, `approved_by_name`, `approved_at`, `approval_notes`
- Assignment details: `assigned_to_code`, `assigned_to_name`, `assigned_at`
- Asset details: `related_asset_id`, `related_asset_code`
- Timestamps: `created_at`, `updated_at`

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

## Error Handling

### Standard Error Response Format

```json
{
  "success": false,
  "detail": "Error message explaining what went wrong",
  "timestamp": "2026-02-11T10:30:00Z"
}
```

### Common HTTP Status Codes

| Status Code | Meaning | Common Causes |
|-------------|---------|---------------|
| `200 OK` | Success | Request completed successfully |
| `201 Created` | Resource created | POST request created new resource |
| `400 Bad Request` | Invalid request | Validation error, business rule violation |
| `401 Unauthorized` | Not authenticated | Missing or invalid JWT token |
| `403 Forbidden` | Not authorized | User lacks permission for this action |
| `404 Not Found` | Resource not found | Invalid ID or resource doesn't exist |
| `422 Unprocessable Entity` | Validation failed | Request body doesn't match schema |
| `500 Internal Server Error` | Server error | Unexpected error (check logs) |

### Common Error Scenarios

**Authentication Errors:**
```json
// Invalid credentials
{"detail": "Invalid email or password"}

// Token expired
{"detail": "Token has expired"}

// Inactive user
{"detail": "User account is inactive"}
```

**Permission Errors:**
```json
// Insufficient role
{"detail": "Only IT Support Manager can approve IT requests"}

// Not the owner
{"detail": "Cannot update another user's request"}
```

**Business Rule Errors:**
```json
// Invalid state transition
{"detail": "Cannot approve request with status REJECTED"}

// Duplicate action
{"detail": "Already have active parking"}

// Resource unavailable
{"detail": "No available parking slots"}
```

**Validation Errors:**
```json
{
  "detail": [
    {
      "loc": ["body", "description"],
      "msg": "String should have at least 10 characters",
      "type": "string_too_short"
    }
  ]
}
```

---

## Development Notes

### Adding New Features

1. **Create Model** in `app/models/` with SQLAlchemy ORM
2. **Create Schemas** in `app/schemas/` with Pydantic
3. **Create Service** in `app/services/` for business logic
4. **Create Endpoints** in `app/api/v1/endpoints/`
5. **Register Router** in `app/api/v1/router.py`
6. **Create Migration** with `alembic revision --autogenerate`

### Async Best Practices

```python
# Always use selectinload for relationships in async context
from sqlalchemy.orm import selectinload

result = await db.execute(
    select(Model).options(
        selectinload(Model.relationship1),
        selectinload(Model.relationship2)
    )
)

# After commit, reload with relationships (not just refresh)
await db.commit()
result = await db.execute(
    select(Model).where(Model.id == id).options(
        selectinload(Model.relationship)
    )
)
model = result.scalar_one()
```

### Response Helpers

```python
from app.utils.response import create_response, create_paginated_response

# Standard response
return create_response(
    data={"key": "value"},
    message="Operation successful"
)

# Paginated response
return create_paginated_response(
    data=items,
    total=total_count,
    page=page,
    page_size=page_size,
    message="Items retrieved"
)
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Database Connection Errors

**Error:** `could not translate host name "db" to address`

**Solution:**
```bash
# If using Docker Compose
docker compose down
docker compose up --build

# If using local database
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U postgres -h localhost -d office_management
```

**Error:** `FATAL: password authentication failed`

**Solution:**
- Check DATABASE_URL in .env matches PostgreSQL credentials
- Ensure user exists and has correct password
- For Docker: Check docker-compose.yml environment variables

#### 2. Migration Errors

**Error:** `Can't locate revision identified by 'xxxxx'`

**Solution:**
```bash
# Reset migration history (WARNING: Development only!)
# Drop all tables
psql -U postgres office_management -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Recreate from scratch
alembic upgrade head
python scripts/seed_hierarchy.py
```

**Error:** `Target database is not up to date`

**Solution:**
```bash
# Check current version
alembic current

# Upgrade to head
alembic upgrade head

# If that fails, check for conflicts in migration files
alembic history
```

#### 3. pgvector Extension Errors

**Error:** `type "vector" does not exist`

**Solution:**
```bash
# Install pgvector extension
psql -U postgres office_management -c "CREATE EXTENSION vector;"

# Verify installation
psql -U postgres office_management -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

**For Docker:**
```bash
# Use pgvector-enabled PostgreSQL image
# In docker-compose.yml:
#   image: pgvector/pgvector:pg16
```

#### 4. Import Errors

**Error:** `ModuleNotFoundError: No module named 'app'`

**Solution:**
```bash
# Ensure you're in the correct directory
cd unified-office-management

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run from project root
uvicorn app.main:app --reload
```

#### 5. JWT Token Errors

**Error:** `{"detail": "Could not validate credentials"}`

**Solution:**
- Check Authorization header format: `Bearer <token>`
- Verify token hasn't expired (24-hour default)
- Ensure SECRET_KEY in .env matches server's SECRET_KEY
- Try logging in again to get fresh token

**Get new token:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@company.com", "password": "Admin@123"}'
```

#### 6. Async/SQLAlchemy Errors

**Error:** `greenlet_spawn has not been called; can't call await_only()`

**Solution:**
- Always use `selectinload` for relationships in async context
- Don't access relationships directly without eager loading

```python
# ❌ Wrong
user = await db.get(User, user_id)
team_lead = user.team_lead  # Error!

# ✅ Correct
result = await db.execute(
    select(User)
    .where(User.id == user_id)
    .options(selectinload(User.team_lead))
)
user = result.scalar_one()
team_lead = user.team_lead  # Works!
```

#### 7. Port Already in Use

**Error:** `Address already in use: 8000`

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows

# Or use different port
uvicorn app.main:app --reload --port 8080
```

#### 8. CORS Errors

**Error:** `No 'Access-Control-Allow-Origin' header`

**Solution:**
```python
# In app/main.py, update CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourapp.com"],  # Specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 9. Embedding Service Errors

**Error:** `Model 'all-MiniLM-L6-v2' not found`

**Solution:**
```bash
# First run downloads the model (~80MB)
# Ensure internet connection
# Model caches to ~/.cache/torch/sentence_transformers/

# If behind proxy, set environment variables
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port
```

**Error:** `ImportError: cannot import name 'SentenceTransformer'`

**Solution:**
```bash
# Reinstall sentence-transformers
pip uninstall sentence-transformers torch
pip install torch==2.1.2 sentence-transformers==2.2.2
```

#### 10. Seeding Errors

**Error:** `User with email already exists`

**Solution:**
```bash
# Script is idempotent, but if you want to reset
psql -U postgres office_management

# Delete existing users
DELETE FROM users;

# Run seed again
python scripts/seed_hierarchy.py
```

#### 11. Docker Build Errors

**Error:** `failed to solve with frontend dockerfile.v0`

**Solution:**
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker compose build --no-cache
docker compose up
```

#### 12. Performance Issues

**Slow Queries:**

```bash
# Enable query logging
# In app/core/database.py, set echo=True

# Check slow queries in PostgreSQL
psql -U postgres office_management
```

```sql
-- Enable query logging
ALTER DATABASE office_management SET log_min_duration_statement = 1000;  -- Log queries > 1s

-- Check running queries
SELECT pid, now() - query_start AS duration, query 
FROM pg_stat_activity 
WHERE state = 'active' AND query NOT LIKE '%pg_stat_activity%'
ORDER BY duration DESC;
```

**Too Many Connections:**

```bash
# Check max connections
psql -U postgres -c "SHOW max_connections;"

# Check current connections
psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# Increase max_connections in postgresql.conf
# max_connections = 200
```

#### 13. Testing Issues

**Error:** `No database found for testing`

**Solution:**
```bash
# Create test database
createdb office_management_test

# Or use SQLite for tests (faster)
# In conftest.py:
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
```

**Error:** `fixture 'client' not found`

**Solution:**
```bash
# Ensure conftest.py exists in tests/ directory
# Check pytest discovers tests
pytest --collect-only
```

---

## 📚 Additional Resources

### API Documentation

- **Interactive Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Related Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Pydantic V2](https://docs.pydantic.dev/latest/)
- [pgvector](https://github.com/pgvector/pgvector)
- [Alembic](https://alembic.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Project Links

- **Repository**: <your-repo-url>
- **Issue Tracker**: <your-repo-url>/issues
- **Wiki**: <your-repo-url>/wiki

---

## 📝 Changelog

### Version 1.0.0 (February 2026)

**Initial Release:**
- ✅ Complete office management system with 12 modules
- ✅ Role-based access control with 5-tier hierarchy
- ✅ JWT authentication with access and refresh tokens
- ✅ Semantic search using sentence transformers (all-MiniLM-L6-v2)
- ✅ Docker containerization with docker-compose
- ✅ PostgreSQL with pgvector for vector similarity search
- ✅ Async-first architecture with SQLAlchemy 2.0
- ✅ Comprehensive API documentation (Swagger + ReDoc)
- ✅ Database migrations with Alembic
- ✅ Seed scripts for initial data
- ✅ Hierarchical approval workflows
- ✅ Auto-generated codes (user, asset, request, project, order)
- ✅ Production-ready deployment configurations

**Modules:**
1. Authentication & User Management
2. Attendance Tracking
3. Leave Management
4. Parking Management
5. Desk & Conference Room Booking
6. Cafeteria Table Booking
7. Food Ordering
8. IT Asset Management
9. IT Request Management
10. Project Management
11. Holiday Management
12. Semantic Search

**Technical Highlights:**
- Proper async relationship loading with `selectinload`
- Consistent response formatting across all endpoints
- Comprehensive error handling and validation
- RBAC enforcement at endpoint level
- Connection pooling and query optimization
- Vector indexing for fast semantic search

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
   - Follow existing code style
   - Add tests for new features
   - Update documentation
4. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
5. **Push to branch**
   ```bash
   git push origin feature/amazing-feature
   ```
6. **Open a Pull Request**

### Code Style

- Follow PEP 8 for Python code
- Use type hints
- Write docstrings for functions and classes
- Keep functions focused and small
- Use async/await consistently

### Testing Requirements

- All new features must have tests
- Maintain or improve code coverage
- Tests must pass before merging

```bash
# Run tests before committing
pytest --cov=app --cov-report=term-missing
```

---

## 📄 License

MIT License

Copyright (c) 2026 Unified Office Management System

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 🆘 Support

### Getting Help

- **Documentation**: Read this README and API docs at http://localhost:8000/docs
- **Issues**: Report bugs or request features via GitHub Issues
- **Discussions**: Ask questions in GitHub Discussions
- **Email**: support@yourcompany.com (if applicable)

### Reporting Issues

When reporting issues, please include:

1. **Environment Information**:
   - OS (Linux/Mac/Windows)
   - Python version (`python --version`)
   - PostgreSQL version (`psql --version`)
   - Docker version (if using Docker)

2. **Steps to Reproduce**:
   - Detailed steps to reproduce the issue
   - Expected behavior vs actual behavior
   - Error messages and stack traces

3. **Additional Context**:
   - Screenshots if applicable
   - Relevant configuration (.env values without secrets)
   - Database migration version (`alembic current`)

### Feature Requests

We welcome feature requests! Please:
- Check existing issues first to avoid duplicates
- Describe the use case and business value
- Provide examples of how the feature would work
- Consider contributing the feature yourself via PR

---

## 🎯 Roadmap

### Planned Features

- [ ] **Websocket Support**: Real-time notifications for approvals
- [ ] **Email Notifications**: Automated emails for important events
- [ ] **Analytics Dashboard**: Reports and insights
- [ ] **Mobile Push Notifications**: Mobile app integration
- [ ] **File Uploads**: Support for documents and images
- [ ] **Calendar Integration**: Sync with Google Calendar, Outlook
- [ ] **Audit Logs**: Comprehensive activity logging
- [ ] **Export Features**: PDF/Excel exports for reports
- [ ] **Multi-tenancy**: Support for multiple companies
- [ ] **Advanced Search**: Full-text search across all modules
- [ ] **Two-Factor Authentication**: Enhanced security
- [ ] **API Rate Limiting**: Prevent abuse
- [ ] **GraphQL API**: Alternative to REST
- [ ] **Metrics & Monitoring**: Prometheus/Grafana integration

### Future Improvements

- Performance optimization with Redis caching
- Elasticsearch integration for advanced search
- Kubernetes deployment configurations
- Automated testing and CI/CD pipeline
- API versioning strategy
- Internationalization (i18n) support
- Dark mode friendly responses
- Webhook support for integrations

---

## 👥 Authors

- **Project Lead**: Your Name
- **Contributors**: See GitHub contributors page

---

## 🙏 Acknowledgments

- FastAPI team for the excellent framework
- SQLAlchemy team for the powerful ORM
- pgvector developers for vector similarity search
- Sentence Transformers team for pre-trained models
- Open source community for continuous inspiration

---

**Made with ❤️ using FastAPI, PostgreSQL, and Python**

---