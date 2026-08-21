"""Normalize datasets to the complete calendar duration of their configured year."""
from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATASETS_DIR = BASE_DIR / "data" / "datasets"

REQUIRED_COLUMNS = [
    "timestamp", "Year", "Month", "Week", "Day", "DayOfWeek", "Hour", "Minute",
    "Season", "Weather", "Temperature", "Humidity", "OccupancyLevel",
    "ElectricityTariff", "RenewableEnergyStatus", "PowerOutageStatus",
    "DeviceStatus", "DevicePowerConsumption", "TotalHouseholdConsumption",
    "EstimatedCost", "CarbonEmissions", "AnomalyLabel",
    "SolarGeneration", "BatterySOC", "GridImport", "GridExport",
    "Ceiling_Fan_Living", "Ceiling_Fan_Bed1", "Ceiling_Fan_Bed2", "Ceiling_Fan_Kitchen",
    "Table_Fan_Study", "Exhaust_Fan_Kitchen", "Exhaust_Fan_Bath",
    "Air_Conditioner_Bed1", "Air_Conditioner_Living", "Air_Conditioner_Study",
    "Refrigerator_Main", "Refrigerator_Secondary", "Water_Purifier_Kitchen",
    "Microwave_Oven", "Induction_Stove_1", "Induction_Stove_2", "Rice_Cooker",
    "Electric_Kettle", "Coffee_Machine", "Mixer_Grinder", "Toaster",
    "Electric_Chimney", "Air_Fryer", "Dishwasher", "Bottle_Warmer",
    "Washing_Machine", "Iron_Box", "Vacuum_Cleaner", "Robot_Vacuum",
    "Geyser_Bathroom1", "Geyser_Bathroom2", "Water_Heater_Kitchen",
    "Room_Heater_Bed1", "Room_Heater_Bed2", "Water_Pump_Overhead",
    "Aquarium_Pump", "Aquarium_Heater", "Television_Living", "Television_Second",
    "Home_Theater_Speaker", "Soundbar_Living", "Projector", "Gaming_Console",
    "Desktop_PC", "Laptop_1", "Laptop_2", "Monitor_1", "Monitor_2", "Printer",
    "WiFi_Router", "LED_Lights_Living", "LED_Lights_Kitchen", "LED_Lights_Bed1",
    "LED_Lights_Bed2", "LED_Lights_Study", "LED_Lights_Bathroom",
    "LED_Lights_Corridor", "LED_Lights_Outdoor", "Garden_Lights",
    "Security_Lights", "Security_Lights_Backyard", "Festival_String_Lights",
    "Phone_Charger_1", "Phone_Charger_2", "Phone_Charger_3", "Tablet_Charger_1",
    "Tablet_Charger_2", "Smartwatch_Charger_1", "Smartwatch_Charger_2",
    "Laptop_Charger_1", "Laptop_Charger_2", "EV_Charger_Wall", "UPS_Backup",
    "Smart_Speaker_Living", "Smart_Speaker_Bed", "Smart_Hub", "Smart_Display_Kitchen",
    "Smart_Plug_1", "Smart_Plug_2", "Smart_Doorbell", "Smart_Lock",
    "CCTV_Camera_1", "CCTV_Camera_2", "Smart_Curtains_Living", "Smart_Curtains_Bed",
    "Pedestal_Fan_Stand", "Air_Purifier", "Humidifier", "CPAP_Machine", "Treadmill",
    "Hair_Dryer", "Electric_Shaver", "Electric_Toothbrush", "Vacuum_Charger_Base",
    "Garage_Door_Motor",
]

REQUIRED_DEVICES = [c for c in REQUIRED_COLUMNS if c not in {
    "timestamp", "Year", "Month", "Week", "Day", "DayOfWeek", "Hour", "Minute",
    "Season", "Weather", "Temperature", "Humidity", "OccupancyLevel",
    "ElectricityTariff", "RenewableEnergyStatus", "PowerOutageStatus",
    "DeviceStatus", "DevicePowerConsumption", "TotalHouseholdConsumption",
    "EstimatedCost", "CarbonEmissions", "AnomalyLabel",
    "SolarGeneration", "BatterySOC", "GridImport", "GridExport",
}]

TARGET_COLS = REQUIRED_COLUMNS
CO2_FACTOR = 0.82


def season_for_month(month: int) -> str:
    if month in (12, 1, 2):
        return "Winter"
    if month in (3, 4, 5):
        return "Summer"
    if month in (6, 7, 8):
        return "Monsoon"
    return "Autumn"


def _generate_vectorized(seed: int, years: list[int], uses_renewables: bool = False) -> pd.DataFrame:
    rng = np.random.RandomState(seed)
    start = datetime(years[0], 1, 1, 0, 0, 0)
    end = datetime(years[-1], 12, 31, 23, 59, 0)
    n = int((end - start).total_seconds() // 60) + 1
    timestamps = np.array([start + timedelta(minutes=i) for i in range(n)], dtype="datetime64[m]")

    years_arr = timestamps.astype("datetime64[Y]").astype(int) + 1970
    months_arr = timestamps.astype("datetime64[M]").astype(int) % 12 + 1
    days_arr = (timestamps - timestamps.astype("datetime64[M]")).astype(int) // 86400000000000 + 1

    hours_arr = (timestamps.astype("datetime64[h]") - timestamps.astype("datetime64[D]")).astype(int)
    minutes_arr = (timestamps.astype("datetime64[m]") - timestamps.astype("datetime64[h]")).astype(int)

    week_arr = np.array([datetime(y, m, d).isocalendar().week for y, m, d in zip(years_arr, months_arr, days_arr)])
    dayofweek_arr = np.array([datetime(y, m, d).weekday() for y, m, d in zip(years_arr, months_arr, days_arr)])

    seasons_arr = np.array([season_for_month(m) for m in months_arr])

    day_of_year = np.array([t.timetuple().tm_yday for t in timestamps.astype(datetime)])
    base_temp = np.where(months_arr <= 2, 18.0, np.where(months_arr <= 5, 35.0, np.where(months_arr <= 8, 27.0, 27.0)))
    seasonal_var = 5.0 * np.sin(2 * np.pi * (day_of_year - 80) / 365.0)
    temp_arr = base_temp + seasonal_var + rng.uniform(-2.0, 2.0, size=n)
    temp_arr = np.round(temp_arr, 1)

    weather_arr = np.where(temp_arr > 30, rng.choice(["Sunny", "Hot", "Dry Weather", "Heatwave"], size=n),
                   np.where(temp_arr < 20, rng.choice(["Cool", "Cold Wave", "Cloudy"], size=n),
                            rng.choice(["Sunny", "Cloudy", "Dry Weather", "High Humidity"], size=n)))
    humidity_arr = np.where(temp_arr > 30, rng.randint(30, 60, size=n),
                      np.where(temp_arr < 20, rng.randint(50, 80, size=n),
                               rng.randint(40, 70, size=n)))

    occupancy_arr = np.zeros(n, dtype=int)
    is_weekend = dayofweek_arr >= 5
    for h in range(24):
        mask = (hours_arr == h) & is_weekend
        if 0 <= h < 8:
            occupancy_arr[mask] = rng.choice([0, 1], size=mask.sum(), p=[0.8, 0.2])
        elif h < 22:
            occupancy_arr[mask] = rng.choice([2, 3, 4], size=mask.sum(), p=[0.3, 0.4, 0.3])
        else:
            occupancy_arr[mask] = rng.choice([0, 1, 2], size=mask.sum(), p=[0.5, 0.3, 0.2])

        mask = (hours_arr == h) & ~is_weekend
        if 0 <= h < 6:
            occupancy_arr[mask] = rng.choice([0, 1], size=mask.sum(), p=[0.9, 0.1])
        elif h < 9:
            occupancy_arr[mask] = rng.choice([1, 2, 3], size=mask.sum(), p=[0.3, 0.4, 0.3])
        elif h < 17:
            occupancy_arr[mask] = rng.choice([1, 2], size=mask.sum(), p=[0.6, 0.4])
        elif h < 22:
            occupancy_arr[mask] = rng.choice([2, 3, 4], size=mask.sum(), p=[0.2, 0.4, 0.4])
        else:
            occupancy_arr[mask] = rng.choice([0, 1, 2], size=mask.sum(), p=[0.5, 0.3, 0.2])

    tariff_arr = np.full(n, 6.26)
    tariff_arr[(hours_arr >= 18) & (hours_arr <= 22)] = round(6.26 * 1.2, 2)
    tariff_arr[hours_arr < 5] = round(6.26 * 0.85, 2)

    outage_arr = np.full(n, "None")
    outage_mask = rng.random(n) < 0.0001
    outage_arr[outage_mask] = rng.choice(["Scheduled Load Shedding", "Voltage Fluctuation", "Emergency Outage"], size=outage_mask.sum())
    is_outage = outage_arr != "None"

    device_status_arr = np.where(is_outage, "offline", "operational")

    anomaly_arr = np.full(n, "Normal")
    anomaly_mask = rng.random(n) < 0.0001
    anomaly_arr[anomaly_mask] = "Abnormal"

    renewable_arr = np.full(n, "Active" if uses_renewables else "Not Installed")

    solar_arr = np.zeros(n)
    battery_soc_arr = np.zeros(n)
    grid_import_arr = np.zeros(n)
    grid_export_arr = np.zeros(n)

    if uses_renewables:
        hour_f = hours_arr + minutes_arr / 60.0
        sun_mask = (hour_f >= 6) & (hour_f <= 18)
        sun = np.exp(-((hour_f - 12.5) ** 2) / (2 * 3.2 ** 2))
        cloud = np.where(weather_arr == "Sunny", 1.0,
                         np.where(weather_arr == "Cloudy", 0.55,
                                  np.where(weather_arr == "Rainy", 0.3, 0.7)))
        solar_arr = np.where(sun_mask, 3.0 * sun * cloud * rng.uniform(0.92, 1.08, size=n), 0.0)
        solar_arr = np.round(solar_arr, 4)

        battery_mask = (hours_arr >= 18) & (hours_arr <= 22)
        battery_soc_arr = np.clip(80.0 + 20.0 * np.sin(np.arange(n) / 10000.0), 0, 100)
        battery_soc_arr = np.round(battery_soc_arr, 1)

    # Device power generation
    devices_data = {}
    for name in REQUIRED_DEVICES:
        vals = np.zeros(n)
        if name == "Solar_Inverter":
            vals = solar_arr.copy()
        elif name == "Battery_Storage":
            if uses_renewables:
                battery_mask = (hours_arr >= 18) & (hours_arr <= 22)
                vals[battery_mask] = np.round(1.5 * rng.uniform(0.5, 1.0, size=battery_mask.sum()), 4)
        elif name in {"Refrigerator_Main", "Refrigerator_Secondary", "WiFi_Router", "Smart_Hub",
                      "CCTV_Camera_1", "CCTV_Camera_2", "UPS_Backup", "Water_Purifier_Kitchen"}:
            vals = np.round(rng.uniform(0.02, 0.15, size=n), 4)
        elif name in {"Television_Living", "Television_Second", "Desktop_PC", "Laptop_1", "Laptop_2",
                      "Gaming_Console", "Projector", "Monitor_1", "Monitor_2"}:
            mask = rng.random(n) < 0.3
            vals[mask] = np.round(rng.uniform(0.05, 0.5, size=mask.sum()), 4)
        elif name in {"Ceiling_Fan_Living", "Ceiling_Fan_Bed1", "Ceiling_Fan_Bed2", "Ceiling_Fan_Kitchen",
                      "Table_Fan_Study", "Pedestal_Fan_Stand", "Exhaust_Fan_Kitchen", "Exhaust_Fan_Bath"}:
            mask = rng.random(n) < 0.4
            vals[mask] = np.round(rng.uniform(0.03, 0.12, size=mask.sum()), 4)
        elif name in {"LED_Lights_Living", "LED_Lights_Kitchen", "LED_Lights_Bed1", "LED_Lights_Bed2",
                      "LED_Lights_Study", "LED_Lights_Bathroom", "LED_Lights_Corridor",
                      "LED_Lights_Outdoor", "Garden_Lights", "Security_Lights",
                      "Security_Lights_Backyard", "Festival_String_Lights"}:
            mask = (hours_arr >= 6) & (hours_arr <= 23) | (rng.random(n) < 0.1)
            vals[mask] = np.round(rng.uniform(0.005, 0.05, size=mask.sum()), 4)
        elif name in {"Air_Conditioner_Bed1", "Air_Conditioner_Living", "Air_Conditioner_Study"}:
            mask = (temp_arr > 28) & (rng.random(n) < 0.5)
            vals[mask] = np.round(rng.uniform(0.8, 2.5, size=mask.sum()), 4)
        elif name in {"Microwave_Oven", "Induction_Stove_1", "Induction_Stove_2", "Electric_Kettle",
                      "Rice_Cooker", "Coffee_Machine", "Toaster", "Air_Fryer", "Mixer_Grinder"}:
            mask = rng.random(n) < 0.05
            vals[mask] = np.round(rng.uniform(0.5, 2.0, size=mask.sum()), 4)
        elif name in {"Washing_Machine", "Dishwasher", "Iron_Box", "Robot_Vacuum", "Vacuum_Cleaner"}:
            mask = rng.random(n) < 0.02
            vals[mask] = np.round(rng.uniform(0.3, 1.5, size=mask.sum()), 4)
        elif name in {"Geyser_Bathroom1", "Geyser_Bathroom2", "Water_Heater_Kitchen", "Room_Heater_Bed1", "Room_Heater_Bed2"}:
            mask = ((hours_arr >= 6) & (hours_arr <= 9)) | ((hours_arr >= 18) & (hours_arr <= 22))
            vals[mask] = np.round(rng.uniform(0.5, 3.0, size=mask.sum()), 4)
        elif name in {"Phone_Charger_1", "Phone_Charger_2", "Phone_Charger_3",
                      "Tablet_Charger_1", "Tablet_Charger_2", "Smartwatch_Charger_1",
                      "Smartwatch_Charger_2", "Laptop_Charger_1", "Laptop_Charger_2", "EV_Charger_Wall"}:
            mask = rng.random(n) < 0.15
            vals[mask] = np.round(rng.uniform(0.01, 0.2, size=mask.sum()), 4)
        else:
            mask = rng.random(n) < 0.1
            vals[mask] = np.round(rng.uniform(0.01, 0.3, size=mask.sum()), 4)

        # Apply anomaly multiplier
        anomaly_device_mask = rng.random(n) < 0.0001
        vals[anomaly_device_mask] = np.round(vals[anomaly_device_mask] * rng.uniform(1.5, 3.0, size=anomaly_device_mask.sum()), 4)

        # Apply outage
        vals[is_outage] = 0.0

        devices_data[name] = vals

    device_total = np.sum(np.array(list(devices_data.values())), axis=0)
    device_total = np.round(device_total, 4)

    if uses_renewables:
        net_load = device_total - solar_arr
        grid_import_arr = np.round(np.maximum(0.0, net_load), 4)
        grid_export_arr = np.round(np.maximum(0.0, -net_load), 4)
        total_consumed = device_total
    else:
        total_consumed = device_total

    cost_arr = np.where(uses_renewables, grid_import_arr * tariff_arr, total_consumed * tariff_arr)
    cost_arr = np.round(cost_arr, 3)
    carbon_arr = np.round((grid_import_arr if uses_renewables else total_consumed) * CO2_FACTOR, 4)

    # Build dataframe
    data = {
        "timestamp": pd.to_datetime(timestamps).strftime("%Y-%m-%d %H:%M:%S"),
        "Year": years_arr,
        "Month": months_arr,
        "Week": week_arr,
        "Day": days_arr,
        "DayOfWeek": dayofweek_arr,
        "Hour": hours_arr,
        "Minute": minutes_arr,
        "Season": seasons_arr,
        "Weather": weather_arr,
        "Temperature": temp_arr,
        "Humidity": humidity_arr,
        "OccupancyLevel": occupancy_arr,
        "ElectricityTariff": tariff_arr,
        "RenewableEnergyStatus": renewable_arr,
        "PowerOutageStatus": outage_arr,
        "DeviceStatus": device_status_arr,
        "DevicePowerConsumption": device_total,
        "TotalHouseholdConsumption": total_consumed,
        "EstimatedCost": cost_arr,
        "CarbonEmissions": carbon_arr,
        "AnomalyLabel": anomaly_arr,
        "SolarGeneration": solar_arr,
        "BatterySOC": battery_soc_arr,
        "GridImport": grid_import_arr,
        "GridExport": grid_export_arr,
    }
    for name in REQUIRED_DEVICES:
        data[name] = devices_data[name]

    df = pd.DataFrame(data, columns=TARGET_COLS)
    return df


def generate_dataset(name: str, seed: int, years: list[int], uses_renewables: bool = False) -> None:
    out_path = DATASETS_DIR / f"{name}.csv"
    print(f"Generating {name}.csv ({years})...", flush=True)
    df = _generate_vectorized(seed, years, uses_renewables)
    df.to_csv(out_path, index=False)
    print(f"Saved {out_path} ({len(df):,} rows, {len(df.columns)} cols)", flush=True)


def main() -> None:
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)

    tasks = [
        ("energy_dataset_2021", 42, [2021], False),
        ("energy_dataset_2024", 43, [2024], False),
        ("energy_dataset_2025", 44, [2025], False),
        ("energy_dataset_merged_3years", 45, [2023, 2024, 2025], False),
        ("_smoke_working", 11, [2023, 2024, 2025], False),
        ("_smoke_business", 21, [2024, 2025], False),
        ("_smoke_eco", 31, [2024, 2025], True),
        ("_smoke_slim", 41, [2021], False),
    ]

    for name, seed, years, renewables in tasks:
        generate_dataset(name, seed, years, renewables)

    print("All datasets normalized successfully.", flush=True)


if __name__ == "__main__":
    main()
