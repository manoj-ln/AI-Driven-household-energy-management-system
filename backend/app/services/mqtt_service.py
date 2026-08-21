"""
MQTT integration layer.

The project is software-only, so MQTT is DISABLED by default and the service
degrades to the old no-op stub behaviour (nothing is published or subscribed,
`connect()` returns False). Setting ``MQTT_ENABLED=1`` switches the service
into a real paho client that:

- connects to ``MQTT_BROKER_HOST:MQTT_BROKER_PORT`` (defaults localhost:1883)
- subscribes to ``<prefix>/devices/+/telemetry`` and ingests JSON readings
  through the same pipeline as ``POST /energy/ingest`` (DataService.save_reading)
- exposes ``send_command()`` used by the device toggle flow to publish control
  messages to ``<prefix>/devices/{device_id}/cmd``

No broker is required for the default software-only demo; the router and the
startup hook are always wired, but a disabled or unreachable broker is never
fatal for the rest of the application.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.core.config import settings
from app.utils.logger import logger

TELEMETRY_SUFFIX = "devices/+/telemetry"
COMMAND_SUFFIX = "devices/{device_id}/cmd"


class MQTTService:
    def __init__(
        self,
        broker_host: Optional[str] = None,
        broker_port: Optional[int] = None,
        enabled: Optional[bool] = None,
    ):
        self.broker_host = broker_host or settings.mqtt_broker_host
        self.broker_port = broker_port if broker_port is not None else settings.mqtt_broker_port
        if enabled is None:
            enabled = os.getenv("MQTT_ENABLED", "0").strip().lower() in {"1", "true", "yes", "on"}
        self.enabled = bool(enabled)
        self.topic_prefix = settings.mqtt_topic_prefix
        self.connected = False
        self._client = None

    # -- lifecycle -----------------------------------------------------------

    def connect(self) -> bool:
        """Connect to the broker. No-op (returns False) when disabled."""
        if not self.enabled:
            return False
        try:
            import paho.mqtt.client as mqtt
        except ImportError:
            logger.warning("paho-mqtt is not installed; MQTT stays disabled.")
            self.enabled = False
            return False

        try:
            client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="energy-backend")
            client.on_connect = self._on_connect
            client.on_message = self._on_message
            client.on_disconnect = self._on_disconnect
            client.connect(self.broker_host, self.broker_port, keepalive=60)
            client.loop_start()
            self._client = client
            return True
        except Exception as exc:  # pragma: no cover - depends on broker presence
            logger.warning("MQTT connect to %s:%s failed: %s", self.broker_host, self.broker_port, exc)
            self.connected = False
            return False

    def disconnect(self) -> None:
        """Stop the paho loop and disconnect from the broker (best effort)."""
        if self._client is not None:
            try:
                self._client.loop_stop()
                self._client.disconnect()
            except Exception:  # pragma: no cover - best effort teardown
                pass
            self._client = None
        self.connected = False

    def start(self) -> bool:
        """Idempotent startup hook used from the FastAPI lifespan."""
        return self.connect()

    def stop(self) -> None:
        self.disconnect()

    # -- paho callbacks ------------------------------------------------------

    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        connected = not reason_code.is_failure
        self.connected = connected
        if connected:
            client.subscribe(f"{self.topic_prefix}/{TELEMETRY_SUFFIX}", qos=0)
            logger.info("MQTT connected to %s:%s", self.broker_host, self.broker_port)

    def _on_disconnect(self, client, userdata, flags, reason_code=None, properties=None):
        self.connected = False

    def _on_message(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            logger.warning("Ignoring non-JSON MQTT payload on %s", message.topic)
            return
        self._ingest_reading(payload)

    def _ingest_reading(self, payload: Dict[str, Any]) -> bool:
        """Persist an MQTT telemetry reading via the shared ingest pipeline."""
        try:
            from app.schemas.energy_schema import EnergyReading
            from app.services.data_service import DataService

            raw_ts = payload.get("timestamp")
            timestamp = datetime.fromisoformat(raw_ts) if raw_ts else datetime.now(timezone.utc)
            energy = payload.get("energy_kwh")
            if energy is None:
                energy = payload.get("energy_consumption")
                if energy is None:
                    power_w = payload.get("power")
                    energy = (float(power_w) / 1000.0) if power_w is not None else None
            if energy is None:
                logger.warning("MQTT reading without energy value ignored: %s", payload)
                return False

            reading = EnergyReading(
                timestamp=timestamp,
                energy_kwh=float(energy),
                device_id=str(payload.get("device_id") or "mqtt_device"),
                device_type=payload.get("device_type") or "mqtt",
                temperature=payload.get("temperature"),
                appliance=payload.get("appliance"),
                location=payload.get("location"),
            )
            DataService.save_reading(reading)
            return True
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Failed to ingest MQTT reading: %s", exc)
            return False

    # -- publish / commands --------------------------------------------------

    def publish(self, topic: str, payload: Dict[str, Any], qos: int = 1) -> bool:
        """Publish a JSON payload. Returns False when disabled/disconnected."""
        if not self.enabled or not self.connected or self._client is None:
            return False
        try:
            info = self._client.publish(topic, json.dumps(payload), qos=qos)
            return info.rc == 0
        except Exception:  # pragma: no cover - defensive
            return False

    def subscribe(self, topic: str, qos: int = 1) -> bool:
        if not self.enabled or not self.connected or self._client is None:
            return False
        try:
            result, _mid = self._client.subscribe(topic, qos=qos)
            return result == 0
        except Exception:  # pragma: no cover - defensive
            return False

    def send_command(self, device_id: str, command: str, params: Dict[str, Any] | None = None) -> bool:
        """Publish a control command for a device (used by the toggle flow)."""
        topic = f"{self.topic_prefix}/{COMMAND_SUFFIX.format(device_id=device_id)}"
        payload = {
            "command": command,
            "device_id": device_id,
            "params": params or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return self.publish(topic, payload, qos=1)

    def broadcast_command(
        self,
        command: str,
        params: Dict[str, Any] | None = None,
        device_type: str | None = None,
    ) -> bool:
        """Publish a command for a whole device type (best-effort fan-out)."""
        topic = f"{self.topic_prefix}/devices/{device_type or '+'}/cmd"
        payload = {
            "command": command,
            "device_type": device_type,
            "params": params or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return self.publish(topic, payload, qos=1)

    def get_status(self) -> Dict[str, Any]:
        return {
            "enabled": self.enabled,
            "connected": self.connected,
            "broker_host": self.broker_host,
            "broker_port": self.broker_port,
            "topic_prefix": self.topic_prefix,
            "mode": "active" if self.enabled else "disabled",
            "message": "MQTT broker link is active."
            if self.enabled
            else "MQTT is disabled in the software-only project.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


mqtt_service = MQTTService()
