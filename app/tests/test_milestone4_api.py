import os

os.environ["DATABASE_URL"] = "sqlite:///./test_milestone4_fresh.db"

from app.config import get_settings

get_settings.cache_clear()

import app.models  # noqa: F401
from app.database import Base, engine
from app.main import app
from fastapi.testclient import TestClient

Base.metadata.create_all(bind=engine)

from app.seed import seed_data

seed_data()
client = TestClient(app)


def test_intelligence_latest():
    response = client.get("/api/intelligence/latest")
    assert response.status_code == 200
    body = response.json()
    assert "kpis" in body
    assert body["outlet_count"] >= 1


def test_executive_summary():
    response = client.get("/api/executive/summary")
    assert response.status_code == 200
    body = response.json()
    assert "agent_summaries" in body
    assert len(body["agent_summaries"]) == 6


def test_audit_dashboard():
    response = client.get("/api/audit/dashboard/summary")
    assert response.status_code == 200
    assert response.json()["total_inspections"] >= 0


def test_notifications_list():
    sync = client.post("/api/notifications/sync")
    assert sync.status_code == 200
    response = client.get("/api/notifications")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
