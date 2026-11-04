
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from database import get_connection, initialize_database


app = FastAPI(
    title="ITCare AI API",
    description="IT asset inventory management API",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type"],
)

# Create the tables if they do not exist.
initialize_database()


class AssetInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type: str = Field(min_length=1, max_length=50)
    location: str = Field(min_length=1, max_length=100)


class TicketInput(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str = Field(min_length=5, max_length=2000)
    priority: str = Field(
        default="Medium",
        pattern="^(Low|Medium|High|Critical)$",
    )


def validate_text_fields(data, fields):
    if any(not data[field].strip() for field in fields):
        raise HTTPException(
            status_code=422,
            detail="Required fields cannot contain only whitespace",
        )



def ensure_history_tables(connection):
    connection.execute("""CREATE TABLE IF NOT EXISTS asset_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT, asset_id INTEGER NOT NULL,
        action TEXT NOT NULL, details TEXT NOT NULL, created_at TEXT NOT NULL)""")
    connection.execute("""CREATE TABLE IF NOT EXISTS ticket_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT, ticket_id INTEGER NOT NULL,
        action TEXT NOT NULL, details TEXT NOT NULL, created_at TEXT NOT NULL)""")

def row_to_dict(row):
    return dict(row) if row is not None else None


@app.get("/")
def home():
    return {
        "message": "Welcome to ITCare AI API",
        "status": "running",
        "database": "SQLite",
    }


# --------------------
# Assets
# --------------------

@app.get("/assets")
def get_assets():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, name, type, location FROM assets ORDER BY id"
        ).fetchall()

    return [dict(row) for row in rows]


@app.get("/assets/{asset_id}")
def get_asset(asset_id: int):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, name, type, location FROM assets WHERE id = ?",
            (asset_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Asset not found")

    return row_to_dict(row)


@app.post("/assets", status_code=201)
def create_asset(asset_input: AssetInput):
    data = asset_input.model_dump()
    validate_text_fields(data, ("name", "type", "location"))

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO assets (name, type, location)
            VALUES (?, ?, ?)
            """,
            (
                data["name"].strip(),
                data["type"].strip(),
                data["location"].strip(),
            ),
        )

        ensure_history_tables(connection)
        connection.execute(
            "INSERT INTO asset_history (asset_id, action, details, created_at) VALUES (?, ?, ?, ?)",
            (cursor.lastrowid, "Created", f'{data["name"].strip()} | {data["type"].strip()} | {data["location"].strip()}', datetime.now(timezone.utc).isoformat()),
        )
        row = connection.execute(
            "SELECT id, name, type, location FROM assets WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()

    return row_to_dict(row)


@app.put("/assets/{asset_id}")
def update_asset(asset_id: int, asset_input: AssetInput):
    data = asset_input.model_dump()
    validate_text_fields(data, ("name", "type", "location"))

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE assets
            SET name = ?, type = ?, location = ?
            WHERE id = ?
            """,
            (
                data["name"].strip(),
                data["type"].strip(),
                data["location"].strip(),
                asset_id,
            ),
        )

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Asset not found")

        ensure_history_tables(connection)
        connection.execute(
            "INSERT INTO asset_history (asset_id, action, details, created_at) VALUES (?, ?, ?, ?)",
            (asset_id, "Updated", f'{data["name"].strip()} | {data["type"].strip()} | {data["location"].strip()}', datetime.now(timezone.utc).isoformat()),
        )
        row = connection.execute(
            "SELECT id, name, type, location FROM assets WHERE id = ?",
            (asset_id,),
        ).fetchone()

    return row_to_dict(row)


@app.delete("/assets/{asset_id}")
def delete_asset(asset_id: int):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT id, name, type, location FROM assets WHERE id = ?",
            (asset_id,),
        ).fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="Asset not found")

        deleted_asset = dict(row)

        ensure_history_tables(connection)
        connection.execute(
            "INSERT INTO asset_history (asset_id, action, details, created_at) VALUES (?, ?, ?, ?)",
            (asset_id, "Deleted", f'{deleted_asset["name"]} | {deleted_asset["type"]} | {deleted_asset["location"]}', datetime.now(timezone.utc).isoformat()),
        )
        connection.execute(
            "DELETE FROM assets WHERE id = ?",
            (asset_id,),
        )

    return {"message": "Asset deleted", "asset": deleted_asset}


# --------------------
# Tickets
# --------------------

@app.get("/tickets")
def get_tickets():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, title, description, priority, status, created_at
            FROM tickets
            ORDER BY id
            """
        ).fetchall()

    return [dict(row) for row in rows]


@app.post("/tickets", status_code=201)
def create_ticket(ticket_input: TicketInput):
    data = ticket_input.model_dump()
    validate_text_fields(data, ("title", "description"))

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO tickets
                (title, description, priority, status, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                data["title"].strip(),
                data["description"].strip(),
                data["priority"],
                "Open",
                datetime.now(timezone.utc).isoformat(),
            ),
        )

        row = connection.execute(
            """
            SELECT id, title, description, priority, status, created_at
            FROM tickets
            WHERE id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()

    return row_to_dict(row)


@app.patch("/tickets/{ticket_id}/status")
def update_ticket_status(ticket_id: int, status: str):
    allowed_statuses = {"Open", "In Progress", "Resolved", "Closed"}

    if status not in allowed_statuses:
        raise HTTPException(status_code=422, detail="Invalid status")

    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE tickets SET status = ? WHERE id = ?",
            (status, ticket_id),
        )

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Ticket not found")

        row = connection.execute(
            """
            SELECT id, title, description, priority, status, created_at
            FROM tickets
            WHERE id = ?
            """,
            (ticket_id,),
        ).fetchone()

    return row_to_dict(row)


# --------------------
# Extended project features
# --------------------

class TicketUpdate(BaseModel):
    priority: str = Field(pattern="^(Low|Medium|High|Critical)$")
    status: str = Field(pattern="^(Open|In Progress|Resolved|Closed)$")
    resolution_notes: str = Field(default="", max_length=4000)


@app.put("/tickets/{ticket_id}")
def update_ticket(ticket_id: int, ticket_update: TicketUpdate):
    data = ticket_update.model_dump()
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as connection:
        cursor = connection.execute(
            """UPDATE tickets
               SET priority = ?, status = ?, resolution_notes = ?, updated_at = ?
               WHERE id = ?""",
            (data["priority"], data["status"], data["resolution_notes"].strip(), now, ticket_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Ticket not found")
        connection.execute(
            "INSERT INTO ticket_history (ticket_id, action, details, created_at) VALUES (?, ?, ?, ?)",
            (ticket_id, "Updated", f'Priority: {data["priority"]}; Status: {data["status"]}; Notes updated', now),
        )
        row = connection.execute(
            """SELECT id, title, description, priority, status, created_at,
                      resolution_notes, updated_at FROM tickets WHERE id = ?""",
            (ticket_id,),
        ).fetchone()
    return row_to_dict(row)


@app.get("/tickets/{ticket_id}/history")
def get_ticket_history(ticket_id: int):
    with get_connection() as connection:
        exists = connection.execute("SELECT id FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        if exists is None:
            raise HTTPException(status_code=404, detail="Ticket not found")
        rows = connection.execute(
            "SELECT id, action, details, created_at FROM ticket_history WHERE ticket_id = ? ORDER BY id DESC",
            (ticket_id,),
        ).fetchall()
    return [dict(row) for row in rows]


@app.get("/assets/{asset_id}/history")
def get_asset_history(asset_id: int):
    with get_connection() as connection:
        exists = connection.execute("SELECT id FROM assets WHERE id = ?", (asset_id,)).fetchone()
        if exists is None:
            raise HTTPException(status_code=404, detail="Asset not found")
        rows = connection.execute(
            "SELECT id, action, details, created_at FROM asset_history WHERE asset_id = ? ORDER BY id DESC",
            (asset_id,),
        ).fetchall()
    return [dict(row) for row in rows]


@app.get("/reports/summary")
def get_report_summary():
    with get_connection() as connection:
        assets = connection.execute("SELECT type, COUNT(*) AS total FROM assets GROUP BY type ORDER BY type").fetchall()
        tickets = connection.execute("SELECT status, COUNT(*) AS total FROM tickets GROUP BY status ORDER BY status").fetchall()
        priorities = connection.execute("SELECT priority, COUNT(*) AS total FROM tickets GROUP BY priority ORDER BY priority").fetchall()
        totals = {
            "assets": connection.execute("SELECT COUNT(*) FROM assets").fetchone()[0],
            "tickets": connection.execute("SELECT COUNT(*) FROM tickets").fetchone()[0],
        }
    return {"totals": totals, "assets_by_type": [dict(x) for x in assets],
            "tickets_by_status": [dict(x) for x in tickets], "tickets_by_priority": [dict(x) for x in priorities]}
