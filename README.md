# IT Help Room Inventory Tracker (Python)

A desktop application for tracking IT equipment across multiple locations, built with Python, Tkinter, and SQLite.

## Features

- **View Inventory**: Browse all items with search and location filtering
- **Update Counts**: Use +/- buttons or type directly to update item quantities
- **Add Items**: Add new items to any location
- **Delete Items**: Remove items from inventory with confirmation
- **Deploy Computer**: Subtract multiple items at once when setting up a new computer
- **Summary Stats**: View total counts per location at a glance

## Upcoming Features
- Item History
- Create Report
- Expected Count (Number of each item we want at least)
- Low Item Report
- Auto-refresh

## Requirements

- Python 3.10 or higher
- No additional packages required (uses only standard library)

## Running the Application

```bash
python inventory_app.py
```

## Detailed Instructions
On GitHub repo click green 'Code' button > Download ZIP > Unzip > Type and enter 'cmd' in address bar(while in the folder path) >
In terminal enter 'python inventory_app.py'

## Database

The application uses SQLite and automatically creates an `inventory.db` file in the same directory on first run. The database is seeded with sample data including:

- 5 locations (Help Desk, Storage Room, Computer Lab 1 & 2, Server Room)
- 23 inventory items across all locations

To reset the database, simply delete the `inventory.db` file and restart the application.

## Project Structure

```
python_app/
├── inventory_app.py   # Main application with Tkinter GUI
├── database.py        # SQLite database operations
├── requirements.txt   # Dependencies (standard library only)
└── README.md          # This file
```

