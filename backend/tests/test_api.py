import asyncio

from app.main import health_check
from app.routes.predictions import get_next_hour_prediction
from app.routes.control import DeviceCreateRequest, create_control_device, get_control_devices


def test_health_check():
    response = asyncio.run(health_check())
    assert response["status"] == "ok"


def test_prediction_endpoint():
    response = asyncio.run(get_next_hour_prediction())
    assert "prediction" in response


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
