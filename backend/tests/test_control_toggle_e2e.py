"""End-to-end contract test for the device toggle -> analytics zeroing flow.

Pins the invariant that `_apply_device_states` actually reflects a toggle:
turning a dataset-backed device OFF must drop its consumption from the
summary and the device breakdown, and turning it back ON must restore the
original numbers.

This is the exact flow the DeviceControl UI performs
(POST /control/devices/{name}/toggle), and the reason it regressed silently is
that the analytics device-state map only read the DB registry, which never
contained dataset-derived devices.
"""

from uuid import uuid4

from fastapi.testclient import TestClient

from app.database.repository import db
from app.main import app
from app.services.control_service import ControlService

client = TestClient(app)


def _auth_headers():
    unique = uuid4().hex[:10]
    identifier = f"{unique}@example.com"
    resp = client.post("/users/register", json={
        "name": "E2E User",
        "age": "30",
        "identifier": identifier,
        "password": "StrongPass1",
    })
    token = resp.json().get("token")
    return {"Authorization": f"Bearer {token}"}


def test_toggle_off_reduces_analytics_and_toggle_on_restores():
    headers = _auth_headers()
    devices = client.get("/control/devices", headers=headers).json()
    candidates = [d for d in devices if float(d.get("share", 0.0)) > 0]
    assert candidates, "No dataset-backed device with nonzero share was found"
    target = max(candidates, key=lambda d: float(d.get("share", 0.0)))
    name = target["name"]

    registered_before = {str(d.get("device_id", "")).strip().lower() for d in db.get_devices()}
    ControlService._device_states.pop(name, None)

    baseline = float(client.get("/analytics/summary", headers=headers).json()["daily_consumption"])

    off = client.post(f"/control/devices/{name}/toggle", headers=headers)
    assert off.status_code == 200, off.text
    assert off.json()["state"] == "off"
    assert off.json()["changed_at"]
    events = client.get(f"/control/devices/{target['device_id']}/state-events", headers=headers)
    assert events.status_code == 200, events.text
    assert events.json()[-1]["state"] == "off"
    off_summary = client.get("/analytics/summary", headers=headers).json()
    off_breakdown = {d["name"]: d for d in client.get("/analytics/device-breakdown", headers=headers).json()}

    assert float(off_summary["daily_consumption"]) < baseline, (
        "Toggling a device OFF must reduce the daily consumption total"
    )
    assert float(off_breakdown[name]["share"]) == 0.0, (
        "A device toggled OFF must disappear from the device breakdown"
    )

    on = client.post(f"/control/devices/{name}/toggle", headers=headers)
    assert on.status_code == 200, on.text
    restored = float(client.get("/analytics/summary", headers=headers).json()["daily_consumption"])
    assert abs(restored - baseline) < 0.6, (
        "Toggling a device back ON must restore the original daily consumption total"
    )

    # Leave the durable registry as we found it.
    registered_after = {str(d.get("device_id", "")).strip().lower() for d in db.get_devices()}
    for device_id in registered_after - registered_before:
        db.delete_device(device_id)


def test_control_registry_contains_union_of_all_dataset_devices():
    headers = _auth_headers()
    devices = client.get("/control/devices", headers=headers).json()
    control_ids = {str(device["device_id"]).lower() for device in devices}

    from app.services.dataset_service import DatasetService

    expected_ids = {
        str(device_id).lower().replace(" ", "_")
        for device_id in DatasetService.all_dataset_device_columns()
    }
    assert expected_ids.issubset(control_ids)
    dataset_devices = {str(device["device_id"]).lower(): device for device in devices}
    for device_id in expected_ids:
        device = dataset_devices[device_id]
        assert float(device["rated_power_w"]) > 0
        assert float(device["efficiency"]) > 0
        assert device["operating_state"] in {"on", "off", "standby"}
