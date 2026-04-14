import asyncio

from app.main import health_check
from app.routes.predictions import get_next_hour_prediction, get_prediction_explainability
from app.routes.control import DeviceCreateRequest, create_control_device, get_control_devices
from app.routes.optimization import get_optimization_report
from app.routes.analytics import (
    get_dataset_mode,
    get_available_datasets,
    set_dataset_mode,
    select_dataset,
    DatasetModeRequest,
    DatasetSelectRequest,
)


def test_health_check():
    response = asyncio.run(health_check())
    assert response["status"] == "ok"


def test_prediction_endpoint():
    response = asyncio.run(get_next_hour_prediction())
    assert "prediction" in response
    assert "anomaly_summary" in response


def test_prediction_explainability_endpoint():
    response = asyncio.run(get_prediction_explainability())
    assert "prediction" in response
    assert "top_factors" in response
    assert isinstance(response["top_factors"], list)


def test_optimization_endpoint():
    response = asyncio.run(get_optimization_report())
    assert "estimated_savings" in response
    assert "monthly_projection" in response


def test_dataset_mode_and_selection_endpoints():
    mode_data = asyncio.run(get_dataset_mode())
    assert "mode" in mode_data
    datasets_data = asyncio.run(get_available_datasets())
    assert "datasets" in datasets_data
    assert len(datasets_data["datasets"]) >= 5
    selected = datasets_data["datasets"][0]
    select_response = asyncio.run(select_dataset(DatasetSelectRequest(dataset_name=selected)))
    assert select_response["status"] == "success"
    set_mode_response = asyncio.run(set_dataset_mode(DatasetModeRequest(mode="synthetic_demo")))
    assert set_mode_response["status"] == "success"


def test_create_control_device():
    payload = DeviceCreateRequest(
        name="Study Lamp",
        device_type="light",
        location="Study Room",
        quantity=1,
    )
    created = asyncio.run(create_control_device(payload))
    devices = asyncio.run(get_control_devices())

    assert created["name"] == "Study Lamp"
    assert any(device["name"] == "Study Lamp" for device in devices)
