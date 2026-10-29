
import json
from pathlib import Path

from database import get_connection, initialize_database

BASE_DIR = Path(__file__).resolve().parent
ASSETS_FILE = BASE_DIR / "assets.json"
TICKETS_FILE = BASE_DIR / "tickets.json"


def read_json(file_path):
    if not file_path.exists():
        print(f"File not found, skipping: {file_path.name}")
        return []

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(f"{file_path.name} must contain a JSON list")

    return data


def migrate():
    assets = read_json(ASSETS_FILE)
    tickets = read_json(TICKETS_FILE)

    initialize_database()

    with get_connection() as connection:
        # Avoid importing the same records twice.
        existing_assets = connection.execute(
            "SELECT COUNT(*) FROM assets"
        ).fetchone()[0]

        existing_tickets = connection.execute(
            "SELECT COUNT(*) FROM tickets"
        ).fetchone()[0]

        if existing_assets or existing_tickets:
            print("Migration stopped: the database already contains records.")
            print("No data was imported. Check the database before retrying.")
            return

        for asset in assets:
            connection.execute(
                """
                INSERT INTO assets (id, name, type, location)
                VALUES (?, ?, ?, ?)
                """,
                (
                    asset["id"],
                    asset["name"],
                    asset["type"],
                    asset["location"],
                ),
            )

        for ticket in tickets:
            connection.execute(
                """
                INSERT INTO tickets
                    (id, title, description, priority, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    ticket["id"],
                    ticket["title"],
                    ticket["description"],
                    ticket["priority"],
                    ticket["status"],
                    ticket["created_at"],
                ),
            )

    print("Migration completed successfully.")
    print(f"Assets imported: {len(assets)}")
    print(f"Tickets imported: {len(tickets)}")


if __name__ == "__main__":
    migrate()
