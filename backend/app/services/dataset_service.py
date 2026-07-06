from collections import Counter
from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import Any

from app.database.db import db
from app.services.dataset_cache_service import DatasetCacheService


class DatasetService:
    _dataset_mode = "auto"
    _valid_modes = {"auto", "real_only", "synthetic_demo"}
    _dataset_dir = Path(__file__).resolve().parents[2] / "data" / "datasets"
    _selected_dataset = "energy_last_24_hours.csv"
    _settings_file = Path(__file__).resolve().parents[2] / "data" / "dataset_preferences.json"

    @classmethod
    def _ensure_settings_storage(cls) -> None:
        cls._settings_file.parent.mkdir(parents=True, exist_ok=True)
        if not cls._settings_file.exists():
            payload = {
                "mode": cls._dataset_mode,
                "selected_dataset": cls._selected_dataset,
            }
            cls._settings_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def _load_settings(cls) -> None:
        cls._ensure_settings_storage()
        try:
            payload = json.loads(cls._settings_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = {}
        mode = str(payload.get("mode", cls._dataset_mode)).strip().lower()
        if mode in cls._valid_modes:
            cls._dataset_mode = mode
        selected_dataset = str(payload.get("selected_dataset", cls._selected_dataset)).strip()
        available = cls.list_datasets()
        if selected_dataset and selected_dataset in available:
            cls._selected_dataset = selected_dataset
        elif cls._selected_dataset not in available and available:
            cls._selected_dataset = available[0]

    @classmethod
    def _save_settings(cls) -> None:
        cls._ensure_settings_storage()
        payload = {
            "mode": cls._dataset_mode,
            "selected_dataset": cls._selected_dataset,
        }
        cls._settings_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def _dataset_path(cls, dataset_name: str | None = None) -> Path:
        target_name = dataset_name or cls._selected_dataset
        return cls._dataset_dir / target_name

    @classmethod
    def _active_dataset_metadata(cls) -> dict[str, Any] | None:
        cls._load_settings()
        return DatasetCacheService.load_metadata(cls._dataset_path())

    @classmethod
    def _get_dataset_details(cls, dataset_name: str | None = None) -> dict[str, Any]:
        return DatasetCacheService.dataset_details(cls._dataset_path(dataset_name))

    @classmethod
    def _selected_dataset_rows(cls, *, hourly: bool) -> list[dict[str, Any]]:
        metadata = cls._active_dataset_metadata()
        if metadata:
            key = "recent_hourly_rows" if hourly else "recent_minute_rows"
            rows = metadata.get(key)
            if rows is not None:
                return [DatasetCacheService.clone_row(row) for row in rows]

        rows = DatasetCacheService.load_csv(cls._dataset_path())
        if not hourly:
            return rows
        return DatasetCacheService.aggregate_rows(rows, 60)

    @classmethod
    def _selected_dataset_available(cls) -> bool:
        dataset_path = cls._dataset_path()
        metadata = DatasetCacheService.load_metadata(dataset_path)
        if metadata:
            return True
        return dataset_path.exists() and dataset_path.stat().st_size > 0

    @classmethod
    def _use_selected_dataset(cls) -> bool:
        cls._load_settings()
        return cls._dataset_mode != "real_only" and cls._selected_dataset_available()

    @classmethod
    def get_dataset_mode(cls) -> dict[str, Any]:
        cls._load_settings()
        return {
            "mode": cls._dataset_mode,
            "selected_dataset": cls._selected_dataset,
            "supported_modes": sorted(cls._valid_modes),
            "description": {
                "auto": "Use the selected dashboard dataset across analytics, predictions, graphs, and reports.",
                "real_only": "Use only ingested real data.",
                "synthetic_demo": "Always use the selected dashboard dataset.",
            },
            "dataset_details": cls._get_dataset_details(cls._selected_dataset),
        }

    @classmethod
    def set_dataset_mode(cls, mode: str) -> dict[str, Any]:
        cls._load_settings()
        normalized = str(mode or "").strip().lower()
        if normalized not in cls._valid_modes:
            return {
                "status": "error",
                "message": f"Unsupported mode: {mode}",
                "supported_modes": sorted(cls._valid_modes),
            }
        cls._dataset_mode = normalized
        cls._save_settings()
        return {"status": "success", **cls.get_dataset_mode()}

    @classmethod
    def list_datasets(cls) -> list[str]:
        cls._dataset_dir.mkdir(parents=True, exist_ok=True)
        return sorted(path.name for path in cls._dataset_dir.glob("*.csv"))

    @classmethod
    def select_dataset(cls, dataset_name: str) -> dict[str, Any]:
        cls._load_settings()
        normalized = str(dataset_name or "").strip()
        available = cls.list_datasets()
        if normalized not in available:
            return {"status": "error", "message": f"Dataset not found: {dataset_name}", "available_datasets": available}
        cls._selected_dataset = normalized
        # Automatically switch to synthetic mode so the user sees the data
        if cls._dataset_mode == "real_only":
            cls._dataset_mode = "synthetic_demo"
        cls._save_settings()
        return {
            "status": "success",
            "selected_dataset": cls._selected_dataset,
            "available_datasets": available,
            "dataset_details": cls._get_dataset_details(cls._selected_dataset),
        }

    @staticmethod
    def _active_device_map() -> dict[str, bool]:
        devices = db.get_devices()
        return {
            str(device.get("device_id", "")).strip().lower(): bool(device.get("is_active", True))
            for device in devices
        }

    @staticmethod
    def _season_for_month(month: int) -> str:
        if month in (12, 1, 2):
            return "❄️ Winter"
        if month in (3, 4, 5):
            return "☀️ Summer"
        if month in (6, 7, 8, 9):
            return "🌧️ Monsoon"
        return "🍂 Post-Monsoon"

    @staticmethod
    def _day_period_for_hour(hour: int) -> str:
        if 4 <= hour < 7:
            return "early_morning"
        if 7 <= hour < 12:
            return "morning"
        if 12 <= hour < 17:
            return "afternoon"
        if 17 <= hour < 21:
            return "evening"
        if 21 <= hour < 24:
            return "night"
        return "late_night"

    @staticmethod
    def _display_name(name: str) -> str:
        lowered = str(name or "").strip().lower()
        if lowered.startswith("esp32_"):
            suffix = lowered.split("_")[-1]
            return f"Home Device {suffix}"
        cleaned = str(name or "unknown_device").replace("_", " ").replace("-", " ").strip()
        return " ".join(word.capitalize() for word in cleaned.split())

    @staticmethod
    def _get_category(name: str) -> str:
        name_lower = str(name or "").lower()
        if "bulb" in name_lower or "light" in name_lower or "lamp" in name_lower:
            return "Lighting"
        if "ac" in name_lower or "air condition" in name_lower or "fan" in name_lower or "cooler" in name_lower:
            return "Cooling"
        if "fridge" in name_lower or "refrigerator" in name_lower or "kitchen" in name_lower or "oven" in name_lower or "microwave" in name_lower or "induction" in name_lower or "kettle" in name_lower or "cooker" in name_lower:
            return "Kitchen"
        if "washing" in name_lower or "iron" in name_lower or "vacuum" in name_lower or "heater" in name_lower or "geyser" in name_lower:
            return "Utility"
        if "tv" in name_lower or "console" in name_lower or "speaker" in name_lower or "theater" in name_lower or "laptop" in name_lower or "pc" in name_lower:
            return "Entertainment"
        if "security" in name_lower or "camera" in name_lower or "lock" in name_lower or "alarm" in name_lower:
            return "Security"
        if "health" in name_lower or "purifier" in name_lower or "treadmill" in name_lower or "gym" in name_lower:
            return "Health"
        if "charge" in name_lower or "ev" in name_lower or "ups" in name_lower or "inverter" in name_lower:
            return "Power"
        return "Others"

    @classmethod
    def _device_signature(cls, name: str) -> int:
        return sum(ord(char) for char in str(name or "").lower())

    @classmethod
    def _device_profile(cls, name: str) -> dict[str, Any]:
        lowered = str(name or "").strip().lower()
        signature = cls._device_signature(lowered)
        profile = {
            "preferred_hours": {7, 8, 9, 18, 19, 20},
            "peak_boost": 1.18,
            "off_peak_floor": 0.55,
            "volatility": 0.06,
        }
        if "heater" in lowered:
            profile.update({"preferred_hours": {5, 6, 7, 20, 21, 22, 23}, "peak_boost": 1.34, "off_peak_floor": 0.42, "volatility": 0.08})
        elif "fan" in lowered:
            profile.update({"preferred_hours": {10, 11, 12, 13, 14, 15, 20, 21}, "peak_boost": 1.22, "off_peak_floor": 0.62, "volatility": 0.07})
        elif "bulb" in lowered or "light" in lowered or "lamp" in lowered:
            profile.update({"preferred_hours": {5, 6, 18, 19, 20, 21, 22, 23}, "peak_boost": 1.28, "off_peak_floor": 0.28, "volatility": 0.05})
        elif "washing" in lowered:
            profile.update({"preferred_hours": {8, 9, 10, 14, 15, 16}, "peak_boost": 1.24, "off_peak_floor": 0.25, "volatility": 0.09})
        elif "refrigerator" in lowered or "fridge" in lowered:
            profile.update({"preferred_hours": set(range(24)), "peak_boost": 1.02, "off_peak_floor": 0.88, "volatility": 0.03})
        elif "home device" in lowered or "esp32" in lowered:
            profile.update({"preferred_hours": {9, 10, 11, 12, 13, 18, 19, 20}, "peak_boost": 1.1, "off_peak_floor": 0.6, "volatility": 0.08})
        profile["phase"] = signature % 6
        profile["signature"] = signature
        return profile

    @classmethod
    def _device_activity_factor(cls, name: str, hour: int, minute_bucket: int = 0) -> float:
        profile = cls._device_profile(name)
        signature = profile["signature"]
        wave_seed = ((hour + profile["phase"] + minute_bucket) % 6) - 2
        wave = 1 + (wave_seed * profile["volatility"])
        if hour in profile["preferred_hours"]:
            return round(profile["peak_boost"] * wave, 3)
        if 0 <= hour < 5 and ("bulb" in str(name).lower() or "light" in str(name).lower()):
            return round(max(0.12, profile["off_peak_floor"] * 0.55) * wave, 3)
        if signature % 2 == 0 and 12 <= hour < 16:
            return round(max(profile["off_peak_floor"], 0.78) * wave, 3)
        return round(profile["off_peak_floor"] * wave, 3)

    @classmethod
    def _normalize_readings(cls) -> list[dict[str, Any]]:
        readings = db.get_recent_readings(limit=2000)
        if not readings:
            return []

        buckets: dict[str, dict[str, Any]] = {}
        for reading in readings:
            timestamp_raw = reading.get("timestamp")
            if not timestamp_raw:
                continue
            try:
                timestamp = datetime.fromisoformat(str(timestamp_raw).replace("Z", "+00:00")).replace(tzinfo=None)
            except ValueError:
                continue
            hour_key = timestamp.replace(minute=0, second=0, microsecond=0)
            energy = reading.get("energy_consumption")
            if energy is None:
                power = reading.get("power")
                energy = float(power or 0) / 1000.0
            numeric_energy = float(energy or 0.0)
            if numeric_energy < 0:
                continue

            bucket = buckets.setdefault(
                hour_key.isoformat(),
                {
                    "timestamp": hour_key,
                    "hour": hour_key.hour,
                    "day_of_week": hour_key.weekday(),
                    "is_weekend": 1 if hour_key.weekday() >= 5 else 0,
                    "temperature_total": 0.0,
                    "temperature_count": 0,
                    "total_consumption": 0.0,
                    "appliances": {},
                },
            )
            bucket["total_consumption"] += numeric_energy
            temp_value = reading.get("temperature")
            if temp_value is not None:
                temp_numeric = float(temp_value)
                if -10 <= temp_numeric <= 60:
                    bucket["temperature_total"] += temp_numeric
                    bucket["temperature_count"] += 1

            device_name = str(reading.get("device_id", "unknown_device"))
            bucket["appliances"][device_name] = bucket["appliances"].get(device_name, 0.0) + numeric_energy

        normalized = []
        for bucket in buckets.values():
            temperature = (
                bucket["temperature_total"] / bucket["temperature_count"]
                if bucket["temperature_count"]
                else 24.0
            )
            normalized.append(
                {
                    "timestamp": bucket["timestamp"],
                    "hour": bucket["hour"],
                    "day_of_week": bucket["day_of_week"],
                    "is_weekend": bucket["is_weekend"],
                    "temperature": temperature,
                    "total_consumption": bucket["total_consumption"],
                    "appliances": bucket["appliances"],
                }
            )

        return list(sorted(normalized, key=lambda row: row["timestamp"]))

    @classmethod
    def _hour_factor(cls, hour: int, is_weekend: bool) -> float:
        if 0 <= hour < 5:
            base = 0.52
        elif 5 <= hour < 8:
            base = 0.72
        elif 8 <= hour < 12:
            base = 0.94
        elif 12 <= hour < 17:
            base = 1.02
        elif 17 <= hour < 22:
            base = 1.18
        else:
            base = 0.84
        return round(base * (1.06 if is_weekend else 1.0), 3)

    @classmethod
    def _expand_sparse_data(cls, normalized: list[dict[str, Any]], min_hours: int = 72) -> list[dict[str, Any]]:
        if not normalized:
            return []
        if len(normalized) >= min_hours:
            return normalized

        latest = normalized[-1]
        latest_timestamp = latest["timestamp"]
        device_totals = Counter()
        temperatures = []
        for row in normalized:
            for name, value in row["appliances"].items():
                device_totals[name] += float(value)
            temperatures.append(float(row.get("temperature", 24.0)))

        total_device_energy = sum(device_totals.values()) or 1.0
        device_shares = {
            name: value / total_device_energy
            for name, value in device_totals.items()
        } or {"home_energy": 1.0}

        average_total = sum(float(row["total_consumption"]) for row in normalized) / len(normalized)
        average_temp = sum(temperatures) / len(temperatures) if temperatures else 24.0
        existing = {row["timestamp"].isoformat(): row for row in normalized}

        start_time = latest_timestamp - timedelta(hours=min_hours - 1)
        expanded: list[dict[str, Any]] = []
        rolling_seed = average_total if average_total > 0 else max(float(latest["total_consumption"]), 0.4)

        for offset in range(min_hours):
            ts = start_time + timedelta(hours=offset)
            key = ts.isoformat()
            if key in existing:
                expanded.append(existing[key])
                continue

            factor = cls._hour_factor(ts.hour, ts.weekday() >= 5)
            seasonal_bias = 1.06 if cls._season_for_month(ts.month) == "summer" and 12 <= ts.hour <= 18 else 1.0
            total = round(max(0.05, rolling_seed * factor * seasonal_bias), 3)
            dynamic_weights = {}
            for name, share in device_shares.items():
                activity = cls._device_activity_factor(name, ts.hour)
                dynamic_weights[name] = max(0.001, share * activity)
            weight_total = sum(dynamic_weights.values()) or 1.0
            appliances = {
                name: round(total * (weight / weight_total), 3)
                for name, weight in dynamic_weights.items()
            }
            corrected_total = round(sum(appliances.values()), 3)
            if corrected_total == 0:
                appliances = {name: round(total * share, 3) for name, share in device_shares.items()}
                corrected_total = round(sum(appliances.values()), 3)
            expanded.append(
                {
                    "timestamp": ts,
                    "hour": ts.hour,
                    "day_of_week": ts.weekday(),
                    "is_weekend": 1 if ts.weekday() >= 5 else 0,
                    "temperature": round(average_temp + ((ts.hour - 12) * 0.15), 1),
                    "total_consumption": corrected_total,
                    "appliances": appliances,
                }
            )

        return list(sorted(expanded, key=lambda row: row["timestamp"]))

    @classmethod
    def _fallback_data(cls) -> list[dict[str, Any]]:
        fallback = []
        base_time = datetime.utcnow() - timedelta(hours=168)
        for i in range(168):
            timestamp = base_time + timedelta(hours=i)
            fallback.append(
                {
                    "timestamp": timestamp,
                    "hour": timestamp.hour,
                    "day_of_week": timestamp.weekday(),
                    "is_weekend": 1 if timestamp.weekday() >= 5 else 0,
                    "temperature": 20 + (i % 24) * 0.5,
                    "total_consumption": 0.5 + (i % 24) * 0.1 + (0.1 if i % 50 == 0 else 0),
                    "appliances": {
                        "Heating_Room": 0.167 + (i % 10) * 0.01,
                        "Others_Refrigerator": 0.1,
                        "Kitchen_Induction": 0.066,
                        "Kitchen_Microwave": 0.059,
                        "Kitchen_Kettle": 0.045,
                    },
                }
            )
        return fallback

    @staticmethod
    def _safe_float(value: Any, default: float = 0.0) -> float:
        return DatasetCacheService.safe_float(value, default)

    @classmethod
    def _load_wide_csv_dataset(cls, reader) -> list[dict[str, Any]]:
        return DatasetCacheService._load_wide_csv_dataset(reader)

    @classmethod
    def _load_long_csv_dataset(cls, reader) -> list[dict[str, Any]]:
        return DatasetCacheService._load_long_csv_dataset(reader)

    @classmethod
    def _load_csv_dataset(cls, dataset_name: str) -> list[dict[str, Any]]:
        return DatasetCacheService.load_csv(cls._dataset_path(dataset_name))

    @classmethod
    def _get_data(cls) -> list[dict[str, Any]]:
        cls._load_settings()
        active_map = cls._active_device_map()
        if cls._use_selected_dataset():
            selected_rows = cls._selected_dataset_rows(hourly=False)
            return cls._apply_device_states(selected_rows or cls._fallback_data(), active_map)

        normalized = cls._normalize_readings()
        if cls._dataset_mode == "real_only":
            return cls._apply_device_states(cls._expand_sparse_data(normalized), active_map) if normalized else []
        if normalized:
            return cls._apply_device_states(cls._expand_sparse_data(normalized), active_map)
        return cls._apply_device_states(cls._fallback_data(), active_map)

    @classmethod
    def _get_hourly_data(cls) -> list[dict[str, Any]]:
        cls._load_settings()
        active_map = cls._active_device_map()
        if cls._use_selected_dataset():
            rows = cls._selected_dataset_rows(hourly=True)
            return cls._apply_device_states(rows or cls._fallback_data(), active_map)
        return DatasetCacheService.aggregate_rows(cls._get_data(), 60)

    @classmethod
    def _apply_device_states(cls, data: list[dict[str, Any]], active_map: dict[str, bool]) -> list[dict[str, Any]]:
        if not active_map:
            return data

        adjusted_rows = []
        for row in data:
            appliances = {}
            for device_name, value in row["appliances"].items():
                device_key = str(device_name).strip().lower()
                if active_map.get(device_key, True):
                    appliances[device_name] = value
                else:
                    appliances[device_name] = 0.0
            adjusted_rows.append(
                {
                    **row,
                    "appliances": appliances,
                    "total_consumption": round(sum(float(value) for value in appliances.values()), 3),
                }
            )
        return adjusted_rows

    @classmethod
    def get_recent_data(cls, limit: int = 24) -> list[dict[str, Any]]:
        data = cls._get_hourly_data()
        return data[-limit:]

    @classmethod
    def get_prediction_records(cls, hours: int = 240) -> list[dict[str, Any]]:
        data = cls._get_hourly_data()
        return data[-max(1, int(hours)):]

    @staticmethod
    def _average_usage_per_hour(total_energy: float, rows: list[dict[str, Any]]) -> float:
        return DatasetCacheService.average_usage_per_hour(total_energy, rows)

    @classmethod
    def get_summary(cls) -> dict[str, Any]:
        data = cls._get_data()
        if not data:
            return {
                "current_usage": 0.0,
                "daily_consumption": 0.0,
                "peak_hour": "N/A",
                "average_temperature": 0.0,
                "top_devices": [],
                "selected_dataset": cls._selected_dataset,
            }

        cutoff = data[-1]["timestamp"] - timedelta(hours=24)
        last_24h = [row for row in data if row["timestamp"] >= cutoff]
        total_24h = sum(row["total_consumption"] for row in last_24h)
        current_usage = data[-1]["total_consumption"]
        average_temp = sum(row["temperature"] for row in last_24h) / len(last_24h) if last_24h else 0.0

        hourly_totals: dict[int, float] = {}
        for row in last_24h:
            hourly_totals[row["hour"]] = hourly_totals.get(row["hour"], 0.0) + row["total_consumption"]

        peak_hour = "N/A"
        if hourly_totals:
            peak_hour_index = max(hourly_totals, key=hourly_totals.get)
            peak_hour = f"{peak_hour_index:02d}:00 - {peak_hour_index + 1:02d}:00"

        appliance_totals: Counter[str] = Counter()
        for row in last_24h:
            for appliance, value in row["appliances"].items():
                appliance_totals[appliance] += float(value)

        top_devices = [
            {
                "name": cls._display_name(name),
                "average_usage": cls._average_usage_per_hour(appliance_totals[name], last_24h),
            }
            for name, _ in appliance_totals.most_common(5)
        ]

        return {
            "current_usage": round(current_usage, 3),
            "daily_consumption": round(total_24h, 3),
            "peak_hour": peak_hour,
            "average_temperature": round(average_temp, 1),
            "top_devices": top_devices,
            "selected_dataset": cls._selected_dataset,
        }

    @classmethod
    def get_device_breakdown(cls) -> list[dict[str, Any]]:
        data = cls._get_data()
        relevant_rows = DatasetCacheService.rows_for_minutes_window(data, 1440) if data else []
        appliance_totals: Counter[str] = Counter()
        for row in relevant_rows:
            for appliance, value in row["appliances"].items():
                appliance_totals[appliance] += float(value)

        metadata = DatasetCacheService.dataset_details(cls._dataset_path())
        all_devices = set(metadata.get("device_columns", []))
        for row in relevant_rows:
            all_devices.update(row["appliances"].keys())

        total = sum(appliance_totals.values()) or 1
        return [
            {
                "name": cls._display_name(name),
                "device_id": name,
                "average_usage": cls._average_usage_per_hour(appliance_totals.get(name, 0.0), relevant_rows),
                "share": round((appliance_totals.get(name, 0.0) / total) * 100, 1),
            }
            for name in sorted(all_devices, key=lambda x: appliance_totals.get(x, 0.0), reverse=True)
        ]

    @classmethod
    def get_historical_data(cls, days: int = 7) -> list[dict[str, Any]]:
        cls._load_settings()
        if cls._use_selected_dataset():
            metadata = cls._active_dataset_metadata() or {}
            daily_history = metadata.get("daily_history", [])
            if daily_history:
                latest_date = datetime.fromisoformat(daily_history[-1]["date"]).date()
                cutoff = latest_date - timedelta(days=max(1, int(days)) - 1)
                return [
                    {
                        "date": row["date"],
                        "total_consumption": round(cls._safe_float(row.get("total_consumption"), 0.0), 3),
                        "average_temperature": round(cls._safe_float(row.get("average_temperature"), 24.0), 1),
                    }
                    for row in daily_history
                    if datetime.fromisoformat(row["date"]).date() >= cutoff
                ]

        data = cls._get_data()
        if not data:
            return []

        cutoff = data[-1]["timestamp"] - timedelta(days=days)
        aggregated: dict[str, dict[str, Any]] = {}
        for row in data:
            if row["timestamp"] < cutoff:
                continue
            date_key = row["timestamp"].date().isoformat()
            if date_key not in aggregated:
                aggregated[date_key] = {
                    "date": date_key,
                    "total_consumption": 0.0,
                    "average_temperature": 0.0,
                    "count": 0,
                }
            aggregated[date_key]["total_consumption"] += row["total_consumption"]
            aggregated[date_key]["average_temperature"] += row["temperature"]
            aggregated[date_key]["count"] += 1

        return [
            {
                "date": value["date"],
                "total_consumption": round(value["total_consumption"], 3),
                "average_temperature": round(value["average_temperature"] / value["count"], 1),
            }
            for value in sorted(aggregated.values(), key=lambda x: x["date"])
        ]

    @classmethod
    def get_catalog(cls) -> dict[str, Any]:
        cls._load_settings()
        details = cls._get_dataset_details()
        device_cols = details.get("device_columns", [])
        
        catalog = []
        for col in device_cols:
            catalog.append({
                "id": col,
                "name": cls._display_name(col),
                "category": cls._get_category(col),
                "type": col.split("_")[0].lower() if "_" in col else "other"
            })
            
        return {
            "dataset_name": cls._selected_dataset,
            "device_count": len(catalog),
            "devices": catalog
        }

    @classmethod
    def get_anomaly_detection(cls) -> list[dict[str, Any]]:
        data = cls._get_hourly_data()
        if len(data) < 24:
            return []

        recent = data[-24:]
        avg = sum(row["total_consumption"] for row in recent) / len(recent)
        std = (sum((row["total_consumption"] - avg) ** 2 for row in recent) / len(recent)) ** 0.5

        anomalies = []
        for row in recent:
            if abs(row["total_consumption"] - avg) > 2 * std:
                anomalies.append(
                    {
                        "timestamp": row["timestamp"].isoformat(),
                        "consumption": row["total_consumption"],
                        "deviation": round(abs(row["total_consumption"] - avg), 3),
                        "type": "high" if row["total_consumption"] > avg else "low",
                    }
                )
        return anomalies

    @classmethod
    def get_energy_efficiency_score(cls) -> dict[str, Any]:
        summary = cls.get_summary()
        score = 100
        if summary["daily_consumption"] > 30:
            score -= 20
        if summary["average_temperature"] > 25:
            score -= 10

        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        else:
            grade = "D"

        return {
            "score": max(0, score),
            "grade": grade,
            "recommendations": [
                "Reduce AC usage during peak hours",
                "Use energy-efficient appliances",
                "Implement smart scheduling",
            ],
            "selected_dataset": cls._selected_dataset,
        }

    @staticmethod
    def _get_category(name: str) -> str:
        name = name.lower()
        if any(x in name for x in ["fridge", "microwave", "oven", "stove", "kitchen", "coffee", "toaster", "dish"]):
            return "Kitchen"
        if any(x in name for x in ["ac", "heater", "hvac", "geyser", "fan", "temp", "conditioning"]):
            return "Climate"
        if any(x in name for x in ["tv", "gaming", "speaker", "theater", "console", "audio"]):
            return "Entertainment"
        if any(x in name for x in ["laptop", "computer", "printer", "router", "office", "monitor"]):
            return "Home Office"
        if any(x in name for x in ["light", "bulb", "lamp", "led"]):
            return "Lighting"
        if any(x in name for x in ["washing", "dryer", "iron", "laundry", "cleaner"]):
            return "Cleaning"
        return "Essentials"

    @classmethod
    def get_device_time_series(cls, minutes: int = 1440) -> list[dict[str, Any]]:
        data = cls._get_data()
        if not data:
            return []

        minutes = max(5, minutes)
        relevant_rows = DatasetCacheService.rows_for_minutes_window(data, minutes)
        bucket_minutes = cls._bucket_minutes_for_window(minutes)
        
        # Determine the full set of devices from the dataset metadata
        metadata = DatasetCacheService.dataset_details(cls._dataset_path())
        all_devices = set(metadata.get("device_columns", []))
        
        # Also include any devices actually found in the rows (as a safety fallback)
        for row in relevant_rows:
            all_devices.update(row["appliances"].keys())
            
        device_points: dict[str, list[dict[str, Any]]] = {name: [] for name in all_devices}
        
        for row in DatasetCacheService.aggregate_rows(relevant_rows, bucket_minutes):
            label = row["timestamp"].strftime("%d %b %I:%M %p") if bucket_minutes >= 60 else row["timestamp"].strftime("%I:%M %p")
            ts_iso = row["timestamp"].isoformat()
            
            # Add point for every known device
            for device_name in all_devices:
                value = row["appliances"].get(device_name, 0.0)
                device_points[device_name].append({
                    "timestamp": ts_iso,
                    "label": label,
                    "energy_kwh": round(float(value), 3),
                })

        total_energy = sum(sum(p["energy_kwh"] for p in pts) for pts in device_points.values()) or 1.0
        return [
            {
                "device_name": cls._display_name(name),
                "device_id": name,
                "category": cls._get_category(name),
                "points": pts,
                "total_energy_kwh": round(sum(p["energy_kwh"] for p in pts), 3),
                "share": round((sum(p["energy_kwh"] for p in pts) / total_energy) * 100, 1),
            }
            for name, pts in sorted(
                device_points.items(), 
                key=lambda item: sum(p["energy_kwh"] for p in item[1]), 
                reverse=True
            )
        ]

    @classmethod
    def _bucket_minutes_for_window(cls, minutes: int) -> int:
        if minutes <= 60:
            return 1
        if minutes <= 180:
            return 2
        if minutes <= 1440:
            return 5
        return 30

    @classmethod
    def get_pattern_insights(cls) -> dict[str, Any]:
        cls._load_settings()
        now = datetime.now()
        if cls._use_selected_dataset():
            metadata = cls._active_dataset_metadata() or {}
            pattern = dict(metadata.get("pattern_summary", {}))
            if pattern:
                notes = list(pattern.get("notes", []))
                cadence_minutes = metadata.get("cadence_minutes")
                if cadence_minutes:
                    notes.append(
                        f"The active dashboard dataset uses a {int(cadence_minutes)}-minute gap and is shared across all pages, graphs, and model flows."
                    )
                pattern["notes"] = notes
                pattern["current_day_period"] = cls._day_period_for_hour(now.hour)
                pattern["current_timestamp"] = now.isoformat()
                pattern["selected_dataset"] = cls._selected_dataset
                return pattern

        data = cls._get_data()
        if not data:
            return {
                "record_count": 0,
                "quality_score": 0,
                "invalid_records": 0,
                "temperature_range": "No data",
                "dominant_season": "Unknown",
                "dominant_day_period": "Unknown",
                "month_distribution": {},
                "season_distribution": {},
                "day_period_distribution": {},
                "notes": ["No normalized readings were available for validation."],
                "selected_dataset": cls._selected_dataset,
            }

        invalid_records = 0
        month_distribution: Counter[str] = Counter()
        season_distribution: Counter[str] = Counter()
        day_period_distribution: Counter[str] = Counter()
        temperatures: list[float] = []

        for row in data:
            timestamp = row.get("timestamp")
            if not timestamp or row.get("total_consumption", 0) < 0:
                invalid_records += 1
                continue

            month_name = timestamp.strftime("%b")
            season = cls._season_for_month(timestamp.month)
            day_period = cls._day_period_for_hour(timestamp.hour)

            month_distribution[month_name] += 1
            season_distribution[season] += 1
            day_period_distribution[day_period] += 1

            temperature = row.get("temperature")
            if temperature is not None:
                temperatures.append(float(temperature))
                if temperature < -10 or temperature > 60:
                    invalid_records += 1

        score_penalty = min(60, invalid_records * 5)
        quality_score = max(40, 100 - score_penalty)
        notes = []
        if invalid_records == 0:
            notes.append("No invalid timestamps or negative energy values were found in the normalized dataset.")
        else:
            notes.append(f"{invalid_records} records look suspicious and should be reviewed.")

        if len(month_distribution) < 2:
            notes.append("Month coverage is narrow, so season-level conclusions are limited.")
        else:
            notes.append("Month and season coverage is wide enough for a presentation-level pattern summary.")

        dominant_season = season_distribution.most_common(1)[0][0] if season_distribution else "Unknown"
        dominant_day_period = day_period_distribution.most_common(1)[0][0] if day_period_distribution else "Unknown"
        current_day_period = cls._day_period_for_hour(now.hour)
        temperature_range = (
            f"{min(temperatures):.1f} C to {max(temperatures):.1f} C"
            if temperatures
            else "No temperature data"
        )

        return {
            "record_count": len(data),
            "quality_score": quality_score,
            "invalid_records": invalid_records,
            "temperature_range": temperature_range,
            "dominant_season": dominant_season,
            "dominant_day_period": dominant_day_period,
            "current_day_period": current_day_period,
            "current_timestamp": now.isoformat(),
            "month_distribution": dict(month_distribution),
            "season_distribution": dict(season_distribution),
            "day_period_distribution": dict(day_period_distribution),
            "notes": notes,
            "selected_dataset": cls._selected_dataset,
        }
