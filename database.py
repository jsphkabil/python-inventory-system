"""
SQLite database module for the IT Help Room Inventory Tracker.
Handles all database operations including initialization, CRUD operations.
"""

import uuid

import sqlite3
from pathlib import Path
from typing import Optional

from collections import defaultdict

# Database file path
DB_PATH = Path(__file__).parent / "inventory.db"


def get_connection() -> sqlite3.Connection:
    """Get a database connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize the database with tables and seed data."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create locations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS locations (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)
    
    # Create inventory table
    # changed to add item information
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            count INTEGER NOT NULL DEFAULT 0,
            deployable INTEGER NOT NULL DEFAULT 0,
            low_count INTEGER NOT NULL DEFAULT 0,
            location_id TEXT NOT NULL,
            FOREIGN KEY (location_id) REFERENCES locations(id)
        )
    """)

    # changed to add item information
    cursor.execute("PRAGMA table_info(inventory)")
    columns = [row[1] for row in cursor.fetchall()]

    if "deployable" not in columns:
        cursor.execute("ALTER TABLE inventory ADD COLUMN deployable INTEGER NOT NULL DEFAULT 0")

    if "low_count" not in columns:
        cursor.execute("ALTER TABLE inventory ADD COLUMN low_count INTEGER")
    
    # Check if locations table is empty, if so seed it
    cursor.execute("SELECT COUNT(*) FROM locations")
    if cursor.fetchone()[0] == 0:
        seed_locations(cursor)
        seed_inventory(cursor)
    
    conn.commit()
    conn.close()


def seed_locations(cursor: sqlite3.Cursor):
    """Seed the locations table with initial data."""
    locations = [
        ('helpdesk', 'Help Desk'),
        ('storage', 'Storage Room'),
        ('lab1', 'Computer Lab 1'),
        ('lab2', 'Computer Lab 2'),
        ('server', 'Server Room'),
    ]
    cursor.executemany("INSERT INTO locations (id, name) VALUES (?, ?)", locations)


def seed_inventory(cursor: sqlite3.Cursor):
    """Seed the inventory table with initial data."""
    items = [
        # Help Desk items
        ('Wireless Mouse', 15, 'helpdesk'),
        ('USB Keyboard', 12, 'helpdesk'),
        ('HDMI Cable (6ft)', 8, 'helpdesk'),
        ('USB-C Charger', 10, 'helpdesk'),
        ('Laptop Bag', 5, 'helpdesk'),
        
        # Storage Room items
        ('Dell Monitor 24"', 20, 'storage'),
        ('HP Monitor 27"', 15, 'storage'),
        ('Ethernet Cable (25ft)', 30, 'storage'),
        ('Power Strip 6-outlet', 18, 'storage'),
        ('Extension Cord', 12, 'storage'),
        
        # Computer Lab 1 items
        ('Wireless Adapter', 25, 'lab1'),
        ('Webcam HD', 8, 'lab1'),
        ('Headset with Microphone', 10, 'lab1'),
        ('USB Hub 4-port', 6, 'lab1'),
        
        # Computer Lab 2 items
        ('VGA Cable', 14, 'lab2'),
        ('DVI Cable', 10, 'lab2'),
        ('Display Port Cable', 8, 'lab2'),
        ('Laptop Stand', 12, 'lab2'),
        
        # Server Room items
        ('Cat6 Ethernet Cable (3ft)', 50, 'server'),
        ('Network Switch 24-port', 4, 'server'),
        ('Rack Mount Kit', 6, 'server'),
        ('UPS Battery Backup', 8, 'server'),
        ('Server Rails', 10, 'server'),
    ]

    # changed to add item information
    cursor.executemany(
        """
        INSERT INTO inventory (name, count, deployable, low_count, location_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        [(name, count, 1, None, location) for (name, count, location) in items]
    )


# Location operations
def get_all_locations() -> list[dict]:
    """Get all locations from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM locations ORDER BY name")
    locations = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return locations


# Inventory operations
def get_all_items(location_id: Optional[str] = None, search_query: str = "") -> list[dict]:
    """Get inventory items, optionally filtered by location and search query."""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT i.id, i.name, i.count,
               i.deployable, i.low_count,
               i.location_id, l.name as location_name
        FROM inventory i
        JOIN locations l ON i.location_id = l.id
        WHERE 1=1
    """
    params = []
    
    if location_id and location_id != "all":
        query += " AND i.location_id = ?"
        params.append(location_id)
    
    if search_query:
        query += " AND LOWER(i.name) LIKE LOWER(?)"
        params.append(f"%{search_query}%")
    
    query += " ORDER BY i.name"
    
    cursor.execute(query, params)
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return items


def get_item_by_id(item_id: int) -> Optional[dict]:
    """Get a single item by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.id, i.name, i.count,
               i.deployable, i.low_count,
               i.location_id, l.name as location_name
        FROM inventory i
        JOIN locations l ON i.location_id = l.id
        WHERE i.id = ?
    """, (item_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


# changed to add item information
def add_item(name: str, count: int, location_id: str,
             deployable: bool = False,
             low_count: int = 0) -> int:
    """Add a new item to the inventory. Returns the new item's ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO inventory (name, count, deployable, low_count, location_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, count, int(deployable), low_count, location_id)
    )
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


### 'Update Item' function to work in conjuction with new 'Edit Item' feature in GUI
# changed to add item information
def update_item(item_id: int, name: str, count: int, location_id: str,
                deployable: bool, low_count: Optional[int]):
    """Update item's name, count, and location"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE inventory
        SET name = ?, count = ?, deployable = ?, low_count = ?, location_id = ?
        WHERE id = ?
    """, (name, max(0, count), int(deployable), low_count, location_id, item_id)
    )
    conn.commit()
    conn.close()


def update_item_count(item_id: int, new_count: int):
    """Update the count of an item."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE inventory SET count = ? WHERE id = ?",
        (max(0, new_count), item_id)
    )
    conn.commit()
    conn.close()


def delete_item(item_id: int):
    """Delete an item from the inventory."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()


def deploy_items(deployments: list[tuple[int, int]]):
    """
    Deploy items (subtract quantities from multiple items).
    deployments: list of (item_id, quantity) tuples
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    for item_id, quantity in deployments:
        cursor.execute(
            "UPDATE inventory SET count = MAX(0, count - ?) WHERE id = ?",
            (quantity, item_id)
        )
    
    conn.commit()
    conn.close()


### Function to add a location. Returns new location ID
def add_location(name: str) -> str:
    conn = get_connection()
    cursor = conn.cursor()

    import uuid
    location_id = str(uuid.uuid4())

    cursor.execute(
        "INSERT INTO locations (id, name) VALUES (?, ?)",
        (location_id, name)
    )

    conn.commit()
    conn.close()
    return location_id


### Function to delete a location
def delete_location(location_id: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM inventory WHERE location_id = ?",
        (location_id,)
    )
    item_count = cursor.fetchone()[0]

    if item_count > 0:
        conn.close()
        raise Exception("Cannot delete location that still has items.")
    
    cursor.execute(
        "DELETE FROM locations WHERE id = ?",
        (location_id,)
    )

    conn.commit()
    conn.close()


### Function to update a location
def update_location(location_id: str, new_name: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "Update locations SET name = ? WHERE id = ?",
        (new_name, location_id)
    )
    
    conn.commit()
    conn.close()


def get_location_summary() -> list[dict]:
    """Get summary statistics for each location."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            l.id,
            l.name,
            COUNT(i.id) as item_count,
            COALESCE(SUM(i.count), 0) as total_count
        FROM locations l
        LEFT JOIN inventory i ON l.id = i.location_id
        GROUP BY l.id, l.name
        ORDER BY l.name
    """)
    summary = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return summary

### Functions to change summary section from displaying total item count to low stock item count
def get_low_item_list() -> list[dict]:
    """Get complete list of low stock items"""
    items = get_all_items()
    low_items = []

    for item in items:
        if item["low_count"] is not None:
            if item["count"] <= item["low_count"]:
                low_items.append(item)
        else:
            if item["count"] == 0:
                low_items.append(item)

    return low_items

def get_low_item_location_summary() -> list[dict]:
    """Get summary statistics for low sock items in each locations"""
    low_items = get_low_item_list()
    summary_dict = defaultdict(lambda: {"item_count": 0, "total_count": 0})

    for item in low_items:
        loc_id = item["location_id"]
        loc_name = item["location_name"]

        summary_dict[loc_id]["name"] = loc_name
        summary_dict[loc_id]["item_count"] += 1
        summary_dict[loc_id]["total_count"] += item["count"]

    summary = []
    for loc_id, data in summary_dict.items():
        summary.append({
            "id": loc_id,
            "name": data["name"],
            "item_count": data["item_count"],
            "total_count": data["total_count"]
        })

    summary.sort(key=lambda x: x["name"])
    return summary

