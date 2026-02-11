# 🤖 AI Agent API Reference Guide

> **Purpose**: This document provides a comprehensive API reference for an AI agent to process natural language requests from employees and execute appropriate API calls.

**Base URL**: `http://127.0.0.1:8000/api/v1`

**Authentication**: All endpoints (except `/auth/login`) require JWT Bearer token in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

---

## 📋 Table of Contents

1. [Authentication](#1-authentication)
2. [Attendance Management](#2-attendance-management)
3. [Leave Management](#3-leave-management)
4. [Parking Management](#4-parking-management)
5. [Desk Booking](#5-desk-booking)
6. [Conference Room Booking](#6-conference-room-booking)
7. [Food Orders](#7-food-orders)
8. [IT Requests](#8-it-requests)
9. [Holidays](#9-holidays)
10. [User Profile](#10-user-profile)
11. [Natural Language Intent Mapping](#11-natural-language-intent-mapping)

---

## 1. Authentication

### Login
**Intent Examples**: "login", "sign in", "authenticate"

```http
POST /auth/login
Content-Type: application/json

{
    "email": "employee@company.com",
    "password": "password123"
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
        "expires_in": 1800
    }
}
```

### Get Current User Profile
**Intent Examples**: "who am I", "my profile", "my details"

```http
GET /auth/me
Authorization: Bearer <token>
```

### Change Password
**Intent Examples**: "change my password", "update password"

```http
POST /auth/change-password
Authorization: Bearer <token>

{
    "current_password": "oldpassword",
    "new_password": "newpassword123",
    "confirm_password": "newpassword123"
}
```

---

## 2. Attendance Management

### Check In
**Intent Examples**: "check in", "mark attendance", "punch in", "start work", "I'm here", "arrived at office"

```http
POST /attendance/check-in
Authorization: Bearer <token>
```
> No request body needed - automatically records current time.

**Response**:
```json
{
    "success": true,
    "message": "Check-in recorded successfully",
    "data": {
        "id": "uuid",
        "user_code": "5001",
        "date": "2026-02-11",
        "status": "draft",
        "total_hours": 0,
        "entries": [...]
    }
}
```

### Check Out
**Intent Examples**: "check out", "punch out", "leaving", "going home", "end work", "signing off"

```http
POST /attendance/check-out
Authorization: Bearer <token>
```
> No request body needed - automatically records current time.

### Get My Attendance Status Today
**Intent Examples**: "my attendance status", "am I checked in", "attendance today", "work hours today"

```http
GET /attendance/my-status
Authorization: Bearer <token>
```

**Response**:
```json
{
    "success": true,
    "data": {
        "has_attendance": true,
        "is_checked_in": true,
        "can_submit": false,
        "status": "draft",
        "total_hours": 4.5,
        "first_check_in": "2026-02-11T09:00:00Z",
        "last_check_out": null,
        "entries": [
            {
                "id": "uuid",
                "check_in": "2026-02-11T09:00:00Z",
                "check_out": null,
                "duration_hours": null
            }
        ]
    }
}
```

### Submit Attendance for Approval
**Intent Examples**: "submit my attendance", "send attendance for approval", "submit today's work"

```http
POST /attendance/submit
Authorization: Bearer <token>
```
> Submits today's attendance for manager approval. All check-ins must have check-outs.

### Get My Attendance History
**Intent Examples**: "my attendance history", "past attendance", "attendance records"

```http
GET /attendance/my?page=1&page_size=20&start_date=2026-02-01&end_date=2026-02-11
Authorization: Bearer <token>
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| page | int | Page number (default: 1) |
| page_size | int | Items per page (default: 20, max: 100) |
| start_date | date | Filter from date (YYYY-MM-DD) |
| end_date | date | Filter to date (YYYY-MM-DD) |

---

## 3. Leave Management

### Apply for Leave
**Intent Examples**: "apply for leave", "take sick leave", "request vacation", "need day off", "apply casual leave from X to Y"

```http
POST /leave/requests
Authorization: Bearer <token>
Content-Type: application/json

{
    "leave_type": "casual",
    "start_date": "2026-02-15",
    "end_date": "2026-02-16",
    "reason": "Personal work",
    "is_half_day": false,
    "emergency_contact": "John Doe",
    "emergency_phone": "+919876543210"
}
```

**Leave Types** (for `leave_type` field):
| Value | Description |
|-------|-------------|
| `sick` | Sick leave |
| `casual` | Casual leave |
| `annual` | Annual/earned leave |
| `unpaid` | Unpaid leave |
| `maternity` | Maternity leave |
| `paternity` | Paternity leave |
| `bereavement` | Bereavement leave |

**For Half-Day Leave**:
```json
{
    "leave_type": "casual",
    "start_date": "2026-02-15",
    "end_date": "2026-02-15",
    "reason": "Doctor appointment",
    "is_half_day": true,
    "half_day_type": "first_half"
}
```
> `half_day_type`: `"first_half"` or `"second_half"`

### Get My Leave Balance
**Intent Examples**: "my leave balance", "how many leaves left", "available leaves", "check leave balance"

```http
GET /leave/balance?year=2026
Authorization: Bearer <token>
```

**Response**:
```json
{
    "success": true,
    "data": [
        {
            "id": "uuid",
            "user_code": "5001",
            "leave_type": "casual",
            "year": 2026,
            "total_days": 12,
            "used_days": 2,
            "pending_days": 1,
            "available_days": 9
        },
        {
            "id": "uuid",
            "user_code": "5001",
            "leave_type": "sick",
            "year": 2026,
            "total_days": 10,
            "used_days": 0,
            "pending_days": 0,
            "available_days": 10
        }
    ]
}
```

### Get My Leave Requests
**Intent Examples**: "my leave requests", "leave history", "pending leave requests", "check leave status"

```http
GET /leave/requests?page=1&page_size=20&status=pending
Authorization: Bearer <token>
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| page | int | Page number |
| page_size | int | Items per page |
| status | string | `pending`, `approved_by_team_lead`, `approved`, `rejected`, `cancelled` |
| leave_type | string | Filter by leave type |

### Get Specific Leave Request
**Intent Examples**: "check leave request status", "view leave request"

```http
GET /leave/requests/{request_id}
Authorization: Bearer <token>
```

### Cancel Leave Request
**Intent Examples**: "cancel my leave", "withdraw leave request", "cancel leave application"

```http
POST /leave/requests/{request_id}/cancel
Authorization: Bearer <token>
```

---

## 4. Parking Management

### Allocate Parking (Get a Slot)
**Intent Examples**: "book parking", "need parking", "allocate parking slot", "park my car", "get parking spot"

```http
POST /parking/allocate
Authorization: Bearer <token>
```
> No request body needed - automatically assigns first available slot using user's vehicle info.

**Response**:
```json
{
    "success": true,
    "message": "Parking allocated successfully",
    "data": {
        "message": "Parking allocated successfully",
        "slot_code": "PRK-001",
        "vehicle_number": "GJ01EM5002",
        "vehicle_type": "car",
        "entry_time": "2026-02-11T10:30:00Z"
    }
}
```

**Note**: User must have `vehicle_number` in their profile. If not set, update profile first.

### Release Parking
**Intent Examples**: "release parking", "leaving parking", "exit parking", "free up parking slot"

```http
POST /parking/release
Authorization: Bearer <token>
```
> Automatically finds and releases user's active parking slot.

**Response**:
```json
{
    "success": true,
    "data": {
        "message": "Parking released successfully",
        "slot_code": "PRK-001",
        "vehicle_number": "GJ01EM5002",
        "entry_time": "2026-02-11T09:00:00Z",
        "exit_time": "2026-02-11T18:00:00Z",
        "duration_mins": 540
    }
}
```

### Check My Parking Status
**Intent Examples**: "my parking status", "where did I park", "do I have parking", "check my parking"

```http
GET /parking/my-slot
Authorization: Bearer <token>
```

**Response (with active parking)**:
```json
{
    "success": true,
    "data": {
        "has_active_parking": true,
        "slot": {
            "id": "uuid",
            "slot_code": "PRK-001"
        },
        "vehicle": {
            "vehicle_number": "GJ01EM5002",
            "vehicle_type": "car"
        },
        "entry_time": "2026-02-11T09:00:00Z"
    }
}
```

---

## 5. Desk Booking

### Book a Desk
**Intent Examples**: "book a desk", "reserve desk", "I need a desk", "book desk for tomorrow"

```http
POST /desks/bookings
Authorization: Bearer <token>
Content-Type: application/json

{
    "desk_id": "uuid-of-desk",
    "start_date": "2026-02-12",
    "end_date": "2026-02-12",
    "notes": "Near window preferred"
}
```

**Note**: First get available desks, then book by desk_id.

### List Available Desks
**Intent Examples**: "show available desks", "which desks are free", "list desks"

```http
GET /desks?status=available&is_active=true&page=1&page_size=20
Authorization: Bearer <token>
```

**Response**:
```json
{
    "success": true,
    "data": [
        {
            "id": "uuid",
            "desk_code": "DSK-0001",
            "desk_label": "Desk A1",
            "status": "available",
            "has_monitor": true,
            "has_docking_station": true,
            "is_active": true
        }
    ],
    "pagination": {
        "total": 50,
        "page": 1,
        "page_size": 20,
        "total_pages": 3
    }
}
```

### Get My Desk Bookings
**Intent Examples**: "my desk bookings", "show my booked desks", "desk reservations"

```http
GET /desks/bookings/my
Authorization: Bearer <token>
```

### Cancel Desk Booking
**Intent Examples**: "cancel desk booking", "cancel my desk reservation"

```http
POST /desks/bookings/{booking_id}/cancel
Authorization: Bearer <token>
```

---

## 6. Conference Room Booking

### List Conference Rooms
**Intent Examples**: "show conference rooms", "available meeting rooms", "list meeting rooms"

```http
GET /desks/rooms?is_active=true&page=1&page_size=20
Authorization: Bearer <token>
```

**Response**:
```json
{
    "success": true,
    "data": [
        {
            "id": "uuid",
            "room_code": "CONF-0001",
            "room_name": "Board Room",
            "capacity": 20,
            "has_projector": true,
            "has_video_conferencing": true,
            "has_whiteboard": true,
            "is_active": true
        }
    ]
}
```

### Book Conference Room
**Intent Examples**: "book meeting room", "reserve conference room", "need a meeting room for 10 people"

```http
POST /desks/rooms/bookings
Authorization: Bearer <token>
Content-Type: application/json

{
    "room_id": "uuid-of-room",
    "date": "2026-02-12",
    "start_time": "14:00",
    "end_time": "15:30",
    "title": "Team Standup",
    "attendees_count": 8,
    "notes": "Weekly sync meeting"
}
```

### Get My Conference Room Bookings
**Intent Examples**: "my meeting room bookings", "show my room reservations"

```http
GET /desks/rooms/bookings/my
Authorization: Bearer <token>
```

### Cancel Conference Room Booking
**Intent Examples**: "cancel meeting room", "cancel room booking"

```http
POST /desks/rooms/bookings/{booking_id}/cancel
Authorization: Bearer <token>
```

---

## 7. Food Orders

### Browse Menu / List Food Items
**Intent Examples**: "show menu", "what food is available", "list food items", "show lunch options"

```http
GET /food-orders/items?is_available=true&category=main_course&page=1&page_size=20
Authorization: Bearer <token>
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| category | string | Filter by category |
| is_available | bool | Show only available items |

**Response**:
```json
{
    "success": true,
    "data": [
        {
            "id": "uuid",
            "name": "Paneer Butter Masala",
            "description": "Creamy tomato-based curry with cottage cheese",
            "category_name": "Main Course",
            "price": 180.00,
            "is_available": true,
            "preparation_time_minutes": 20
        }
    ]
}
```

### Place Food Order
**Intent Examples**: "order food", "I want to order lunch", "place food order", "order paneer butter masala"

```http
POST /food-orders/orders
Authorization: Bearer <token>
Content-Type: application/json

{
    "items": [
        {
            "item_id": "uuid-of-item",
            "quantity": 2,
            "notes": "Less spicy"
        },
        {
            "item_id": "uuid-of-another-item",
            "quantity": 1
        }
    ],
    "delivery_notes": "Desk A12, 3rd floor",
    "scheduled_for": "2026-02-11T13:00:00Z"
}
```

### Get My Orders
**Intent Examples**: "my food orders", "order history", "check my order status"

```http
GET /food-orders/my-orders?page=1&page_size=20&status=pending
Authorization: Bearer <token>
```

**Order Statuses**:
| Status | Description |
|--------|-------------|
| `pending` | Order placed, not yet started |
| `preparing` | Being prepared |
| `ready` | Ready for pickup/delivery |
| `delivered` | Delivered |
| `cancelled` | Cancelled |

### Cancel Food Order
**Intent Examples**: "cancel my food order", "cancel lunch order"

```http
POST /food-orders/orders/{order_id}/cancel
Authorization: Bearer <token>
```

---

## 8. IT Requests

### Create IT Request
**Intent Examples**: "raise IT ticket", "IT support request", "my laptop is broken", "need software installed", "request new laptop"

```http
POST /it-requests
Authorization: Bearer <token>
Content-Type: application/json

{
    "request_type": "repair",
    "title": "Laptop screen flickering",
    "description": "My laptop screen has been flickering intermittently for the past 2 days. It happens especially when running multiple applications.",
    "priority": "medium",
    "related_asset_code": "LAP-0042"
}
```

**Request Types** (`request_type` field):
| Value | Use Case |
|-------|----------|
| `new_asset` | Request a new laptop/equipment |
| `repair` | Something is broken/not working |
| `REPLACEMENT` | Replace old/damaged equipment |
| `software_install` | Install new software |
| `access_request` | Request access to systems/tools |
| `network_issue` | WiFi, VPN, network problems |
| `other` | Anything else |

**Priority Levels**:
| Value | Description |
|-------|-------------|
| `low` | Can wait, minor issue |
| `medium` | Standard request (default) |
| `high` | Important, needs attention soon |
| `critical` | Urgent, blocking work |

### Get My IT Requests
**Intent Examples**: "my IT tickets", "IT request status", "check IT support requests"

```http
GET /it-requests?page=1&page_size=20&status=pending
Authorization: Bearer <token>
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | `pending`, `approved`, `in_progress`, `completed`, `rejected`, `cancelled` |
| request_type | string | Filter by request type |
| priority | string | Filter by priority |

### Get Specific IT Request
**Intent Examples**: "check ticket status", "view IT request"

```http
GET /it-requests/{request_id}
Authorization: Bearer <token>
```

---

## 9. Holidays

### List Holidays
**Intent Examples**: "show holidays", "upcoming holidays", "holiday list", "when is the next holiday"

```http
GET /holidays/list?upcoming_only=true&year=2026&page=1&page_size=50
Authorization: Bearer <token>
```

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| upcoming_only | bool | Show only future holidays (default: true) |
| year | int | Filter by year |

**Response**:
```json
{
    "success": true,
    "data": [
        {
            "id": "uuid",
            "name": "Republic Day",
            "description": "National holiday",
            "date": "2026-01-26",
            "holiday_type": "national",
            "is_optional": false
        },
        {
            "id": "uuid",
            "name": "Holi",
            "description": "Festival of colors",
            "date": "2026-03-10",
            "holiday_type": "festival",
            "is_optional": false
        }
    ]
}
```

---

## 10. User Profile

### Get My Profile
**Intent Examples**: "my profile", "show my details", "my information"

```http
GET /users/me
Authorization: Bearer <token>
```

**Response**:
```json
{
    "success": true,
    "data": {
        "id": "uuid",
        "user_code": "5001",
        "email": "employee@company.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+919876543210",
        "role": "employee",
        "department": "Engineering",
        "vehicle_number": "GJ01EM5002",
        "vehicle_type": "car",
        "is_active": true
    }
}
```

---

## 11. Natural Language Intent Mapping

Use this mapping to identify user intent and corresponding API calls:

### Attendance Intents
| User Says | API Call |
|-----------|----------|
| "check in", "I'm at office", "mark attendance", "punch in" | `POST /attendance/check-in` |
| "check out", "leaving office", "punch out", "going home" | `POST /attendance/check-out` |
| "attendance status", "am I checked in", "today's hours" | `GET /attendance/my-status` |
| "submit attendance", "send for approval" | `POST /attendance/submit` |
| "attendance history", "past attendance" | `GET /attendance/my` |

### Leave Intents
| User Says | API Call |
|-----------|----------|
| "apply leave", "take leave", "need time off" | `POST /leave/requests` |
| "sick leave for tomorrow" | `POST /leave/requests` with `leave_type: "sick"` |
| "half day today" | `POST /leave/requests` with `is_half_day: true` |
| "leave balance", "how many leaves left" | `GET /leave/balance` |
| "my leave requests", "pending leaves" | `GET /leave/requests` |
| "cancel leave" | `POST /leave/requests/{id}/cancel` |

### Parking Intents
| User Says | API Call |
|-----------|----------|
| "book parking", "need parking", "park my car" | `POST /parking/allocate` |
| "release parking", "exit parking", "leaving" | `POST /parking/release` |
| "where is my car", "my parking slot" | `GET /parking/my-slot` |

### Desk/Room Intents
| User Says | API Call |
|-----------|----------|
| "book desk", "reserve desk", "I need a desk" | `POST /desks/bookings` |
| "available desks", "show free desks" | `GET /desks?status=available` |
| "my desk bookings" | `GET /desks/bookings/my` |
| "book meeting room", "conference room" | `POST /desks/rooms/bookings` |
| "available meeting rooms" | `GET /desks/rooms` |
| "cancel desk/room booking" | `POST /desks/bookings/{id}/cancel` |

### Food Intents
| User Says | API Call |
|-----------|----------|
| "show menu", "what's for lunch" | `GET /food-orders/items` |
| "order food", "I want to eat" | `POST /food-orders/orders` |
| "my orders", "order status" | `GET /food-orders/my-orders` |
| "cancel food order" | `POST /food-orders/orders/{id}/cancel` |

### IT Support Intents
| User Says | API Call |
|-----------|----------|
| "raise IT ticket", "IT help", "laptop broken" | `POST /it-requests` |
| "install software" | `POST /it-requests` with `request_type: "software_install"` |
| "network not working", "WiFi issue" | `POST /it-requests` with `request_type: "network_issue"` |
| "need new laptop" | `POST /it-requests` with `request_type: "new_asset"` |
| "my IT tickets", "ticket status" | `GET /it-requests` |

### General Intents
| User Says | API Call |
|-----------|----------|
| "holiday list", "upcoming holidays" | `GET /holidays/list` |
| "my profile", "my details" | `GET /users/me` |
| "change password" | `POST /auth/change-password` |

---

## 📝 Common Response Format

All API responses follow this structure:

**Success Response**:
```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": { ... }
}
```

**Paginated Response**:
```json
{
    "success": true,
    "message": "Records retrieved successfully",
    "data": [ ... ],
    "pagination": {
        "total": 100,
        "page": 1,
        "page_size": 20,
        "total_pages": 5
    }
}
```

**Error Response**:
```json
{
    "success": false,
    "message": "Error message",
    "detail": "Detailed error description"
}
```

---

## ⚠️ Error Handling

| HTTP Code | Meaning | Agent Action |
|-----------|---------|--------------|
| 400 | Bad Request | Check request body, inform user of validation error |
| 401 | Unauthorized | Token expired, need to re-login |
| 403 | Forbidden | User doesn't have permission for this action |
| 404 | Not Found | Resource doesn't exist, inform user |
| 500 | Server Error | Retry once, then inform user of technical issue |

---

## 🔑 Agent Workflow Example

**User**: "I want to apply for sick leave tomorrow"

**Agent Steps**:
1. Extract intent: `apply_leave`
2. Extract entities: `leave_type=sick`, `date=tomorrow`
3. Calculate dates: `start_date=2026-02-12`, `end_date=2026-02-12`
4. Call API:
```http
POST /leave/requests
{
    "leave_type": "sick",
    "start_date": "2026-02-12",
    "end_date": "2026-02-12",
    "reason": "Not feeling well"
}
```
5. Return response to user: "Your sick leave for February 12, 2026 has been applied and is pending approval."

---

*Last Updated: February 11, 2026*
