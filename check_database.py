
from database import get_connection, initialize_database


def check_database():
    initialize_database()

    with get_connection() as connection:
        assets = connection.execute(
            "SELECT * FROM assets ORDER BY id"
        ).fetchall()

        tickets = connection.execute(
            "SELECT * FROM tickets ORDER BY id"
        ).fetchall()

        print("\n=== ASSETS ===")
        print(f"Total assets: {len(assets)}")

        for asset in assets:
            print(dict(asset))

        print("\n=== TICKETS ===")
        print(f"Total tickets: {len(tickets)}")

        for ticket in tickets:
            print(dict(ticket))

        print("\n=== DATABASE CHECK ===")
        print("Assets table: OK")
        print("Tickets table: OK")


if __name__ == "__main__":
    check_database()
