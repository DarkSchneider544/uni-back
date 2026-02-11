"""
Seed data script for initial setup.
Creates managers with ManagerType, employees, desks, parking slots, cafeteria tables, and IT assets.

Run with: python -m scripts.seed_data
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.desk import Desk, ConferenceRoom
from app.models.parking import ParkingSlot
from app.models.cafeteria import CafeteriaTable
from app.models.food import FoodItem
from app.models.it_asset import ITAsset
from app.models.enums import (
    UserRole, ManagerType, AssetType, AssetStatus,
    DeskStatus, ParkingSlotStatus, VehicleType, ParkingType
)
from decimal import Decimal
import random


async def seed_users(db: AsyncSession):
    """
    Seed initial users:
    - 1 Super Admin
    - 1 Admin
    - 5 Managers (one for each ManagerType)
    - 2 Team Leads
    - 5 Employees
    """
    users = [
        # Super Admin
        {
            "user_code": "1001",
            "email": "super.admin@company.com",
            "password": "Admin@123",
            "first_name": "Super",
            "last_name": "Admin",
            "role": UserRole.SUPER_ADMIN,
            "manager_type": None,
            "department": "Administration",
            "vehicle_number": "GJ01SA1001",
            "vehicle_type": VehicleType.CAR
        },
        # Admin
        {
            "user_code": "2001",
            "email": "admin@company.com",
            "password": "Admin@123",
            "first_name": "System",
            "last_name": "Admin",
            "role": UserRole.ADMIN,
            "manager_type": None,
            "department": "Administration",
            "vehicle_number": "GJ01AD2001",
            "vehicle_type": VehicleType.CAR
        },
        # Parking Manager
        {
            "user_code": "3001",
            "email": "parking.manager@company.com",
            "password": "Manager@123",
            "first_name": "Rajesh",
            "last_name": "Kumar",
            "role": UserRole.MANAGER,
            "manager_type": ManagerType.PARKING,
            "department": "Facilities",
            "vehicle_number": "GJ01PM3001",
            "vehicle_type": VehicleType.CAR
        },
        # Attendance Manager
        {
            "user_code": "3002",
            "email": "attendance.manager@company.com",
            "password": "Manager@123",
            "first_name": "Priya",
            "last_name": "Sharma",
            "role": UserRole.MANAGER,
            "manager_type": ManagerType.ATTENDANCE,
            "department": "HR",
            "vehicle_number": "GJ01AM3002",
            "vehicle_type": VehicleType.CAR
        },
        # Desk & Conference Manager
        {
            "user_code": "3003",
            "email": "desk.manager@company.com",
            "password": "Manager@123",
            "first_name": "Amit",
            "last_name": "Patel",
            "role": UserRole.MANAGER,
            "manager_type": ManagerType.DESK_CONFERENCE,
            "department": "Facilities",
            "vehicle_number": "GJ01DM3003",
            "vehicle_type": VehicleType.CAR
        },
        # Cafeteria Manager
        {
            "user_code": "3004",
            "email": "cafeteria.manager@company.com",
            "password": "Manager@123",
            "first_name": "Sunita",
            "last_name": "Gupta",
            "role": UserRole.MANAGER,
            "manager_type": ManagerType.CAFETERIA,
            "department": "Food Services",
            "vehicle_number": "GJ01CM3004",
            "vehicle_type": VehicleType.CAR
        },
        # IT Support Manager
        {
            "user_code": "3005",
            "email": "it.manager@company.com",
            "password": "Manager@123",
            "first_name": "Vikram",
            "last_name": "Singh",
            "role": UserRole.MANAGER,
            "manager_type": ManagerType.IT_SUPPORT,
            "department": "IT",
            "vehicle_number": "GJ01IT3005",
            "vehicle_type": VehicleType.CAR
        },
        # Team Leads
        {
            "user_code": "4001",
            "email": "dev.teamlead@company.com",
            "password": "TeamLead@123",
            "first_name": "Ravi",
            "last_name": "Verma",
            "role": UserRole.TEAM_LEAD,
            "manager_type": None,
            "department": "Development",
            "vehicle_number": "GJ01TL4001",
            "vehicle_type": VehicleType.CAR
        },
        {
            "user_code": "4002",
            "email": "sales.teamlead@company.com",
            "password": "TeamLead@123",
            "first_name": "Anita",
            "last_name": "Desai",
            "role": UserRole.TEAM_LEAD,
            "manager_type": None,
            "department": "Sales",
            "vehicle_number": "GJ01TL4002",
            "vehicle_type": VehicleType.CAR
        },
        # Employees
        {
            "user_code": "5001",
            "email": "employee1@company.com",
            "password": "Employee@123",
            "first_name": "Alice",
            "last_name": "Johnson",
            "role": UserRole.EMPLOYEE,
            "manager_type": None,
            "department": "Development",
            "vehicle_number": "GJ01EM5001",
            "vehicle_type": VehicleType.CAR
        },
        {
            "user_code": "5002",
            "email": "employee2@company.com",
            "password": "Employee@123",
            "first_name": "Bob",
            "last_name": "Smith",
            "role": UserRole.EMPLOYEE,
            "manager_type": None,
            "department": "Development",
            "vehicle_number": "GJ01EM5002",
            "vehicle_type": VehicleType.CAR
        },
        {
            "user_code": "5003",
            "email": "employee3@company.com",
            "password": "Employee@123",
            "first_name": "Charlie",
            "last_name": "Brown",
            "role": UserRole.EMPLOYEE,
            "manager_type": None,
            "department": "Sales",
            "vehicle_number": "GJ01EM5003",
            "vehicle_type": VehicleType.CAR
        },
        {
            "user_code": "5004",
            "email": "employee4@company.com",
            "password": "Employee@123",
            "first_name": "Diana",
            "last_name": "Williams",
            "role": UserRole.EMPLOYEE,
            "manager_type": None,
            "department": "HR",
            "vehicle_number": "GJ01EM5004",
            "vehicle_type": VehicleType.CAR
        },
        {
            "user_code": "5005",
            "email": "employee5@company.com",
            "password": "Employee@123",
            "first_name": "Ethan",
            "last_name": "Davis",
            "role": UserRole.EMPLOYEE,
            "manager_type": None,
            "department": "IT",
            "vehicle_number": "GJ01EM5005",
            "vehicle_type": VehicleType.CAR
        },
    ]
    
    created_users = []
    for user_data in users:
        # Check if user already exists
        result = await db.execute(
            select(User).where(User.email == user_data["email"])
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"  User already exists: {user_data['email']}")
            created_users.append(existing)
            continue
        
        user = User(
            user_code=user_data["user_code"],
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            role=user_data["role"],
            manager_type=user_data.get("manager_type"),
            department=user_data.get("department"),
            vehicle_number=user_data["vehicle_number"],
            vehicle_type=user_data.get("vehicle_type", VehicleType.CAR),
            is_active=True
        )
        db.add(user)
        created_users.append(user)
        print(f"  Created user: {user_data['email']} (Code: {user_data['user_code']}, Role: {user_data['role'].value})")
    
    await db.commit()
    return created_users


async def seed_desks(db: AsyncSession, users: list):
    """
    Seed sample desks (10 desks with auto-generated DSK-XXXX codes).
    """
    # Find desk manager
    desk_manager = next((u for u in users if u.manager_type == ManagerType.DESK_CONFERENCE), users[0])
    
    # Check existing count
    result = await db.execute(select(Desk))
    existing_desks = result.scalars().all()
    if len(existing_desks) >= 10:
        print(f"  Desks already seeded ({len(existing_desks)} desks)")
        return
    
    desk_labels = [
        "Window Desk A1", "Window Desk A2", "Window Desk A3",
        "Corner Desk B1", "Corner Desk B2",
        "Open Area C1", "Open Area C2", "Open Area C3",
        "Quiet Zone D1", "Quiet Zone D2"
    ]
    
    for i, label in enumerate(desk_labels):
        desk_code = f"DSK-{random.randint(1000, 9999)}"
        
        desk = Desk(
            desk_code=desk_code,
            desk_label=label,
            status=DeskStatus.AVAILABLE,
            has_monitor=random.choice([True, False]),
            has_docking_station=random.choice([True, False]),
            notes=f"Desk {i+1} of 10 - auto-seeded",
            is_active=True,
            created_by_code=desk_manager.user_code
        )
        db.add(desk)
        print(f"  Created desk: {desk_code} - {label}")
    
    await db.commit()


async def seed_conference_rooms(db: AsyncSession, users: list):
    """
    Seed sample conference rooms (5 rooms with auto-generated CNF-XXXX codes).
    """
    # Find desk manager
    desk_manager = next((u for u in users if u.manager_type == ManagerType.DESK_CONFERENCE), users[0])
    
    # Check existing count
    result = await db.execute(select(ConferenceRoom))
    existing_rooms = result.scalars().all()
    if len(existing_rooms) >= 5:
        print(f"  Conference rooms already seeded ({len(existing_rooms)} rooms)")
        return
    
    rooms = [
        {"label": "Board Room", "capacity": 20, "has_projector": True, "has_whiteboard": True, "has_video_conferencing": True},
        {"label": "Meeting Room Alpha", "capacity": 8, "has_projector": True, "has_whiteboard": True, "has_video_conferencing": True},
        {"label": "Meeting Room Beta", "capacity": 6, "has_projector": False, "has_whiteboard": True, "has_video_conferencing": False},
        {"label": "Huddle Space 1", "capacity": 4, "has_projector": False, "has_whiteboard": False, "has_video_conferencing": False},
        {"label": "Interview Room", "capacity": 3, "has_projector": False, "has_whiteboard": True, "has_video_conferencing": True},
    ]
    
    for room_data in rooms:
        room_code = f"CNF-{random.randint(1000, 9999)}"
        
        room = ConferenceRoom(
            room_code=room_code,
            room_label=room_data["label"],
            capacity=room_data["capacity"],
            has_projector=room_data["has_projector"],
            has_whiteboard=room_data["has_whiteboard"],
            has_video_conferencing=room_data["has_video_conferencing"],
            notes=f"Conference room - auto-seeded",
            is_active=True,
            created_by_code=desk_manager.user_code
        )
        db.add(room)
        print(f"  Created conference room: {room_code} - {room_data['label']} (capacity: {room_data['capacity']})")
    
    await db.commit()


async def seed_parking_slots(db: AsyncSession, users: list):
    """
    Seed sample parking slots (15 slots with auto-generated PKG-XXXX codes).
    """
    # Find parking manager
    parking_manager = next((u for u in users if u.manager_type == ManagerType.PARKING), users[0])
    
    # Check existing count
    result = await db.execute(select(ParkingSlot))
    existing_slots = result.scalars().all()
    if len(existing_slots) >= 15:
        print(f"  Parking slots already seeded ({len(existing_slots)} slots)")
        return
    
    # Employee slots (10)
    employee_slots = [
        {"label": "Employee A1", "vehicle_type": VehicleType.CAR, "parking_type": ParkingType.EMPLOYEE},
        {"label": "Employee A2", "vehicle_type": VehicleType.CAR, "parking_type": ParkingType.EMPLOYEE},
        {"label": "Employee A3", "vehicle_type": VehicleType.CAR, "parking_type": ParkingType.EMPLOYEE},
        {"label": "Employee B1", "vehicle_type": VehicleType.CAR, "parking_type": ParkingType.EMPLOYEE},
        {"label": "Employee B2", "vehicle_type": VehicleType.CAR, "parking_type": ParkingType.EMPLOYEE},
        {"label": "Bike Bay 1", "vehicle_type": VehicleType.BIKE, "parking_type": ParkingType.EMPLOYEE},
        {"label": "Bike Bay 2", "vehicle_type": VehicleType.BIKE, "parking_type": ParkingType.EMPLOYEE},
        {"label": "Bike Bay 3", "vehicle_type": VehicleType.BIKE, "parking_type": ParkingType.EMPLOYEE},
        {"label": "Bike Bay 4", "vehicle_type": VehicleType.BIKE, "parking_type": ParkingType.EMPLOYEE},
        {"label": "Bike Bay 5", "vehicle_type": VehicleType.BIKE, "parking_type": ParkingType.EMPLOYEE},
    ]
    
    # Visitor slots (5)
    visitor_slots = [
        {"label": "Visitor V1", "vehicle_type": VehicleType.CAR, "parking_type": ParkingType.VISITOR},
        {"label": "Visitor V2", "vehicle_type": VehicleType.CAR, "parking_type": ParkingType.VISITOR},
        {"label": "Visitor V3", "vehicle_type": VehicleType.CAR, "parking_type": ParkingType.VISITOR},
        {"label": "Visitor Bike 1", "vehicle_type": VehicleType.BIKE, "parking_type": ParkingType.VISITOR},
        {"label": "Visitor Bike 2", "vehicle_type": VehicleType.BIKE, "parking_type": ParkingType.VISITOR},
    ]
    
    all_slots = employee_slots + visitor_slots
    
    for slot_data in all_slots:
        slot_code = f"PKG-{random.randint(1000, 9999)}"
        
        slot = ParkingSlot(
            slot_code=slot_code,
            slot_label=slot_data["label"],
            parking_type=slot_data["parking_type"],
            vehicle_type=slot_data["vehicle_type"],
            status=ParkingSlotStatus.AVAILABLE,
            notes=f"Parking slot - auto-seeded",
            is_active=True,
            created_by_code=parking_manager.user_code
        )
        db.add(slot)
        print(f"  Created parking slot: {slot_code} - {slot_data['label']} ({slot_data['parking_type'].value})")
    
    await db.commit()


async def seed_cafeteria_tables(db: AsyncSession, users: list):
    """
    Seed sample cafeteria tables (8 tables with auto-generated TBL-XXXX codes).
    """
    # Find cafeteria manager
    cafeteria_manager = next((u for u in users if u.manager_type == ManagerType.CAFETERIA), users[0])
    
    # Check existing count
    result = await db.execute(select(CafeteriaTable))
    existing_tables = result.scalars().all()
    if len(existing_tables) >= 8:
        print(f"  Cafeteria tables already seeded ({len(existing_tables)} tables)")
        return
    
    tables = [
        {"label": "Window Table 1", "capacity": 4, "table_type": "regular"},
        {"label": "Window Table 2", "capacity": 4, "table_type": "regular"},
        {"label": "Center Table 1", "capacity": 6, "table_type": "large"},
        {"label": "Center Table 2", "capacity": 6, "table_type": "large"},
        {"label": "Round Table 1", "capacity": 8, "table_type": "round"},
        {"label": "Round Table 2", "capacity": 8, "table_type": "round"},
        {"label": "High Top 1", "capacity": 2, "table_type": "high"},
        {"label": "High Top 2", "capacity": 2, "table_type": "high"},
    ]
    
    for table_data in tables:
        table_code = f"TBL-{random.randint(1000, 9999)}"
        
        table = CafeteriaTable(
            table_code=table_code,
            table_label=table_data["label"],
            capacity=table_data["capacity"],
            table_type=table_data["table_type"],
            notes=f"Cafeteria table - auto-seeded",
            is_active=True,
            created_by_code=cafeteria_manager.user_code
        )
        db.add(table)
        print(f"  Created cafeteria table: {table_code} - {table_data['label']} (capacity: {table_data['capacity']})")
    
    await db.commit()


async def seed_food_items(db: AsyncSession, users: list):
    """Seed sample food items."""
    # Find cafeteria manager
    cafeteria_manager = next((u for u in users if u.manager_type == ManagerType.CAFETERIA), users[0])
    
    food_items = [
        {"name": "Butter Chicken", "description": "Creamy tomato-based curry with tender chicken", "price": Decimal("12.99"), "category": "Main Course", "tags": ["non-veg", "spicy"], "calories": 450},
        {"name": "Paneer Tikka", "description": "Grilled cottage cheese with spices", "price": Decimal("9.99"), "category": "Starters", "tags": ["vegetarian", "high-protein"], "calories": 280},
        {"name": "Masala Dosa", "description": "Crispy rice crepe with potato filling", "price": Decimal("7.99"), "category": "South Indian", "tags": ["vegetarian", "vegan"], "calories": 320},
        {"name": "Chicken Biryani", "description": "Aromatic basmati rice with spiced chicken", "price": Decimal("14.99"), "category": "Main Course", "tags": ["non-veg", "spicy"], "calories": 520},
        {"name": "Dal Makhani", "description": "Creamy black lentils slow-cooked", "price": Decimal("8.99"), "category": "Main Course", "tags": ["vegetarian"], "calories": 350},
        {"name": "Mango Lassi", "description": "Sweet mango yogurt drink", "price": Decimal("3.99"), "category": "Beverages", "tags": ["vegetarian", "sweet"], "calories": 180},
        {"name": "Coffee", "description": "Fresh brewed hot coffee", "price": Decimal("2.49"), "category": "Beverages", "tags": ["vegetarian", "vegan"], "calories": 5},
        {"name": "Tea", "description": "Hot brewed masala chai", "price": Decimal("1.99"), "category": "Beverages", "tags": ["vegetarian", "vegan"], "calories": 25},
        {"name": "Veg Sandwich", "description": "Fresh vegetable grilled sandwich", "price": Decimal("4.99"), "category": "Snacks", "tags": ["vegetarian", "healthy"], "calories": 250},
        {"name": "Samosa", "description": "Crispy fried pastry with potato filling", "price": Decimal("2.99"), "category": "Snacks", "tags": ["vegetarian", "spicy"], "calories": 150},
    ]
    
    for item_data in food_items:
        result = await db.execute(
            select(FoodItem).where(FoodItem.name == item_data["name"])
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"  Food item already exists: {item_data['name']}")
            continue
        
        item = FoodItem(
            name=item_data["name"],
            description=item_data["description"],
            price=item_data["price"],
            category_name=item_data["category"],
            tags=item_data["tags"],
            calories=item_data["calories"],
            is_available=True,
            is_active=True,
            created_by_code=cafeteria_manager.user_code
        )
        db.add(item)
        print(f"  Created food item: {item_data['name']} (₹{item_data['price']})")
    
    await db.commit()


async def seed_it_assets(db: AsyncSession, users: list):
    """Seed sample IT assets."""
    # Find IT manager
    it_manager = next((u for u in users if u.manager_type == ManagerType.IT_SUPPORT), users[0])
    
    assets = [
        {"asset_code": "IT-LAP-001", "name": "Dell Latitude 5520", "asset_type": AssetType.LAPTOP, "serial_number": "DELL-LAP-001", "model": "Latitude 5520", "vendor": "Dell"},
        {"asset_code": "IT-LAP-002", "name": "Dell Latitude 5520", "asset_type": AssetType.LAPTOP, "serial_number": "DELL-LAP-002", "model": "Latitude 5520", "vendor": "Dell"},
        {"asset_code": "IT-LAP-003", "name": "MacBook Pro 14", "asset_type": AssetType.LAPTOP, "serial_number": "APPLE-MAC-001", "model": "MacBook Pro 14", "vendor": "Apple"},
        {"asset_code": "IT-MON-001", "name": "HP Monitor 24", "asset_type": AssetType.MONITOR, "serial_number": "HP-MON-001", "model": "HP E24", "vendor": "HP"},
        {"asset_code": "IT-MON-002", "name": "HP Monitor 24", "asset_type": AssetType.MONITOR, "serial_number": "HP-MON-002", "model": "HP E24", "vendor": "HP"},
        {"asset_code": "IT-MON-003", "name": "Dell Monitor 27", "asset_type": AssetType.MONITOR, "serial_number": "DELL-MON-001", "model": "Dell U2722D", "vendor": "Dell"},
        {"asset_code": "IT-KB-001", "name": "Logitech Keyboard", "asset_type": AssetType.KEYBOARD, "serial_number": "LOG-KB-001", "model": "K120", "vendor": "Logitech"},
        {"asset_code": "IT-KB-002", "name": "Logitech Keyboard", "asset_type": AssetType.KEYBOARD, "serial_number": "LOG-KB-002", "model": "K120", "vendor": "Logitech"},
        {"asset_code": "IT-MS-001", "name": "Logitech Mouse", "asset_type": AssetType.MOUSE, "serial_number": "LOG-MS-001", "model": "M100", "vendor": "Logitech"},
        {"asset_code": "IT-MS-002", "name": "Logitech Mouse", "asset_type": AssetType.MOUSE, "serial_number": "LOG-MS-002", "model": "M100", "vendor": "Logitech"},
    ]
    
    for asset_data in assets:
        result = await db.execute(
            select(ITAsset).where(ITAsset.serial_number == asset_data["serial_number"])
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"  IT asset already exists: {asset_data['serial_number']}")
            continue
        
        asset = ITAsset(
            asset_code=asset_data["asset_code"],
            name=asset_data["name"],
            asset_type=asset_data["asset_type"],
            serial_number=asset_data["serial_number"],
            model=asset_data["model"],
            vendor=asset_data["vendor"],
            status=AssetStatus.AVAILABLE,
            is_active=True
        )
        db.add(asset)
        print(f"  Created IT asset: {asset_data['asset_code']} - {asset_data['name']}")
    
    await db.commit()


async def main():
    """Main seed function."""
    print("\n" + "=" * 60)
    print("  UNIFIED OFFICE MANAGEMENT - SEED DATA")
    print("  New ManagerType-Based System")
    print("=" * 60 + "\n")
    
    async with AsyncSessionLocal() as db:
        try:
            print("1. Creating users...")
            users = await seed_users(db)
            
            print("\n2. Creating desks...")
            await seed_desks(db, users)
            
            print("\n3. Creating conference rooms...")
            await seed_conference_rooms(db, users)
            
            print("\n4. Creating parking slots...")
            await seed_parking_slots(db, users)
            
            print("\n5. Creating cafeteria tables...")
            await seed_cafeteria_tables(db, users)
            
            print("\n6. Creating food items...")
            await seed_food_items(db, users)
            
            print("\n7. Creating IT assets...")
            await seed_it_assets(db, users)
            
            print("\n" + "=" * 60)
            print("  SEED DATA COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print("\n" + "-" * 60)
            print("  DEFAULT CREDENTIALS")
            print("-" * 60)
            print("\n  SUPER ADMIN:")
            print("    Email: super.admin@company.com")
            print("    Password: Admin@123")
            print("\n  ADMIN:")
            print("    Email: admin@company.com")
            print("    Password: Admin@123")
            print("\n  MANAGERS (Password: Manager@123):")
            print("    Parking:     parking.manager@company.com")
            print("    Attendance:  attendance.manager@company.com")
            print("    Desk:        desk.manager@company.com")
            print("    Cafeteria:   cafeteria.manager@company.com")
            print("    IT Support:  it.manager@company.com")
            print("\n  TEAM LEADS (Password: TeamLead@123):")
            print("    Development: dev.teamlead@company.com")
            print("    Sales:       sales.teamlead@company.com")
            print("\n  EMPLOYEES (Password: Employee@123):")
            print("    employee1@company.com to employee5@company.com")
            print("\n" + "-" * 60)
            
        except Exception as e:
            print(f"\nError during seeding: {e}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(main())
