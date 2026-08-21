"""Tests for the MQTT integration layer.

The software-only default keeps MQTT disabled and never touches the network;
the tests assert that disabled mode is a safe no-op and that the status
endpoint reports it truthfully.
"""

from fastapi.testclient import TestClient

from app.main import app
from app.services.control_service import ControlService
from app.services.mqtt_service import MQTTService, mqtt_service

client = TestClient(app)


def test_mqtt_status_default_disabled():
    response = client.get("/mqtt/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["enabled"] is False
    assert payload["connected"] is False
    assert payload["mode"] == "disabled"


def test_disabled_mqtt_is_a_safe_noop():
    assert mqtt_service.enabled is False
    assert mqtt_service.connect() is False
    assert mqtt_service.disconnect() is None
    assert mqtt_service.publish("energy/test", {"a": 1}) is False
    assert mqtt_service.subscribe("energy/test") is False
    assert mqtt_service.send_command("air_fryer", "off") is False
    assert mqtt_service.broadcast_command("off") is False


def test_mqtt_status_reflects_explicit_configuration(monkeypatch):
    monkeypatch.setenv("MQTT_ENABLED", "1")
    service = MQTTService()
    status = service.get_status()
    assert status["enabled"] is True
    assert status["mode"] == "active"
    assert status["connected"] is False  # no broker in tests
    assert service.send_command("air_fryer", "off") is False  # not connected
    service.disconnect()


def test_toggle_still_works_with_mqtt_disabled():
    # The control flow must not be affected by the (disabled) MQTT hook.
    ControlService._device_states.pop("Study Lamp", None)
    result = ControlService.toggle_device("Study Lamp")
    assert "is_on" in result
    # Restore the original state so later tests are unaffected.
    ControlService.toggle_device("Study Lamp")