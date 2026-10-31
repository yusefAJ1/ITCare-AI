
import pytest
from fastapi.testclient import TestClient

import api
from database import get_connection


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Give every test its own temporary SQLite database.
    test_db = tmp_path / "test_itcare.db"

    def test_connection():
        import sqlite3

        connection = sqlite3.connect(test_db)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    monkeypatch.setattr(api, "get_connection", test_connection)

    with test_connection() as connection:
        connection.execute("""
            CREATE TABLE assets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                location TEXT NOT NULL
            )
        """)
        connection.execute("""
            CREATE TABLE tickets (
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

    with TestClient(api.app) as test_client:
        yield test_client


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["database"] == "SQLite"


def test_create_and_list_asset(client):
    response = client.post(
        "/assets",
        json={
            "name": "Test Laptop",
            "type": "Laptop",
            "location": "IT Office",
        },
    )

    assert response.status_code == 201
    asset = response.json()
    assert asset["name"] == "Test Laptop"

    list_response = client.get("/assets")
    assert list_response.status_code == 200
    assert any(item["id"] == asset["id"] for item in list_response.json())


def test_missing_asset_returns_404(client):
    response = client.get("/assets/99999")
    assert response.status_code == 404


def test_create_and_update_ticket_status(client):
    response = client.post(
        "/tickets",
        json={
            "title": "Network problem",
            "description": "Testing ticket creation",
            "priority": "High",
        },
    )

    assert response.status_code == 201
    ticket = response.json()
    assert ticket["status"] == "Open"

    update_response = client.patch(
        f"/tickets/{ticket['id']}/status",
        params={"status": "In Progress"},
    )

    assert update_response.status_code == 200
    assert update_response.json()["status"] == "In Progress"

def test_delete_asset(client):
    create_response = client.post(
        "/assets",
        json={
            "name": "Temporary Laptop",
            "type": "Laptop",
            "location": "Test Room",
        },
    )

    assert create_response.status_code == 201
    asset_id = create_response.json()["id"]

    delete_response = client.delete(f"/assets/{asset_id}")

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Asset deleted"

    get_response = client.get(f"/assets/{asset_id}")
    assert get_response.status_code == 404


def test_delete_asset(client):
    create_response = client.post(
        "/assets",
        json={
            "name": "Temporary Laptop",
            "type": "Laptop",
            "location": "Test Room",
        },
    )

    assert create_response.status_code == 201
    asset_id = create_response.json()["id"]

    delete_response = client.delete(f"/assets/{asset_id}")

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Asset deleted"

    get_response = client.get(f"/assets/{asset_id}")
    assert get_response.status_code == 404

def test_update_asset(client):
    create_response = client.post(
        "/assets",
        json={
            "name": "Old Laptop",
            "type": "Laptop",
            "location": "Room A",
        },
    )

    assert create_response.status_code == 201
    asset_id = create_response.json()["id"]

    update_response = client.put(
        f"/assets/{asset_id}",
        json={
            "name": "Updated Laptop",
            "type": "Laptop",
            "location": "Room B",
        },
    )

    assert update_response.status_code == 200
    updated_asset = update_response.json()

    assert updated_asset["name"] == "Updated Laptop"
    assert updated_asset["location"] == "Room B"

def test_invalid_ticket_priority(client):
    response = client.post(
        "/tickets",
        json={
            "title": "Test invalid priority",
            "description": "Testing an unsupported priority",
            "priority": "Urgent",
        },
    )

    assert response.status_code == 422
