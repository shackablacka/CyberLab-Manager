import sqlite3
from pathlib import Path

DATABASE = Path("database/database.db")


def initialize_database() -> None:
    DATABASE.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'student',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CHECK(role IN ('student', 'admin', 'instructor'))
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                serial_number TEXT UNIQUE,
                location TEXT,
                status TEXT NOT NULL DEFAULT 'available'
                    CHECK(status IN ('available', 'borrowed', 'maintenance')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                check_in TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                check_out TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS borrowings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                asset_id INTEGER NOT NULL,
                borrow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_date TEXT NOT NULL,
                return_date TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tool_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                role TEXT NOT NULL,
                team TEXT NOT NULL,
                tool_name TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'ok',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.commit()
