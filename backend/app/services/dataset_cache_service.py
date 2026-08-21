import csv
from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import Any


class DatasetCacheService:
    _metadata_cache: dict[str, tuple[float, dict[str, Any]]] = {}
    _csv_cache: dict[str, tuple[float, list[dict[str, Any]]]] = {}
    _wide_metadata_fields = {
        "Timestamp", "timestamp",
        "Hour", "hour",
        "DayOfWeek", "day_of_week",
        "IsWeekend", "is_weekend",
        "Temperature", "temperature", "temperature_c",
        "Humidity", "humidity",
        "Total_Consumption", "total_consumption", "TotalHouseholdConsumption",
        "Year", "Month", "Week", "Day", "Minute",
        "Season", "Weather",
        "OccupancyLevel", "ElectricityTariff",
        "RenewableEnergyStatus", "PowerOutageStatus",
        "DeviceStatus", "DevicePowerConsumption",
        "EstimatedCost", "CarbonEmissions", "AnomalyLabel",
        "SolarGeneration", "BatterySOC", "GridImport", "GridExport",
        "device_id", "energy_kwh",
    }

    @staticmethod
    def cache_path(dataset_path: Path) -> Path:
        return dataset_path.with_suffix(".cache.json")

    @staticmethod
    def safe_float(value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def clone_row(row: dict[str, Any]) -> dict[str, Any]:
        return {
            **row,
            "appliances": dict(row.get("appliances", {})),
        }

    @classmethod
    def _cache_row_to_internal(cls, row: dict[str, Any]) -> dict[str, Any]:
        timestamp = row.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        return {
            "timestamp": timestamp,
            "hour": int(row.get("hour", timestamp.hour if timestamp else 0)),
            "day_of_week": int(row.get("day_of_week", timestamp.weekday() if timestamp else 0)),
            "is_weekend": int(row.get("is_weekend", 0)),
            "temperature": round(cls.safe_float(row.get("temperature"), 24.0), 2),
            "total_consumption": round(cls.safe_float(row.get("total_consumption"), 0.0), 6),
            "appliances": {
                str(name): round(cls.safe_float(value, 0.0), 6)
                for name, value in dict(row.get("appliances", {})).items()
                if cls.safe_float(value, 0.0) > 0
            },
        }

    @classmethod
    def load_metadata(cls, dataset_path: Path) -> dict[str, Any] | None:
        cache_path = cls.cache_path(dataset_path)
        if not cache_path.exists() or cache_path.stat().st_size == 0:
            return None

        cache_key = str(cache_path.resolve())
        modified_at = cache_path.stat().st_mtime
        cached = cls._metadata_cache.get(cache_key)
        if cached and cached[0] == modified_at:
            return cached[1]

        payload = json.loads(cache_path.read_text(encoding="utf-8"))
        payload["recent_minute_rows"] = [
            cls._cache_row_to_internal(row)
            for row in payload.get("recent_minute_rows", [])
        ]
        payload["recent_hourly_rows"] = [
            cls._cache_row_to_internal(row)
            for row in payload.get("recent_hourly_rows", [])
        ]
        payload["row_count"] = int(payload.get("row_count", 0))
        payload["cadence_minutes"] = int(payload.get("cadence_minutes", 60))
        payload["coverage_days"] = round(float(payload.get("coverage_days", 0.0)), 2)
        cls._metadata_cache[cache_key] = (modified_at, payload)
        return payload

    @classmethod
    def dataset_details(cls, dataset_path: Path) -> dict[str, Any]:
        metadata = cls.load_metadata(dataset_path)
        if metadata and metadata.get("device_columns"):
            return {
                "dataset_name": dataset_path.name,
                "row_count": int(metadata.get("source_row_count", metadata.get("row_count", 0))),
                "cached_row_count": int(metadata.get("cached_row_count", metadata.get("row_count", 0))),
                "start": metadata.get("start"),
                "end": metadata.get("end"),
                "source_start": metadata.get("source_start", metadata.get("start")),
                "source_end": metadata.get("source_end", metadata.get("end")),
                "coverage_days": round(float(metadata.get("coverage_days", 0.0)), 2),
                "cadence_minutes": int(metadata.get("cadence_minutes", 60)),
                "device_count": len(metadata.get("device_columns", [])),
                "device_columns": metadata.get("device_columns", []),
            }
        
        # Fallback to reading the CSV header if metadata is missing or incomplete
        device_cols = []
        row_count = 0
        if dataset_path.exists():
            with dataset_path.open("r", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                if reader.fieldnames:
                    # Filter out metadata fields to get only appliances
                    device_cols = [f for f in reader.fieldnames if f not in cls._wide_metadata_fields]
            # Efficiently count rows
            row_count = sum(1 for _ in dataset_path.open("r", encoding="utf-8")) - 1

        return {
            "dataset_name": dataset_path.name,
            "row_count": row_count,
            "start": None,
            "end": None,
            "coverage_days": 0.0,
            "cadence_minutes": None,
            "device_count": len(device_cols),
            "device_columns": device_cols,
        }

    @classmethod
    def _load_wide_csv_dataset(cls, data_iterator) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for row in data_iterator:
            timestamp_raw = str(row.get("Timestamp") or row.get("timestamp") or "").strip()
            if not timestamp_raw:
                continue
            try:
                timestamp = datetime.fromisoformat(timestamp_raw)
            except ValueError:
                continue

            appliances = {
                field: round(cls.safe_float(row.get(field), 0.0), 6)
                for field in (row.keys() - cls._wide_metadata_fields)
                if cls.safe_float(row.get(field), 0.0) > 0
            }
            computed_total = round(sum(appliances.values()), 6)
            stored_total = cls.safe_float(row.get("Total_Consumption") or row.get("total_consumption"), computed_total)
            total_consumption = round(stored_total if stored_total > 0 else computed_total, 6)
            if not appliances and total_consumption > 0:
                appliances = {"home_energy": total_consumption}
            if not appliances:
                continue

            rows.append(
                {
                    "timestamp": timestamp,
                    "hour": int(cls.safe_float(row.get("Hour"), timestamp.hour)),
                    "day_of_week": int(cls.safe_float(row.get("DayOfWeek"), timestamp.weekday())),
                    "is_weekend": int(cls.safe_float(row.get("IsWeekend"), 1 if timestamp.weekday() >= 5 else 0)),
                    "temperature": round(cls.safe_float(row.get("Temperature") or row.get("temperature_c"), 24.0), 2),
                    "total_consumption": total_consumption,
                    "appliances": appliances,
                }
            )

        return rows

    @classmethod
    def _load_long_csv_dataset(cls, reader: csv.DictReader) -> list[dict[str, Any]]:
        aggregated: dict[str, dict[str, Any]] = {}
        for row in reader:
            timestamp_raw = str(row.get("timestamp", "")).strip()
            if not timestamp_raw:
                continue
            try:
                timestamp = datetime.fromisoformat(timestamp_raw)
            except ValueError:
                continue

            bucket = aggregated.setdefault(
                timestamp.isoformat(),
                {
                    "timestamp": timestamp,
                    "hour": timestamp.hour,
                    "day_of_week": timestamp.weekday(),
                    "is_weekend": 1 if timestamp.weekday() >= 5 else 0,
                    "temperature_total": 0.0,
                    "temperature_count": 0,
                    "total_consumption": 0.0,
                    "appliances": {},
                },
            )
            energy = max(0.0, cls.safe_float(row.get("energy_kwh"), 0.0))
            device = str(row.get("device_id", "home_energy")).strip() or "home_energy"
            bucket["total_consumption"] += energy
            bucket["appliances"][device] = round(bucket["appliances"].get(device, 0.0) + energy, 6)
            temperature = row.get("temperature_c")
            if temperature not in (None, ""):
                bucket["temperature_total"] += cls.safe_float(temperature, 24.0)
                bucket["temperature_count"] += 1

        rows: list[dict[str, Any]] = []
        for bucket in aggregated.values():
            temperature = bucket["temperature_total"] / bucket["temperature_count"] if bucket["temperature_count"] else 24.0
            rows.append(
                {
                    "timestamp": bucket["timestamp"],
                    "hour": bucket["hour"],
                    "day_of_week": bucket["day_of_week"],
                    "is_weekend": bucket["is_weekend"],
                    "temperature": round(temperature, 2),
                    "total_consumption": round(bucket["total_consumption"], 6),
                    "appliances": bucket["appliances"],
                }
            )
        return rows

    @classmethod
    def load_csv(cls, dataset_path: Path) -> list[dict[str, Any]]:
        if not dataset_path.exists() or dataset_path.stat().st_size == 0:
            return []
        cache_key = str(dataset_path.resolve())
        modified_at = dataset_path.stat().st_mtime
        cached = cls._csv_cache.get(cache_key)
        if cached and cached[0] == modified_at:
            return cached[1]

        with dataset_path.open("r", encoding="utf-8") as handle:
            # Check format from header
            header_line = handle.readline().lower()
            handle.seek(0)
            reader = csv.DictReader(handle)
            
            # If it's a wide dataset (socioeconomic profiles), it's large. Tail it.
            if "total_consumption" in header_line or "totalhouseholdconsumption" in header_line or "fridge_main" in header_line or "refrigerator_main" in header_line:
                from collections import deque
                # Last 10k rows is ~1 week of 1-min data. Perfect for analytics.
                # DictReader is an iterator, so we can deque it.
                data_iterator = deque(reader, maxlen=10000)
                rows = cls._load_wide_csv_dataset(data_iterator)
            else:
                # Long format or small file
                rows = cls._load_long_csv_dataset(reader)

        sorted_rows = sorted(rows, key=lambda item: item["timestamp"])
        cls._csv_cache[cache_key] = (modified_at, sorted_rows)
        return sorted_rows

    @classmethod
    def aggregate_rows(cls, rows: list[dict[str, Any]], bucket_minutes: int) -> list[dict[str, Any]]:
        if not rows:
            return []
        aggregated: dict[datetime, dict[str, Any]] = {}
        bucket_minutes = max(1, int(bucket_minutes))

        for row in rows:
            timestamp = row["timestamp"].replace(second=0, microsecond=0)
            timestamp = timestamp - timedelta(minutes=timestamp.minute % bucket_minutes)
            bucket = aggregated.setdefault(
                timestamp,
                {
                    "timestamp": timestamp,
                    "hour": timestamp.hour,
                    "day_of_week": timestamp.weekday(),
                    "is_weekend": 1 if timestamp.weekday() >= 5 else 0,
                    "temperature_total": 0.0,
                    "temperature_count": 0,
                    "total_consumption": 0.0,
                    "appliances": {},
                },
            )
            bucket["total_consumption"] += float(row.get("total_consumption", 0.0))
            bucket["temperature_total"] += float(row.get("temperature", 24.0))
            bucket["temperature_count"] += 1
            for device_name, value in row.get("appliances", {}).items():
                bucket["appliances"][device_name] = round(bucket["appliances"].get(device_name, 0.0) + float(value), 6)

        normalized = []
        for bucket in sorted(aggregated.values(), key=lambda item: item["timestamp"]):
            temperature = bucket["temperature_total"] / bucket["temperature_count"] if bucket["temperature_count"] else 24.0
            normalized.append(
                {
                    "timestamp": bucket["timestamp"],
                    "hour": bucket["hour"],
                    "day_of_week": bucket["day_of_week"],
                    "is_weekend": bucket["is_weekend"],
                    "temperature": round(temperature, 2),
                    "total_consumption": round(bucket["total_consumption"], 6),
                    "appliances": bucket["appliances"],
                }
            )
        return normalized

    @classmethod
    def rows_for_minutes_window(cls, rows: list[dict[str, Any]], minutes: int) -> list[dict[str, Any]]:
        if not rows:
            return []
        cutoff = rows[-1]["timestamp"] - timedelta(minutes=max(1, int(minutes)))
        return [cls.clone_row(row) for row in rows if row["timestamp"] >= cutoff]

    @staticmethod
    def average_usage_per_hour(total_energy: float, rows: list[dict[str, Any]]) -> float:
        if not rows:
            return 0.0
        duration_hours = max((rows[-1]["timestamp"] - rows[0]["timestamp"]).total_seconds() / 3600.0, 1.0)
        return round(total_energy / duration_hours, 3)
