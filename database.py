
import sqlite3
from pathlib import Path

DATABASE_FILE = Path(__file__).with_name("itcare.db")


def get_connection():
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                location TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                priority TEXT NOT NULL
                    CHECK (priority IN ('Low', 'Medium', 'High', 'Critical')),
                status TEXT NOT NULL DEFAULT 'Open'
                    CHECK (status IN ('Open', 'In Progress', 'Resolved', 'Closed')),
                created_at TEXT NOT NULL
            )
        """)


if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized: {DATABASE_FILE}")
