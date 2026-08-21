"""Shared test fixtures.

Autouse state reset so the class-level dataset settings in DatasetService
(and their persisted mirror at data/dataset_preferences.json) cannot leak
from one test into the next. Without this, a test that selects a dataset
changes the analytics source for every later test in the same run.
"""

from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.dataset_service import DatasetService
from app.services.control_service import ControlService
from app.database.repository import db

_SETTINGS_FILE = Path(__file__).resolve().parents[1] / "data" / "dataset_preferences.json"


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """Register a unique test user and return Authorization headers."""
    unique = uuid4().hex[:10]
    identifier = f"{unique}@example.com"
    password = "StrongPass1"
    resp = client.post(
        "/users/register",
        json={"name": "Test User", "age": "25", "identifier": identifier, "password": password},
    )
    token = resp.json().get("token") or resp.json().get("data", {}).get("token")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def reset_dataset_service():
    """Snapshot dataset settings before each test and restore them after."""
    original_settings = _SETTINGS_FILE.read_text(encoding="utf-8") if _SETTINGS_FILE.exists() else None
    original_selected = DatasetService._selected_dataset
    original_mode = DatasetService._dataset_mode
    original_device_states = dict(ControlService._device_states)

    yield

    DatasetService._selected_dataset = original_selected
    DatasetService._dataset_mode = original_mode
    ControlService._device_states.clear()
    ControlService._device_states.update(original_device_states)
    if original_settings is None:
        if _SETTINGS_FILE.exists():
            _SETTINGS_FILE.unlink()
    else:
        _SETTINGS_FILE.write_text(original_settings, encoding="utf-8")
