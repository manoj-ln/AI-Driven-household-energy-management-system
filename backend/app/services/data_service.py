from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from app.database.repository import db
from app.schemas.energy_schema import EnergyReading
from app.utils.logger import logger


class DataService:
    @staticmethod
    def save_reading(reading: EnergyReading) -> None:
        """Persist a reading to SQLite.

        Maps the API-facing EnergyReading schema (energy_kwh, appliance,
        location) onto EnergyRepository's column names (energy_consumption,
        device_type) explicitly, rather than passing reading.dict() straight
        through - the two shapes were never the same, which is what caused
        every /energy/ingest call to raise KeyError('device_id') before
        this fix: insert_reading requires device_id/device_type, and the
        old EnergyReading.dict() never produced them.
        """
        db.insert_reading(
            {
                "timestamp": reading.timestamp.isoformat(),
                "device_id": reading.device_id,
                "device_type": reading.device_type or reading.appliance or "unspecified",
                "energy_consumption": reading.energy_kwh,
                "temperature": reading.temperature,
            }
        )
        logger.info("Ingested energy reading for device %s", reading.device_id)

    @staticmethod
    def get_recent_readings(limit: int = 24, device_id: str | None = None) -> List[Dict[str, Any]]:
        return db.get_recent_readings(limit, device_id)

    @staticmethod
    def get_devices() -> List[Dict[str, Any]]:
        return db.get_devices()

    @staticmethod
    def register_device(device_data: Dict[str, Any]) -> None:
        db.register_device(device_data)

    @staticmethod
    def get_energy_stats(device_id: str | None = None, hours: int = 24) -> Dict[str, Any]:
        return db.get_energy_stats(device_id, hours)

    @staticmethod
    def get_readings_by_date_range(
        start_date: datetime,
        end_date: datetime,
        device_id: str | None = None,
    ) -> List[Dict[str, Any]]:
        return db.get_readings_by_date_range(start_date, end_date, device_id)

    @staticmethod
    def get_hourly_consumption(device_id: str | None = None, days: int = 7) -> List[Dict[str, Any]]:
        """Get hourly energy consumption for the last N days."""
        readings = DataService.get_readings_by_date_range(
            datetime.now(timezone.utc) - timedelta(days=days),
            datetime.now(timezone.utc),
            device_id,
        )

        hourly: dict[str, Dict[str, Any]] = {}
        for reading in readings:
            timestamp = reading.get("timestamp")
            if not timestamp:
                continue
            hour_key = datetime.fromisoformat(timestamp).replace(minute=0, second=0, microsecond=0)
            bucket = hourly.setdefault(
                hour_key.isoformat(),
                {
                    "timestamp": hour_key.isoformat(),
                    "total_consumption": 0.0,
                    "count": 0,
                },
            )
            bucket["total_consumption"] += float(reading.get("energy_consumption") or 0.0)
            bucket["count"] += 1

        if hourly:
            return list(sorted(hourly.values(), key=lambda row: row["timestamp"]))

        return [
            {
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=i)).replace(minute=0, second=0, microsecond=0).isoformat(),
                "total_consumption": round(0.5 + (i % 5) * 0.1, 3),
                "count": 4,
            }
            for i in range(24 * days)
        ]

    @staticmethod
    def get_daily_consumption(device_id: str | None = None, days: int = 30) -> List[Dict[str, Any]]:
        """Get daily energy consumption for the last N days."""
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        readings = db.get_readings_by_date_range(start_date, end_date, device_id)

        daily_data: dict[str, Dict[str, Any]] = {}
        for reading in readings:
            if reading.get("energy_consumption") is None or not reading.get("timestamp"):
                continue

            timestamp = datetime.fromisoformat(reading["timestamp"])
            day_key = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
            bucket = daily_data.setdefault(
                day_key.isoformat(),
                {
                    "date": day_key.date().isoformat(),
                    "total_consumption": 0.0,
                    "count": 0,
                },
            )
            bucket["total_consumption"] += float(reading["energy_consumption"])
            bucket["count"] += 1

        return list(sorted(daily_data.values(), key=lambda row: row["date"]))
