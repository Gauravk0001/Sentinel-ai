"""
SentinelAI - API integration tests.

Tests the FastAPI endpoints (auth, dashboard, AI engine, alerts, incidents).
Uses TestClient with an in-memory/SQLite database.

These tests start the app fresh via asgi-lifespan TestClient.
"""

import sys
import os
from typing import Dict

import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test credentials
TEST_USER = {"username": "admin", "password": "admin123"}


@pytest.fixture(scope="module")
def client():
    """FastAPI TestClient instance (module-scoped)."""
    import app as app_module

    with TestClient(app_module.app) as c:
        yield c


def login(client: TestClient) -> str:
    """Helper: login and return access token."""
    resp = client.post(
        "/api/auth/login",
        data=TEST_USER,
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()["access_token"]


def auth_header(token: str) -> Dict[str, str]:
    """Helper: build auth header."""
    return {"Authorization": f"Bearer {token}"}


# === Health & Info ===

def test_health_check(client):
    """Health endpoint should be up."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"


def test_root_info(client):
    """Root endpoint should return app info."""
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["app"] == "SentinelAI"


# === Auth API ===

def test_login_success(client):
    """Valid credentials should return tokens."""
    resp = client.post("/api/auth/login", data=TEST_USER)
    assert resp.status_code == 200
    token = resp.json()
    assert "access_token" in token
    assert "refresh_token" in token


def test_login_failure(client):
    """Invalid credentials should 401."""
    resp = client.post(
        "/api/auth/login",
        data={"username": "admin", "password": "wrongpass"},
    )
    assert resp.status_code == 401


def test_me_endpoint(client):
    """GET /me should return current user."""
    token = login(client)
    resp = client.get("/api/auth/me", headers=auth_header(token))
    assert resp.status_code == 200
    assert resp.json()["username"] == "admin"


# === AI Engine API ===

def test_ai_predict(client):
    """POST /api/ai/predict should return explainable risk."""
    token = login(client)
    resp = client.post(
        "/api/ai/predict",
        json={"employee_id": "EMP00001"},
        headers=auth_header(token),
    )
    assert resp.status_code == 200, f"Predict failed: {resp.text}"
    data = resp.json()
    assert "risk_score" in data
    assert "threat_level" in data
    assert "confidence" in data
    assert "reasons" in data
    assert 0 <= data["risk_score"] <= 100


def test_ai_employee_risk(client):
    """GET /api/ai/employee-risk should return compact risk."""
    token = login(client)
    resp = client.get(
        "/api/ai/employee-risk",
        params={"employee_id": "EMP00001"},
        headers=auth_header(token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["employee_id"] == "EMP00001"
    assert "risk_score" in data


def test_ai_high_risk_requires_role(client):
    """High-risk endpoint requires admin/analyst role."""
    token = login(client)
    resp = client.get(
        "/api/ai/high-risk",
        headers=auth_header(token),
    )
    assert resp.status_code in (200, 403)


def test_ai_model_info(client):
    """Model info should include active model."""
    token = login(client)
    resp = client.get("/api/ai/model-info", headers=auth_header(token))
    assert resp.status_code == 200
    data = resp.json()
    assert "active_model" in data
    assert "versions" in data


def test_ai_live_alerts(client):
    """Live alerts endpoint should return a list."""
    token = login(client)
    resp = client.get("/api/ai/alerts/live", headers=auth_header(token))
    assert resp.status_code == 200
    data = resp.json()
    assert "alerts" in data


def test_ai_timeline(client):
    """Timeline endpoint should return events."""
    token = login(client)
    resp = client.get(
        "/api/ai/timeline",
        params={"employee_id": "EMP00001"},
        headers=auth_header(token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "timeline" in data
    assert data["employee_id"] == "EMP00001"


def test_ai_baseline(client):
    """Baseline endpoint should return employee baseline."""
    token = login(client)
    resp = client.get(
        "/api/ai/baseline/EMP00001",
        headers=auth_header(token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("employee_id") == "EMP00001"


# === Dashboard API ===

def test_dashboard_overview(client):
    """Dashboard overview should return stats."""
    token = login(client)
    resp = client.get("/api/dashboard/overview", headers=auth_header(token))
    assert resp.status_code == 200
    data = resp.json()
    assert "stats" in data


# === Protected routes require auth ===

def test_protected_route_without_token(client):
    """Protected endpoints should 401 without token."""
    resp = client.get("/api/dashboard/stats")
    assert resp.status_code == 401
