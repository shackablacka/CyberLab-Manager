import sqlite3
from pathlib import Path

DB_PATH = Path("database/database.db")


def get_connection():
    """Return a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)


def initialize_database():
    """Create database tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_tag TEXT UNIQUE NOT NULL,
        asset_name TEXT NOT NULL,
        category TEXT,
        status TEXT DEFAULT 'Available',
        location TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS borrow_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_id INTEGER,
        borrower TEXT,
        borrowed_date TEXT,
        returned_date TEXT,
        status TEXT,
        FOREIGN KEY(asset_id) REFERENCES assets(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        class_name TEXT,
        date TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()
