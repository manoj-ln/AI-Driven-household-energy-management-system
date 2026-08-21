from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _auth_headers():
    from uuid import uuid4
    unique = uuid4().hex[:10]
    identifier = f"{unique}@example.com"
    resp = client.post("/users/register", json={
        "name": "Test User",
        "age": "25",
        "identifier": identifier,
        "password": "StrongPass1",
    })
    token = resp.json().get("token")
    return {"Authorization": f"Bearer {token}"}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_prediction_endpoint():
    headers = _auth_headers()
    response = client.get("/predictions/next-hour", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "anomaly_summary" in data


def test_prediction_explainability_endpoint():
    headers = _auth_headers()
    response = client.get("/predictions/explain-next", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "top_factors" in data
    assert isinstance(data["top_factors"], list)


def test_optimization_endpoint():
    headers = _auth_headers()
    response = client.get("/optimization/report", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "estimated_savings" in data
    assert "monthly_projection" in data


def test_dataset_mode_and_selection_endpoints():
    headers = _auth_headers()
    mode_data = client.get("/analytics/dataset-mode", headers=headers).json()
    assert "mode" in mode_data

    datasets_data = client.get("/analytics/datasets", headers=headers).json()
    assert "datasets" in datasets_data
    assert len(datasets_data["datasets"]) >= 4
    production_datasets = {
        "energy_dataset_2021.csv",
        "energy_dataset_2024.csv",
        "energy_dataset_2025.csv",
        "energy_dataset_merged_3years.csv",
    }
    assert production_datasets.issubset(set(datasets_data["datasets"]))

    selected = datasets_data["datasets"][0]
    select_response = client.post(
        "/analytics/datasets/select",
        json={"dataset_name": selected},
        headers=headers,
    )
    assert select_response.json()["status"] == "success"

    set_mode_response = client.post(
        "/analytics/dataset-mode",
        json={"mode": "synthetic_demo"},
        headers=headers,
    )
    assert set_mode_response.json()["status"] == "success"


def test_create_control_device():
    from app.services.control_service import ControlService
    ControlService._device_states.pop("Study Lamp", None)

    headers = _auth_headers()
    created = client.post(
        "/control/devices",
        json={"name": "Study Lamp", "device_type": "light", "location": "Study Room", "quantity": 1},
        headers=headers,
    ).json()
    devices = client.get("/control/devices", headers=headers).json()

    assert created["name"] == "Study Lamp"
    assert any(device["name"] == "Study Lamp" for device in devices)

    client.delete(f"/control/devices/{created['device_id']}", headers=headers)
