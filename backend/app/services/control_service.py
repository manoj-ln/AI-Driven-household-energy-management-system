from app.database.db import db
from app.services.dataset_service import DatasetService


class ControlService:
    _device_states: dict[str, bool] = {}

    @staticmethod
    def _device_key(value: str) -> str:
        return value.strip().lower().replace(" ", "_")

    @classmethod
    def get_devices(cls) -> list[dict[str, object]]:
        usage_map = {
            cls._device_key(device["name"]): device
            for device in DatasetService.get_device_breakdown()
        }

        registered_devices = db.get_devices()
        result: list[dict[str, object]] = []
        seen_names: set[str] = set()

        for device in registered_devices:
            name = device.get("name") or device.get("device_id") or "Unnamed Device"
            device_key = cls._device_key(str(device.get("device_id") or name))
            stats = usage_map.get(device_key, {})
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
    def add_device(
        cls,
        *,
        name: str,
        device_type: str,
        location: str,
        quantity: int = 1,
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
            }
        )
        cls._device_states[normalized_name] = True

        return {
            "name": normalized_name,
            "device_id": device_id,
            "device_type": normalized_type,
            "location": normalized_location,
            "quantity": normalized_quantity,
            "average_usage": 0.0,
            "share": 0.0,
            "is_on": True,
        }

    @classmethod
    def update_device(
        cls,
        *,
        device_id: str,
        name: str,
        device_type: str,
        location: str,
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
        cls._device_states.pop(device_id, None)
        cls._device_states[normalized_name] = current_state
        return {
            "name": normalized_name,
            "device_id": device_id,
            "device_type": normalized_type,
            "location": normalized_location,
            "is_on": current_state,
        }

    @classmethod
    def delete_device(cls, device_id: str) -> dict[str, object]:
        db.delete_device(device_id)
        cls._device_states.pop(device_id, None)
        return {"status": "success", "device_id": device_id}

    @classmethod
    def toggle_device(cls, device_name: str) -> dict[str, object]:
        if device_name not in cls._device_states:
            cls._device_states[device_name] = True
        cls._device_states[device_name] = not cls._device_states[device_name]
        device_id = cls._device_key(device_name)
        db.update_device_status(device_id, cls._device_states[device_name])
        return {
            "name": device_name,
            "is_on": cls._device_states[device_name],
        }
