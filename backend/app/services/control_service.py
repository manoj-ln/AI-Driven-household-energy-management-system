from datetime import datetime, timezone

from app.database.repository import db
from app.services.dataset_service import DatasetService


class ControlService:
    _device_states: dict[str, bool] = {}
    _dataset_devices_synced = False

    @staticmethod
    def _device_key(value: str) -> str:
        return value.strip().lower().replace(" ", "_")

    @staticmethod
    def _power_for(device: dict[str, object], state: str) -> float:
        if state == "off":
            return 0.0
        if state == "standby":
            return float(device.get("standby_power_w") or 0.0)
        return float(device.get("rated_power_w") or 100.0) * float(device.get("efficiency") or 1.0)

    @staticmethod
    def _default_power_profile(device_id: str) -> dict[str, object]:
        name = str(device_id).lower()
        rated_power_w = 100.0
        for terms, watts in (
            (("air_conditioner", "ac"), 1800.0),
            (("ev_charger", "ev_charge"), 7000.0),
            (("induction", "oven", "water_heater", "geyser"), 2000.0),
            (("washing_machine",), 700.0),
            (("microwave",), 1000.0),
            (("refrigerator", "fridge"), 180.0),
            (("ceiling_fan", "table_fan", "fan"), 75.0),
            (("television", "tv"), 120.0),
            (("light", "led", "bulb", "lamp"), 15.0),
            (("pump",), 750.0),
            (("computer", "laptop", "desktop", "pc"), 250.0),
            (("charger",), 20.0),
        ):
            if any(term in name for term in terms):
                rated_power_w = watts
                break
        return {
            "rated_power_w": rated_power_w,
            "standby_power_w": 2.0 if rated_power_w >= 100.0 else 0.5,
            "priority": 3,
            "efficiency": 0.9,
        }

    @classmethod
    def get_devices(cls) -> list[dict[str, object]]:
        cls._sync_dataset_devices()
        usage_map = {
            cls._device_key(device.get("device_id") or device["name"]): device
            for device in DatasetService.get_device_breakdown()
        }

        registered_devices = db.get_devices()
        result: list[dict[str, object]] = []
        seen_names: set[str] = set()

        for device in registered_devices:
            name = device.get("name") or device.get("device_id") or "Unnamed Device"
            device_key = cls._device_key(str(device.get("device_id") or name))
            stats = usage_map.get(device_key, {})
            if not stats:
                stats = usage_map.get(cls._device_key(name), {})
            is_active = bool(device.get("is_active", True))
            if name not in cls._device_states:
                cls._device_states[name] = is_active
            result.append(
                {
                    "name": name,
                    "device_id": device.get("device_id", name),
                    "device_type": device.get("device_type", "appliance"),
                    "location": device.get("location") or "Home",
                    "average_usage": stats.get("average_usage", 0.0),
                    "share": stats.get("share", 0.0),
                    "is_on": cls._device_states[name],
                    "operating_state": device.get("operating_state", "on"),
                    "rated_power_w": float(device.get("rated_power_w") or 100.0),
                    "standby_power_w": float(device.get("standby_power_w") or 0.0),
                    "priority": int(device.get("priority") or 3),
                    "efficiency": float(device.get("efficiency") or 1.0),
                }
            )
            seen_names.add(device_key)

        for device_key, stats in usage_map.items():
            if device_key in seen_names:
                continue
            name = stats["name"]
            if name not in cls._device_states:
                cls._device_states[name] = True
            result.append(
                {
                    "name": name,
                    "device_id": device_key,
                    "device_type": "appliance",
                    "location": "Home",
                    "average_usage": stats["average_usage"],
                    "share": stats["share"],
                    "is_on": cls._device_states[name],
                }
            )

        return sorted(result, key=lambda device: str(device["name"]).lower())

    @classmethod
    def _sync_dataset_devices(cls) -> None:
        """Register the union of all dataset devices without changing states."""
        if cls._dataset_devices_synced:
            return
        registered_devices = db.get_devices()
        registered = {
            str(device.get("device_id", "")).strip().lower()
            for device in registered_devices
        }
        for device_id in DatasetService.all_dataset_device_columns():
            normalized_id = cls._device_key(device_id)
            if not normalized_id:
                continue
            profile = cls._default_power_profile(normalized_id)
            existing = next(
                (device for device in registered_devices if str(device.get("device_id", "")).strip().lower() == normalized_id),
                None,
            )
            if existing and normalized_id in registered:
                if (
                    float(existing.get("rated_power_w") or 100.0) == 100.0
                    and float(existing.get("standby_power_w") or 0.0) == 0.0
                    and float(existing.get("efficiency") or 1.0) == 1.0
                ):
                    db.update_device_metadata(normalized_id, {**existing, **profile})
                continue
            db.register_device(
                {
                    "device_id": normalized_id,
                    "device_type": "appliance",
                    "name": DatasetService._display_name(device_id),
                    "location": "Home",
                    "is_active": True,
                    **profile,
                }
            )
            registered.add(normalized_id)
        cls._dataset_devices_synced = True

    @classmethod
    def add_device(
        cls,
        *,
        name: str,
        device_type: str,
        location: str,
        quantity: int = 1,
        rated_power_w: float = 100.0,
        standby_power_w: float = 0.0,
        priority: int = 3,
        efficiency: float = 1.0,
        operating_state: str = "on",
    ) -> dict[str, object]:
        normalized_name = name.strip()
        normalized_type = device_type.strip().lower()
        normalized_location = location.strip() or "Home"
        normalized_quantity = max(1, int(quantity))
        device_id = cls._device_key(normalized_name)

        db.register_device(
            {
                "device_id": device_id,
                "device_type": normalized_type,
                "name": normalized_name,
                "location": normalized_location,
                "is_active": True,
                "rated_power_w": rated_power_w,
                "standby_power_w": standby_power_w,
                "priority": priority,
                "efficiency": efficiency,
                "operating_state": operating_state,
            }
        )
        cls._device_states[normalized_name] = operating_state != "off"
        state_event = db.record_device_state(
            device_id,
            normalized_name,
            operating_state,
            changed_at=datetime.now(timezone.utc),
        )

        return {
            "name": normalized_name,
            "device_id": device_id,
            "device_type": normalized_type,
            "location": normalized_location,
            "quantity": normalized_quantity,
            "average_usage": 0.0,
            "share": 0.0,
            "is_on": operating_state != "off",
            "changed_at": state_event["changed_at"],
            "operating_state": operating_state,
            "rated_power_w": rated_power_w,
            "standby_power_w": standby_power_w,
            "priority": priority,
            "efficiency": efficiency,
        }

    @classmethod
    def update_device(
        cls,
        *,
        device_id: str,
        name: str,
        device_type: str,
        location: str,
        rated_power_w: float = 100.0,
        standby_power_w: float = 0.0,
        priority: int = 3,
        efficiency: float = 1.0,
        operating_state: str = "on",
    ) -> dict[str, object]:
        normalized_name = name.strip()
        normalized_type = device_type.strip().lower()
        normalized_location = location.strip() or "Home"
        current_state = cls._device_states.get(device_id, cls._device_states.get(normalized_name, True))
        db.update_device(
            device_id,
            {
                "name": normalized_name,
                "device_type": normalized_type,
                "location": normalized_location,
                "is_active": current_state,
            },
        )
        db.update_device_metadata(device_id, locals())
        cls._device_states.pop(device_id, None)
        cls._device_states[normalized_name] = current_state
        return {
            "name": normalized_name,
            "device_id": device_id,
            "device_type": normalized_type,
            "location": normalized_location,
            "is_on": current_state,
            "operating_state": operating_state if operating_state != "on" else ("on" if current_state else "off"),
            "rated_power_w": rated_power_w,
            "standby_power_w": standby_power_w,
            "priority": priority,
            "efficiency": efficiency,
        }

    @classmethod
    def delete_device(cls, device_id: str) -> dict[str, object]:
        db.delete_device(device_id)
        cls._device_states.pop(device_id, None)
        return {"status": "success", "device_id": device_id}

    @classmethod
    def active_device_map(cls) -> dict[str, bool]:
        """Return the live toggle state keyed by canonical device id.

        The canonical form (lowercase, spaces as underscores) matches the
        appliance-column keys that DatasetService._apply_device_states looks
        up in the CSV rows, so toggled dataset-derived devices actually get
        zeroed out of analytics.
        """
        return {
            cls._device_key(name): bool(is_on)
            for name, is_on in cls._device_states.items()
            if is_on is not None
        }

    @classmethod
    def current_load(cls) -> dict[str, object]:
        total_power_w = 0.0
        devices = []
        for device in db.get_devices():
            name = str(device.get("name") or device.get("device_id"))
            state = str(device.get("operating_state") or ("on" if device.get("is_active", True) else "off"))
            if name in cls._device_states and state != "standby":
                state = "on" if cls._device_states[name] else "off"
            power_w = cls._power_for(device, state)
            total_power_w += power_w
            devices.append({"name": name, "state": state, "power_w": round(power_w, 3)})
        return {
            "current_load_w": round(total_power_w, 3),
            "current_load_kw": round(total_power_w / 1000.0, 3),
            "devices": devices,
            "calculated_at": datetime.now(timezone.utc).isoformat(),
        }

    @classmethod
    def _record_elapsed_energy(
        cls,
        device: dict[str, object],
        previous_state: str,
        previous_timestamp: str,
        changed_at: datetime,
    ) -> float:
        try:
            started_at = datetime.fromisoformat(previous_timestamp)
            elapsed_hours = max(0.0, (changed_at - started_at).total_seconds() / 3600.0)
        except (TypeError, ValueError):
            return 0.0
        power_w = cls._power_for(device, previous_state)
        energy_kwh = round(power_w * elapsed_hours / 1000.0, 6)
        if energy_kwh > 0:
            db.insert_reading(
                {
                    "timestamp": changed_at.isoformat(),
                    "device_id": device.get("device_id", "unknown"),
                    "device_type": device.get("device_type", "appliance"),
                    "power": power_w,
                    "energy_consumption": energy_kwh,
                }
            )
        return energy_kwh

    @classmethod
    def toggle_device(cls, device_name: str) -> dict[str, object]:
        if device_name not in cls._device_states:
            cls._device_states[device_name] = True
        cls._device_states[device_name] = not cls._device_states[device_name]
        device_id = cls._device_key(device_name)

        registered_ids = {str(device.get("device_id", "")).strip().lower() for device in db.get_devices()}
        if device_id not in registered_ids:
            # Persist the device so its live ON/OFF state survives a restart
            # and is visible to the analytics device-state map.
            db.register_device(
                {
                    "device_id": device_id,
                    "device_type": "appliance",
                    "name": device_name,
                    "location": "Home",
                }
            )
        device = next((item for item in db.get_devices() if item.get("device_id") == device_id), {})
        previous_events = db.get_device_state_events(device_id, limit=1)
        changed_at = datetime.now(timezone.utc)
        elapsed_energy_kwh = 0.0
        if previous_events:
            elapsed_energy_kwh = cls._record_elapsed_energy(
                device,
                previous_events[-1]["state"],
                previous_events[-1]["changed_at"],
                changed_at,
            )
        db.update_device_status(device_id, cls._device_states[device_name])
        current_device = next((device for device in db.get_devices() if device.get("device_id") == device_id), {})
        db.update_device_metadata(
            device_id,
            {
                **current_device,
                "operating_state": "on" if cls._device_states[device_name] else "off",
            },
        )
        state_event = db.record_device_state(
            device_id,
            device_name,
            "on" if cls._device_states[device_name] else "off",
            changed_at=changed_at,
        )
        load = cls.current_load()
        db.insert_reading(
            {
                "timestamp": state_event["changed_at"],
                "device_id": "household",
                "device_type": "aggregate",
                "power": load["current_load_w"],
                "energy_consumption": 0.0,
            }
        )

        # Publish the control command over MQTT when the broker link is active
        # (no-op when disabled - the software-only default).
        try:
            from app.services.mqtt_service import mqtt_service
            command = "off" if not cls._device_states[device_name] else "on"
            mqtt_service.send_command(device_id, command)
        except Exception:
            pass

        return {
            "name": device_name,
            "is_on": cls._device_states[device_name],
            "changed_at": state_event["changed_at"],
            "state": state_event["state"],
            "current_load_w": load["current_load_w"],
            "current_load_kw": load["current_load_kw"],
            "elapsed_energy_kwh": elapsed_energy_kwh,
        }

    @classmethod
    def get_state_events(cls, device_id: str, limit: int = 100) -> list[dict[str, object]]:
        return db.get_device_state_events(device_id, limit)
