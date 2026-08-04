"""
SentinelAI - Shared pytest fixtures.

Provides a small synthetic dataset (employees + events) usable across
tests without requiring the full 200k-event generation.
"""

import sys
import os
from typing import Dict

import pandas as pd
import pytest

# Ensure backend and repo root are importable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


@pytest.fixture
def sample_employees() -> pd.DataFrame:
    """Small employee DataFrame for unit tests."""
    return pd.DataFrame(
        [
            {
                "employee_id": "EMP00001",
                "name": "Alice Johnson",
                "email": "alice@test.com",
                "department": "Engineering",
                "position": "Software Engineer",
                "location": "New York",
                "is_remote": False,
                "risk_profile": "normal",
                "tenure_days": 500,
                "working_hours_start": 9,
                "working_hours_end": 17,
                "manager": "Bob Smith",
                "clearance_level": "medium",
                "has_vpn": True,
                "device_id": "DEV-001",
                "os": "Windows 11",
                "department_risk_factor": 1.5,
            },
            {
                "employee_id": "EMP00002",
                "name": "Bob Smith",
                "email": "bob@test.com",
                "department": "Finance",
                "position": "Financial Analyst",
                "location": "London",
                "is_remote": True,
                "risk_profile": "malicious",
                "tenure_days": 900,
                "working_hours_start": 8,
                "working_hours_end": 16,
                "manager": "Carol",
                "clearance_level": "high",
                "has_vpn": True,
                "device_id": "DEV-002",
                "os": "macOS Sonoma",
                "department_risk_factor": 1.3,
            },
        ]
    )


@pytest.fixture
def sample_events() -> Dict[str, pd.DataFrame]:
    """Small event DataFrames for unit tests."""
    login_events = pd.DataFrame(
        [
            {
                "employee_id": "EMP00001",
                "timestamp": "2025-01-01T10:00:00",
                "hour": 10,
                "day_of_week": 2,
                "is_weekend": False,
                "is_new_device": False,
                "device_id": "DEV-001",
                "browser": "Chrome",
                "session_duration_minutes": 120,
                "country": "United States",
            },
            {
                "employee_id": "EMP00001",
                "timestamp": "2025-01-02T03:00:00",
                "hour": 3,
                "day_of_week": 3,
                "is_weekend": False,
                "is_new_device": True,
                "device_id": "DEV-999",
                "browser": "Tor",
                "session_duration_minutes": 30,
                "country": "Russia",
            },
        ]
    )

    usb_events = pd.DataFrame(
        [
            {
                "employee_id": "EMP00001",
                "timestamp": "2025-01-02T03:30:00",
                "transfer_size_mb": 800,
                "files_copied": 300,
                "is_high_volume": True,
            }
        ]
    )

    cloud_events = pd.DataFrame(
        [
            {
                "employee_id": "EMP00001",
                "timestamp": "2025-01-02T03:45:00",
                "upload_size_mb": 500,
                "is_large_upload": True,
            }
        ]
    )

    return {
        "login_events": login_events,
        "usb_events": usb_events,
        "cloud_events": cloud_events,
        "network_events": pd.DataFrame(),
        "browser_events": pd.DataFrame(),
        "email_events": pd.DataFrame(),
        "application_events": pd.DataFrame(),
    }


@pytest.fixture
def test_client():
    """FastAPI TestClient for API integration tests."""
    from fastapi.testclient import TestClient

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import app as app_module

    with TestClient(app_module.app) as client:
        yield client
