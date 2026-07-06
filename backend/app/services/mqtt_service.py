"""
Disabled MQTT compatibility layer.

The software-only version of the project does not require a broker or device
commands, but a small stub is kept so older imports fail gracefully instead of
crashing.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List


class MQTTService:
    def __init__(self, broker_host: str = "disabled", broker_port: int = 0):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.connected = False

    def connect(self) -> bool:
        return False

    def disconnect(self) -> None:
        self.connected = False

    def publish(self, topic: str, payload: Dict[str, Any], qos: int = 1) -> bool:
        return False

    def subscribe(self, topic: str, qos: int = 1) -> bool:
        return False

    def send_command(self, device_id: str, command: str, params: Dict[str, Any] | None = None) -> bool:
        return False

    def broadcast_command(self, command: str, params: Dict[str, Any] | None = None, device_type: str | None = None) -> bool:
        return False

    def get_status(self) -> Dict[str, Any]:
        return {
            "connected": False,
            "broker_host": self.broker_host,
            "broker_port": self.broker_port,
            "mode": "disabled",
            "message": "MQTT is disabled in the software-only project.",
            "timestamp": datetime.utcnow().isoformat(),
        }


mqtt_service = MQTTService()
