import json
from datetime import datetime
from pathlib import Path
from typing import Any, List

class Database:
    storage_file = Path(__file__).resolve().parents[2] / "data" / "energy_store.json"

    @classmethod
    def _ensure_storage(cls) -> None:
        cls.storage_file.parent.mkdir(parents=True, exist_ok=True)
        if not cls.storage_file.exists():
            cls.storage_file.write_text("[]", encoding="utf-8")

    @classmethod
    def insert_reading(cls, record: dict) -> None:
        cls._ensure_storage()
        data = json.loads(cls.storage_file.read_text(encoding="utf-8"))
        data.append(record)
        cls.storage_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def get_recent_readings(cls, limit: int = 24) -> list[dict[str, Any]]:
        cls._ensure_storage()
        data = json.loads(cls.storage_file.read_text(encoding="utf-8"))
        return data[-limit:]

    @classmethod
    def get_devices(cls) -> List[dict]:
        # Return mock devices for now
        return [
            {
                "id": 1,
                "device_id": "living_room_fan",
                "device_type": "appliance",
                "name": "Living Room Fan",
                "location": "living_room",
                "is_active": True,
                "last_seen": datetime.utcnow().isoformat(),
                "ip_address": None
            }
        ]

    @classmethod
    def register_device(cls, device_data: dict) -> None:
        # Mock implementation
        pass

    @classmethod
    def get_energy_stats(cls, device_id: str = None, hours: int = 24) -> dict:
        return {"total_energy": 0, "avg_power": 0, "max_power": 0, "min_power": 0, "count": 0}
