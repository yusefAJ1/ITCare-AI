
import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ITCare AI API",
    description="IT asset inventory management API",
    version="1.0.0",

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

DATA_FILE = Path(__file__).with_name("assets.json")


class AssetInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    type: str = Field(min_length=1, max_length=50)
    location: str = Field(min_length=1, max_length=100)


def load_assets():
    if not DATA_FILE.exists():
        return []

    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_assets(assets):
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(assets, file, indent=4, ensure_ascii=False)


@app.get("/")
def home():
    return {
        "message": "Welcome to ITCare AI API",
        "status": "running",
    }


@app.get("/assets")
def get_assets():
    return load_assets()


@app.get("/assets/{asset_id}")
def get_asset(asset_id: int):
    for asset in load_assets():
        if asset["id"] == asset_id:
            return asset

    raise HTTPException(status_code=404, detail="Asset not found")


@app.post("/assets", status_code=201)
def create_asset(asset_input: AssetInput):
    assets = load_assets()

    new_asset = {
        "id": max((a["id"] for a in assets), default=0) + 1,
        "name": asset_input.name.strip(),
        "type": asset_input.type.strip(),
        "location": asset_input.location.strip(),
    }

    if not all(new_asset[k] for k in ("name", "type", "location")):
        raise HTTPException(status_code=422, detail="All fields must contain text")

    assets.append(new_asset)
    save_assets(assets)
    return new_asset


@app.put("/assets/{asset_id}")
def update_asset(asset_id: int, asset_input: AssetInput):
    assets = load_assets()

    for asset in assets:
        if asset["id"] == asset_id:
            asset["name"] = asset_input.name.strip()
            asset["type"] = asset_input.type.strip()
            asset["location"] = asset_input.location.strip()

            if not all(asset[k] for k in ("name", "type", "location")):
                raise HTTPException(status_code=422, detail="All fields must contain text")

            save_assets(assets)
            return asset

    raise HTTPException(status_code=404, detail="Asset not found")


@app.delete("/assets/{asset_id}")
def delete_asset(asset_id: int):
    assets = load_assets()

    for index, asset in enumerate(assets):
        if asset["id"] == asset_id:
            deleted = assets.pop(index)
            save_assets(assets)
            return {"message": "Asset deleted", "asset": deleted}

    raise HTTPException(status_code=404, detail="Asset not found")
    
from datetime import datetime, timezone


TICKETS_FILE = Path(__file__).with_name("tickets.json")


class TicketInput(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str = Field(min_length=5, max_length=2000)
    priority: str = Field(default="Medium", pattern="^(Low|Medium|High|Critical)$")


def load_tickets():
    if not TICKETS_FILE.exists():
        return []

    with TICKETS_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_tickets(tickets):
    with TICKETS_FILE.open("w", encoding="utf-8") as file:
        json.dump(tickets, file, indent=4, ensure_ascii=False)


@app.get("/tickets")
def get_tickets():
    return load_tickets()


@app.post("/tickets", status_code=201)
def create_ticket(ticket_input: TicketInput):
    tickets = load_tickets()

    new_ticket = {
        "id": max((ticket["id"] for ticket in tickets), default=0) + 1,
        "title": ticket_input.title.strip(),
        "description": ticket_input.description.strip(),
        "priority": ticket_input.priority,
        "status": "Open",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    if not new_ticket["title"] or not new_ticket["description"]:
        raise HTTPException(
            status_code=422,
            detail="Title and description cannot be empty",
        )

    tickets.append(new_ticket)
    save_tickets(tickets)
    return new_ticket


@app.patch("/tickets/{ticket_id}/status")
def update_ticket_status(ticket_id: int, status: str):
    allowed_statuses = {"Open", "In Progress", "Resolved", "Closed"}

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=422,
            detail="Invalid status",
        )

    tickets = load_tickets()

    for ticket in tickets:
        if ticket["id"] == ticket_id:
            ticket["status"] = status
            save_tickets(tickets)
            return ticket

    raise HTTPException(status_code=404, detail="Ticket not found")

