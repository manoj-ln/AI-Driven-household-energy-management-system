from __future__ import annotations

import csv
import math
from datetime import datetime, timedelta
from pathlib import Path


DATASET_DIR = Path(__file__).resolve().parents[1] / "data" / "datasets"
START = datetime(2025, 1, 1, 0, 0, 0)
MINUTES = 365 * 24 * 60  # 1 year minute-wise


def _season_multiplier(month: int, summer: float, winter: float) -> float:
    if month in (3, 4, 5):
        return summer
    if month in (12, 1, 2):
        return winter
    return 1.0


def _daily_wave(minute_of_day: int, phase: float = 0.0, amplitude: float = 0.2) -> float:
    angle = ((minute_of_day / 1440.0) * 2.0 * math.pi) + phase
    return 1.0 + amplitude * math.sin(angle)


def _write_dataset(path: Path, base_load: float, profile: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["timestamp", "device_id", "energy_kwh", "temperature_c"])

        for i in range(MINUTES):
            ts = START + timedelta(minutes=i)
            minute_of_day = ts.hour * 60 + ts.minute
            weekday = ts.weekday()
            weekend = weekday >= 5

            if profile == "daily_normal_use_default":
                device = "home_energy"
                temp = 24 + 7 * math.sin((minute_of_day / 1440.0) * 2.0 * math.pi)
                load = base_load * _daily_wave(minute_of_day, amplitude=0.22)
                load *= 1.06 if weekend else 1.0
            elif profile == "urban_family_weekday":
                device = "home_energy"
                temp = 25 + 8 * math.sin((minute_of_day / 1440.0) * 2.0 * math.pi)
                load = base_load * _daily_wave(minute_of_day, phase=0.2, amplitude=0.28)
                load *= 0.95 if weekend else 1.12
            elif profile == "weekend_peak_entertainment":
                device = "home_energy"
                temp = 24 + 6 * math.sin((minute_of_day / 1440.0) * 2.0 * math.pi)
                load = base_load * _daily_wave(minute_of_day, phase=0.9, amplitude=0.35)
                evening_boost = 1.25 if 18 <= ts.hour <= 23 else 1.0
                load *= evening_boost * (1.22 if weekend else 0.92)
            elif profile == "solar_assisted_home":
                device = "home_energy"
                temp = 26 + 7 * math.sin((minute_of_day / 1440.0) * 2.0 * math.pi)
                load = base_load * _daily_wave(minute_of_day, phase=0.4, amplitude=0.2)
                solar_offset = 0.72 if 9 <= ts.hour <= 16 else 1.0
                load *= solar_offset
            elif profile == "winter_heating_profile":
                device = "home_energy"
                temp = 14 + 5 * math.sin((minute_of_day / 1440.0) * 2.0 * math.pi)
                load = base_load * _daily_wave(minute_of_day, phase=0.5, amplitude=0.26)
                load *= _season_multiplier(ts.month, summer=0.72, winter=1.45)
            elif profile == "student_hostel_shared_load":
                device = "home_energy"
                temp = 25 + 6 * math.sin((minute_of_day / 1440.0) * 2.0 * math.pi)
                load = base_load * _daily_wave(minute_of_day, phase=1.2, amplitude=0.3)
                study_peak = 1.18 if 19 <= ts.hour <= 1 or ts.hour == 0 else 1.0
                load *= study_peak
            else:
                device = "home_energy"
                temp = 24.0
                load = base_load

            writer.writerow([ts.isoformat(), device, round(max(load, 0.001), 4), round(temp, 2)])


def main() -> None:
    datasets = [
        ("daily_normal_use_default.csv", 0.18, "daily_normal_use_default"),
        ("urban_family_weekday.csv", 0.21, "urban_family_weekday"),
        ("weekend_peak_entertainment.csv", 0.24, "weekend_peak_entertainment"),
        ("solar_assisted_home.csv", 0.17, "solar_assisted_home"),
        ("winter_heating_profile.csv", 0.23, "winter_heating_profile"),
        ("student_hostel_shared_load.csv", 0.2, "student_hostel_shared_load"),
    ]
    for filename, base_load, profile in datasets:
        _write_dataset(DATASET_DIR / filename, base_load=base_load, profile=profile)
    print(f"Generated {len(datasets)} datasets in {DATASET_DIR}")


if __name__ == "__main__":
    main()
