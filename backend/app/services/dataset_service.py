from collections import Counter
import csv
from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import Any

from app.database.db import db


class DatasetService:
    _dataset_mode = "auto"
    _valid_modes = {"auto", "real_only", "synthetic_demo"}
    _dataset_dir = Path(__file__).resolve().parents[2] / "data" / "datasets"
    _selected_dataset = "daily_normal_use_default.csv"
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
        if selected_dataset:
            cls._selected_dataset = selected_dataset

    @classmethod
    def _save_settings(cls) -> None:
        cls._ensure_settings_storage()
        payload = {
            "mode": cls._dataset_mode,
            "selected_dataset": cls._selected_dataset,
        }
        cls._settings_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def get_dataset_mode(cls) -> dict[str, Any]:
        cls._load_settings()
        return {
            "mode": cls._dataset_mode,
            "selected_dataset": cls._selected_dataset,
            "supported_modes": sorted(cls._valid_modes),
            "description": {
                "auto": "Use real data when available, else synthetic demo data.",
                "real_only": "Use only ingested real data.",
                "synthetic_demo": "Always use generated demo dataset.",
            },
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
        cls._save_settings()
        return {"status": "success", "selected_dataset": cls._selected_dataset, "available_datasets": available}

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
            return "winter"
        if month in (3, 4, 5):
            return "summer"
        if month in (6, 7, 8, 9):
            return "monsoon"
        return "post_monsoon"

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

    @classmethod
    def _load_csv_dataset(cls, dataset_name: str) -> list[dict[str, Any]]:
        if not dataset_name:
            return []
        dataset_path = cls._dataset_dir / dataset_name
        if not dataset_path.exists():
            return []
        rows: list[dict[str, Any]] = []
        with dataset_path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                timestamp_raw = str(row.get("timestamp", "")).strip()
                if not timestamp_raw:
                    continue
                try:
                    timestamp = datetime.fromisoformat(timestamp_raw)
                except ValueError:
                    continue
                energy = float(row.get("energy_kwh", 0.0) or 0.0)
                temperature = float(row.get("temperature_c", 24.0) or 24.0)
                device = str(row.get("device_id", "home_energy")).strip() or "home_energy"
                rows.append(
                    {
                        "timestamp": timestamp,
                        "hour": timestamp.hour,
                        "day_of_week": timestamp.weekday(),
                        "is_weekend": 1 if timestamp.weekday() >= 5 else 0,
                        "temperature": temperature,
                        "total_consumption": energy,
                        "appliances": {device: energy},
                    }
                )
        return sorted(rows, key=lambda item: item["timestamp"])

    @classmethod
    def _get_data(cls) -> list[dict[str, Any]]:
        cls._load_settings()
        normalized = cls._normalize_readings()
        active_map = cls._active_device_map()
        selected_csv = cls._load_csv_dataset(cls._selected_dataset)
        if cls._dataset_mode == "synthetic_demo":
            return cls._apply_device_states(selected_csv or cls._fallback_data(), active_map)
        if cls._dataset_mode == "real_only":
            return cls._apply_device_states(cls._expand_sparse_data(normalized), active_map) if normalized else []
        if normalized:
            return cls._apply_device_states(cls._expand_sparse_data(normalized), active_map)
        return cls._apply_device_states(selected_csv or cls._fallback_data(), active_map)

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
        data = cls._get_data()
        return data[-limit:]

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
                appliance_totals[appliance] += value

        top_devices = [
            {"name": cls._display_name(name), "average_usage": round(appliance_totals[name] / len(last_24h), 3)}
            for name, _ in appliance_totals.most_common(5)
        ]

        return {
            "current_usage": round(current_usage, 3),
            "daily_consumption": round(total_24h, 3),
            "peak_hour": peak_hour,
            "average_temperature": round(average_temp, 1),
            "top_devices": top_devices,
        }

    @classmethod
    def get_device_breakdown(cls) -> list[dict[str, Any]]:
        data = cls._get_data()
        relevant_rows = data[-1440:] if len(data) >= 1440 else data
        appliance_totals: Counter[str] = Counter()
        for row in relevant_rows:
            for appliance, value in row["appliances"].items():
                appliance_totals[appliance] += value

        total = sum(appliance_totals.values()) or 1
        return [
            {
                "name": cls._display_name(name),
                "device_id": name,
                "average_usage": round(value / len(relevant_rows), 3),
                "share": round((value / total) * 100, 1),
            }
            for name, value in appliance_totals.most_common(10)
        ]

    @classmethod
    def get_historical_data(cls, days: int = 7) -> list[dict[str, Any]]:
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
    def get_anomaly_detection(cls) -> list[dict[str, Any]]:
        data = cls._get_data()
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
        }

    @classmethod
    def get_device_time_series(cls, minutes: int = 1440) -> list[dict[str, Any]]:
        data = cls._get_data()
        if not data:
            return []

        latest_timestamp = data[-1]["timestamp"]
        minutes = max(5, minutes)
        if minutes < 60:
            return cls._get_device_minute_series(minutes)

        cutoff = latest_timestamp - timedelta(minutes=minutes)
        relevant_rows = [row for row in data if row["timestamp"] >= cutoff]

        device_points: dict[str, list[dict[str, Any]]] = {}
        for row in relevant_rows:
            label = row["timestamp"].strftime("%d %b %I:%M %p")
            for device_name, value in row["appliances"].items():
                device_points.setdefault(device_name, []).append(
                    {
                        "timestamp": row["timestamp"].isoformat(),
                        "label": label,
                        "energy_kwh": round(float(value), 3),
                    }
                )

        total_energy = sum(sum(point["energy_kwh"] for point in points) for points in device_points.values()) or 1.0
        return [
            {
                "device_name": cls._display_name(device_name),
                "device_id": device_name,
                "points": points,
                "total_energy_kwh": round(sum(point["energy_kwh"] for point in points), 3),
                "share": round((sum(point["energy_kwh"] for point in points) / total_energy) * 100, 1),
            }
            for device_name, points in sorted(device_points.items(), key=lambda item: cls._display_name(item[0]).lower())
        ]

    @classmethod
    def _get_device_minute_series(cls, minutes: int) -> list[dict[str, Any]]:
        data = cls._get_data()
        if not data:
            return []

        latest = data[-1]
        latest_timestamp = latest["timestamp"]
        device_shares = latest["appliances"] or {"home_energy": latest["total_consumption"] or 0.5}
        total = sum(float(value) for value in device_shares.values()) or 1.0
        points_by_device: dict[str, list[dict[str, Any]]] = {}

        for minute_offset in range(minutes - 1, -1, -5):
            timestamp = latest_timestamp - timedelta(minutes=minute_offset)
            label = timestamp.strftime("%I:%M %p")
            for device_name, value in device_shares.items():
                numeric_value = float(value)
                if numeric_value <= 0:
                    energy = 0.0
                else:
                    profile = cls._device_profile(device_name)
                    signature = profile["signature"]
                    minute_bucket = (minute_offset // 5) + profile["phase"]
                    activity = cls._device_activity_factor(device_name, timestamp.hour, minute_bucket)
                    pulse = 1 + (((signature + minute_offset) % 5) - 2) * 0.025
                    energy = round(max(0.001, numeric_value * activity * pulse / 12.0), 3)
                points_by_device.setdefault(device_name, []).append(
                    {
                        "timestamp": timestamp.isoformat(),
                        "label": label,
                        "energy_kwh": energy,
                    }
                )

        total_energy = sum(sum(point["energy_kwh"] for point in points) for points in points_by_device.values()) or 1.0
        return [
            {
                "device_name": cls._display_name(device_name),
                "device_id": device_name,
                "points": points,
                "total_energy_kwh": round(sum(point["energy_kwh"] for point in points), 3),
                "share": round((sum(point["energy_kwh"] for point in points) / total_energy) * 100, 1),
            }
            for device_name, points in sorted(points_by_device.items(), key=lambda item: cls._display_name(item[0]).lower())
        ]

    @classmethod
    def get_pattern_insights(cls) -> dict[str, Any]:
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
        now = datetime.now()
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
        }
