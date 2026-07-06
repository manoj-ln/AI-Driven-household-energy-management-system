from __future__ import annotations

import csv
import math
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
REF_FILE = BASE_DIR / "data" / "processed" / "energy_features.csv"
SOURCE_FILE = BASE_DIR / "data" / "datasets" / "energy_last_24_hours.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "energy_last_24_hours_features.csv"


APPLIANCE_COLUMNS = [
    "Lighting_LED",
    "Lighting_Tube",
    "Cooling_Fan_Ceiling",
    "Cooling_Fan_Table",
    "Cooling_AC",
    "Cooling_Cooler",
    "Electronics_TV",
    "Electronics_Laptop",
    "Electronics_Desktop",
    "Electronics_Charger",
    "Electronics_WiFi",
    "Kitchen_Microwave",
    "Kitchen_Induction",
    "Kitchen_Kettle",
    "Kitchen_Mixer",
    "Kitchen_Toaster",
    "Kitchen_Coffee",
    "Utility_Washing",
    "Utility_Dishwasher",
    "Utility_Vacuum",
    "Utility_Iron",
    "Heating_Water",
    "Heating_Room",
    "Smart_Speaker",
    "Smart_CCTV",
    "Smart_Purifier",
    "Smart_Humidifier",
    "Others_Refrigerator",
    "Others_Purifier",
    "Others_Exhaust",
]


def _safe_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def main() -> None:
    with REF_FILE.open("r", encoding="utf-8") as rf:
        ref_reader = csv.reader(rf)
        header = next(ref_reader)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with SOURCE_FILE.open("r", encoding="utf-8") as sf, OUTPUT_FILE.open("w", encoding="utf-8", newline="") as of:
        source_reader = csv.DictReader(sf)
        writer = csv.DictWriter(of, fieldnames=header)
        writer.writeheader()

        lag_1 = lag_2 = lag_3 = lag_6 = lag_12 = lag_24 = 0.0
        recent_values: list[float] = []

        for row in source_reader:
            ts = str(row.get("Timestamp", "")).strip()
            if not ts:
                continue
            total = _safe_float(row.get("Total_Consumption"), 0.0)
            temp = _safe_float(row.get("Temperature"), 24.0)
            hour = int(_safe_float(row.get("Hour"), ts[11:13]))
            day_of_week = int(_safe_float(row.get("DayOfWeek"), 0))
            is_weekend = int(_safe_float(row.get("IsWeekend"), 1 if day_of_week >= 5 else 0))
            is_peak_hour = 1 if 18 <= hour <= 22 else 0

            appliance_values = {
                col: round(_safe_float(row.get(col), 0.0), 4)
                for col in APPLIANCE_COLUMNS
            }

            recent_values.append(total)
            if len(recent_values) > 48:
                recent_values.pop(0)

            def rolling(window: int) -> tuple[float, float]:
                values = recent_values[-window:] if len(recent_values) >= window else recent_values
                if not values:
                    return 0.0, 0.0
                mean = sum(values) / len(values)
                variance = sum((v - mean) ** 2 for v in values) / len(values)
                return mean, variance ** 0.5

            m3, s3 = rolling(3)
            m6, s6 = rolling(6)
            m12, s12 = rolling(12)
            m24, s24 = rolling(24)
            m48, s48 = rolling(48)

            hour_sin = math.sin(2 * math.pi * hour / 24)
            hour_cos = math.cos(2 * math.pi * hour / 24)
            day_sin = math.sin(2 * math.pi * day_of_week / 7)
            day_cos = math.cos(2 * math.pi * day_of_week / 7)

            output = {key: "" for key in header}
            output["timestamp"] = ts.replace("T", " ")
            output["Timestamp"] = ts
            output["Hour"] = hour
            output["DayOfWeek"] = day_of_week
            output["IsWeekend"] = is_weekend
            output["Temperature"] = round(temp, 2)
            for col, value in appliance_values.items():
                output[col] = round(value, 4)
            output["Total_Consumption"] = round(total, 4)
            output["hour"] = hour
            output["day_of_week"] = day_of_week
            output["month"] = int(ts[5:7])
            output["is_weekend"] = is_weekend
            output["is_peak_hour"] = is_peak_hour
            output["total_consumption_lag_1"] = round(lag_1, 4)
            output["total_consumption_lag_2"] = round(lag_2, 4)
            output["total_consumption_lag_3"] = round(lag_3, 4)
            output["total_consumption_lag_6"] = round(lag_6, 4)
            output["total_consumption_lag_12"] = round(lag_12, 4)
            output["total_consumption_lag_24"] = round(lag_24, 4)
            output["total_consumption_rolling_mean_3"] = round(m3, 6)
            output["total_consumption_rolling_std_3"] = round(s3, 6)
            output["total_consumption_rolling_mean_6"] = round(m6, 6)
            output["total_consumption_rolling_std_6"] = round(s6, 6)
            output["total_consumption_rolling_mean_12"] = round(m12, 6)
            output["total_consumption_rolling_std_12"] = round(s12, 6)
            output["total_consumption_rolling_mean_24"] = round(m24, 6)
            output["total_consumption_rolling_std_24"] = round(s24, 6)
            output["total_consumption_rolling_mean_48"] = round(m48, 6)
            output["total_consumption_rolling_std_48"] = round(s48, 6)
            output["hour_sin"] = round(hour_sin, 8)
            output["hour_cos"] = round(hour_cos, 8)
            output["day_sin"] = round(day_sin, 8)
            output["day_cos"] = round(day_cos, 8)
            output["appliance_sum"] = round(sum(float(appliance_values[c]) for c in APPLIANCE_COLUMNS), 6)
            output["appliance_count_active"] = sum(1 for c in APPLIANCE_COLUMNS if float(appliance_values[c]) > 0)

            writer.writerow(output)

            lag_24 = lag_12
            lag_12 = lag_6
            lag_6 = lag_3
            lag_3 = lag_2
            lag_2 = lag_1
            lag_1 = total

    print(f"Created reference-style dataset: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
