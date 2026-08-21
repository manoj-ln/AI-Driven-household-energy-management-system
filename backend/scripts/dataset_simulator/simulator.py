"""Core per-minute simulation engine."""

import csv
import math
import random
from datetime import datetime, timedelta

from .config import META_COLUMNS, Scenario
from .devices import DEVICE_CATALOG
from .environment import WeatherEngine, season_for_month
from .occupancy import OccupancyEngine

# Grid emission factor (kg CO2 per kWh) - Indian national average.
CO2_FACTOR = 0.82

OUTAGE_NONE = "None"
OUTAGE_SHED = "Scheduled Load Shedding"
OUTAGE_VOLTAGE = "Voltage Fluctuation"
OUTAGE_EMERGENCY = "Emergency Outage"

STATUS_OK = "operational"
STATUS_MAINT = "maintenance"
STATUS_OFFLINE = "offline"

# Devices that keep running on UPS/battery during an outage.
BACKED_UP_DEVICES = {
    "WiFi_Router", "Smart_Hub", "Smart_Doorbell", "Smart_Lock",
    "CCTV_Camera_1", "CCTV_Camera_2", "CCTV_Camera_3",
    "Refrigerator_Main", "UPS_Backup", "Battery_Backup_UPS",
    "Server_NAS", "Network_Switch", "Security_Lights",
    "Phone_Charger_1", "Phone_Charger_2",
    "Battery_Storage", "Solar_Inverter",
}

# Supply-side devices excluded from household-consumption sums.
SUPPLY_DEVICES = {"Solar_Inverter", "Battery_Storage", "Battery_Backup_UPS", "Generator"}


class DeviceState:
    __slots__ = (
        "profile", "cycle_on", "cycle_remaining", "burst_remaining",
        "charging", "charge_remaining", "maintenance_today", "anomaly_in_window",
    )

    def __init__(self, profile: dict):
        self.profile = profile
        self.cycle_on = False
        self.cycle_remaining = 0
        self.burst_remaining = 0
        self.charging = False
        self.charge_remaining = 0
        self.maintenance_today = False
        self.anomaly_in_window = False


class Simulator:
    """Generates one household's per-minute dataset for configured years."""

    def __init__(
        self,
        scenario: Scenario,
        seed: int,
        *,
        cold_bias: float = 0.0,
        hot_bias: float = 0.0,
        outage_overrides: list[str] | None = None,
        slim_columns: dict[str, str] | None = None,
    ):
        self.scenario = scenario
        self.seed = seed
        self.rng = random.Random(seed)
        self.outage_overrides = outage_overrides or []

        # slim_columns: maps output-column-name -> catalog-device-name.
        # Used to emit the compact 2021-style reference schema.
        self.slim_columns = slim_columns
        self.slim_mode = slim_columns is not None
        if self.slim_mode:
            self.device_names = [name for name in slim_columns.values() if name in DEVICE_CATALOG]
        else:
            self.device_names = [name for name, profile in DEVICE_CATALOG.items() if scenario.power_flags.get(name, False)]

        self.weather = WeatherEngine(seed + 17, scenario.years[0], cold_bias=cold_bias, hot_bias=hot_bias)
        self.occupancy = OccupancyEngine(scenario.name, seed + 31)
        self.occupancy.build_calendar(scenario.years)

        self.device_states = {name: DeviceState(DEVICE_CATALOG[name]) for name in self.device_names}
        self.phases = {name: (self._djb2(name) % 97) for name in self.device_names}

        self.hour_accum = {h: 0.0 for h in range(24)}
        self.day_accum = {}
        self.month_accum = {m: 0.0 for m in range(1, 13)}
        self.battery_soc = 80.0

    @staticmethod
    def _djb2(text: str) -> int:
        h = 5381
        for ch in text:
            h = ((h * 33) ^ ord(ch)) & 0xFFFFFFFF
        return h

    # ------------------------------------------------------------ helpers ---
    @staticmethod
    def _in_window(hour: int, windows) -> bool:
        if not windows:
            return False
        # Normalize: accept a flat list of hours (e.g. [8..23]), or a list of
        # (lo, hi) tuples (overnight windows allowed, e.g. (22, 5)).
        if isinstance(windows[0], int):
            return hour in windows
        for lo, hi in windows:
            if lo <= hi:
                if lo <= hour < hi:
                    return True
            else:  # overnight window, e.g. (22, 5)
                if hour >= lo or hour < hi:
                    return True
        return False

    def _device_multiplier(self, name: str, current: datetime, temp: float, people: int, plan) -> float:
        """Extra lifestyle multiplier on top of the base profile."""
        m = 1.0
        if plan.has_guests:
            m += 0.25
        if plan.festival:
            m += 0.35
        if plan.has_party:
            m += 0.5
        if plan.movie_night and any(k in name for k in ("Television", "Home_Theater", "Soundbar", "Projector")):
            m += 0.6
        if plan.cricket_night and ("Television" in name or "Soundbar" in name):
            m += 0.9
        if plan.exam_day and any(k in name for k in ("LED_Lights_Study", "Desktop", "Laptop")):
            m += 0.7
        if plan.school_off and any(k in name for k in ("Television", "Gaming", "Laptop")):
            m += 0.35
        if plan.wfh_day and any(k in name for k in ("Laptop", "Monitor", "Desktop", "Video_Conference", "Printer")):
            m += 0.55
        if plan.peak_business and self.scenario.name == "business":
            m += 0.4
        if (self.scenario.name == "eco" and self._in_window(current.hour, ((9, 17),))
                and "Charger" in name):
            m += 0.15
        if people <= 1:
            m *= 0.85
        elif people >= 5:
            m *= 1.15
        return m

    # ------------------------------------------------------ device power ----
    def _device_power(self, name: str, current: datetime, temp: float, plan) -> float:
        """Returns appliance power draw in kW (already includes lifestyle modifiers)."""
        profile = DEVICE_CATALOG[name]
        state = self.device_states[name]
        kind = profile["kind"]
        hour = current.hour
        month = current.month
        people, _level = self.occupancy.occupancy_level(current)
        mult = self._device_multiplier(name, current, temp, people, plan)

        if kind == "continuous":
            return profile["rated_kw"]

        if kind == "cycle":
            if "months" in profile and month not in profile["months"]:
                state.cycle_on = False
                return 0.0
            if state.cycle_remaining > 0:
                state.cycle_remaining -= 1
                power = profile["rated_kw"]
                if current.minute == 0:
                    power *= 1.9
                if temp > 32:
                    power *= 1.0 + (temp - 32) * 0.01
                return round(power, 4)
            state.cycle_on = False
            on_fraction = profile["on_frac"]
            if temp > 30:
                on_fraction = min(0.9, on_fraction + 0.08)
            if self.rng.random() < on_fraction * mult:
                state.cycle_remaining = max(2, int(profile["cycle_min"] * self.rng.uniform(0.8, 1.2)))
                state.cycle_remaining -= 1
                return profile["rated_kw"]
            return 0.0

        if kind == "timed":
            if state.burst_remaining > 0:
                state.burst_remaining -= 1
                power = profile["rated_kw"] * self.rng.uniform(0.85, 1.15) * mult
                if state.anomaly_in_window and self.rng.random() < 0.6:
                    power *= 1.6
                return round(power, 4)
            if not self._in_window(hour, profile["hours"]):
                return 0.0
            pct = profile.get("pct", 100)
            if self.rng.random() * 100 >= pct * mult:
                return 0.0
            burst_lo, burst_hi = profile["burst"]
            if "Television" in name or "Projector" in name or "Gaming" in name:
                if plan.movie_night or plan.cricket_night:
                    burst_hi = int(burst_hi * 1.8)
                if plan.school_off:
                    burst_hi = int(burst_hi * 1.3)
            burst = int(self.rng.uniform(burst_lo, burst_hi))
            state.burst_remaining = max(1, burst - 1)
            if plan.has_guests or plan.has_party:
                state.burst_remaining = int(state.burst_remaining * 1.2)
            return round(profile["rated_kw"] * mult, 4)

        if kind == "weather":
            if not self._in_window(hour, profile["hours"]):
                return 0.0
            min_c = profile.get("min_c", 0)
            max_c = profile.get("max_c", 40)
            if temp <= min_c:
                return 0.0
            raw = min(1.0, (temp - min_c) / max(max_c - min_c, 1.0))
            season = season_for_month(month)
            if "Geyser" in name or "Heater" in name:
                if season == "Winter":
                    raw *= profile.get("winter_ratio", 1.0)
                elif season == "Summer":
                    raw *= profile.get("summer_ratio", 0.3)
            surge = 1.35 if current.minute < int(profile.get("warmup", 0) * 60) else 1.0
            return round(profile["rated_kw"] * max(0.25, raw) * surge * mult, 4)

        if kind == "charge":
            if state.charging:
                state.charge_remaining -= 1
                if state.charge_remaining <= 0:
                    state.charging = False
                    return 0.0
                power = profile["rated_kw"] * 0.92
                if state.charge_remaining < profile["charge_min"] * 0.15:
                    power *= 0.6
                return round(power, 4)
            lo, hi = profile.get("hour_pick", (20, 23))
            if not self._in_window(hour, ((lo, hi),)):
                return 0.0
            pct = profile.get("pct", 100)
            if self.rng.random() < (pct / 100.0) * mult * 0.008:
                state.charging = True
                state.charge_remaining = int(profile["charge_min"] * self.rng.uniform(0.9, 1.1))
            return 0.0

        if kind == "seasonal":
            if month not in profile["months"]:
                return 0.0
            if not self._in_window(hour, profile["hours"]):
                return 0.0
            if self.rng.random() * 100 < profile.get("pct", 100) * mult:
                return profile["rated_kw"]
            return 0.0

        if kind == "solar":
            return self._solar_power(current)

        if kind == "battery":
            return self._battery_power(current, profile)

        return 0.0

    def _solar_power(self, current: datetime) -> float:
        """Solar generation in kW based on sun elevation + cloud cover."""
        temp, _h, weather_label = self.weather.last_weather
        hour = current.hour + current.minute / 60.0
        if hour < 6 or hour > 18:
            return 0.0
        sun = math.exp(-((hour - 12.5) ** 2) / (2 * 3.2 ** 2))
        cloud_factor = {
            "Sunny": 1.0, "Dry Weather": 1.0, "Cloudy": 0.55, "High Humidity": 0.6,
            "Rainy": 0.3, "Storm": 0.15, "Heatwave": 0.9, "Cold Wave": 0.85,
        }.get(weather_label, 0.7)
        noise = self.rng.uniform(0.92, 1.08)
        capacity = 3.0 if self.scenario.power_flags.get("Solar_Inverter") else 0.0
        if capacity <= 0:
            return 0.0
        return round(max(0.0, capacity * sun * cloud_factor * noise), 4)

    def _battery_power(self, current: datetime, profile: dict) -> float:
        """Positive kW = battery discharging (offsets load). Charging handled via
        a negative contribution returned from the calling logic."""
        if not self.scenario.uses_renewables:
            return 0.0
        if 18 <= current.hour <= 22 and self.battery_soc > 20:
            self.battery_soc = max(0.0, self.battery_soc - 0.02)
            return round(profile["rated_kw"] * 0.6, 4)
        return 0.0

    def _battery_charge_draw(self, current: datetime, solar: float) -> float:
        """Draw from solar surplus to charge battery; returns kW (positive = load)."""
        if not self.scenario.uses_renewables:
            return 0.0
        if 10 <= current.hour <= 15 and solar > 0.1 and self.battery_soc < 95:
            draw = min(solar * 0.7, solar)
            self.battery_soc = min(100.0, self.battery_soc + 0.02)
            return round(draw, 4)
        return 0.0

    # ------------------------------------------------------------- tariffs ---
    def _tariff_pu(self, current: datetime) -> float:
        name = self.scenario.name
        hour = current.hour
        if name == "business":
            return 8.5
        if name == "eco":
            if 9 <= hour <= 16:
                return 4.5
            if 18 <= hour <= 22:
                return 10.5
            if hour >= 22 or hour < 5:
                return 5.5
            return 6.5
        base = 6.26
        if 18 <= hour <= 22:
            base *= 1.2
        elif hour < 5:
            base *= 0.85
        if self.month_accum[current.month] > 400:
            base *= 1.15
        elif self.month_accum[current.month] < 120:
            base *= 0.95
        return round(base, 2)

    # ----------------------------------------------------------- anomalies ---
    def _maybe_inject_anomaly(self, name: str) -> None:
        prof = DEVICE_CATALOG[name]
        if prof["kind"] in ("continuous", "solar", "battery", "generator"):
            return
        if "Fridge" in name or "Freezer" in name:
            if self.rng.random() < 0.0000018:
                self.device_states[name].cycle_remaining = int(60 * self.rng.uniform(0.5, 1.5))
                self.device_states[name].anomaly_in_window = True
        elif self.rng.random() < 0.0000012:
            state = self.device_states[name]
            state.burst_remaining = max(state.burst_remaining, int(30 * self.rng.uniform(1, 3)))
            state.anomaly_in_window = True

    def _clear_anomaly_flags(self) -> None:
        for state in self.device_states.values():
            if state.anomaly_in_window and state.burst_remaining == 0 and not state.cycle_on:
                state.anomaly_in_window = False

    def _outage_status(self, current: datetime) -> str:
        """Deterministic scheduled shedding + rare random outages."""
        dkey = f"{self.scenario.name}:{current.strftime('%Y%m%d')}:{current.hour}"
        h = self._djb2(dkey)
        if current.month in (4, 5, 6) and 15 <= current.hour <= 20 and (h % 10) < 3:
            return OUTAGE_SHED
        r = self.rng.random()
        if r < 0.00002:
            return OUTAGE_EMERGENCY
        if r < 0.00006:
            return OUTAGE_VOLTAGE
        hour_key = current.strftime("%Y-%m-%d %H")
        if hour_key in self.outage_overrides:
            return OUTAGE_EMERGENCY
        return OUTAGE_NONE

    # ------------------------------------------------------------- main run ---
    def run(self, filepath, *, log_every_minutes: int = 10080, limit_minutes: int | None = None) -> dict:
        first_year = self.scenario.years[0]
        start = datetime(first_year, 1, 1, 0, 0, 0)
        end = datetime(self.scenario.years[-1], 12, 31, 23, 59, 0)
        if limit_minutes is not None:
            end = start + timedelta(minutes=limit_minutes - 1)

        if self.slim_mode:
            header = [
                "timestamp", "temperature", "humidity", "total_consumption",
            ] + list(self.slim_columns.keys())
        else:
            header = META_COLUMNS + self.device_names

        # Annual maintenance calendar: every device 1-2 days/year.
        maintenance_days: dict[str, set[str]] = {}
        for name in self.device_names:
            days = set()
            for year in self.scenario.years:
                for _ in range(self.rng.randint(1, 2)):
                    month = self.rng.randint(1, 12)
                    day = self.rng.randint(1, 28 if month != 2 else 27)
                    days.add(f"{year}-{month:02d}-{day:02d}")
            maintenance_days[name] = days

        total_rows = 0
        total_kwh = 0.0
        total_anomalies = 0
        outage_minutes = 0
        maintenance_minutes = 0
        current = start

        with open(filepath, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(header)

            while current <= end:
                plan = self.occupancy.plan_for(current)
                _people, level = self.occupancy.occupancy_level(current)
                temp, humidity, weather_label = self.weather.compute(current)
                self.weather.last_weather = (temp, humidity, weather_label)

                outage = self._outage_status(current)
                is_outage = outage != OUTAGE_NONE
                if is_outage:
                    outage_minutes += 1

                date_key = current.strftime("%Y-%m-%d")
                for name in self.device_names:
                    self.device_states[name].maintenance_today = date_key in maintenance_days[name]

                # Device simulation.
                per_device = {}
                device_power_total = 0.0
                for name in self.device_names:
                    self._maybe_inject_anomaly(name)
                    state = self.device_states[name]

                    if state.maintenance_today:
                        per_device[name] = 0.0
                        maintenance_minutes += 1
                        continue

                    if is_outage and name not in BACKED_UP_DEVICES and not self._generator_powered(name):
                        per_device[name] = 0.0
                        continue

                    power = self._device_power(name, current, temp, plan)
                    per_device[name] = round(power, 4)

                self._clear_anomaly_flags()

                # Household consumption = sum of load devices (exclude supply-side).
                load_total = sum(v for n, v in per_device.items() if n not in SUPPLY_DEVICES)
                load_total = round(load_total, 4)

                # Eco accounting: solar, battery, grid.
                solar = per_device.get("Solar_Inverter", 0.0)
                battery_out = per_device.get("Battery_Storage", 0.0)
                solar_used = 0.0
                grid_import = 0.0
                grid_export = 0.0
                if self.scenario.uses_renewables:
                    charge_draw = self._battery_charge_draw(current, solar)
                    net_load = load_total + charge_draw - solar - battery_out
                    if net_load > 0:
                        grid_import = round(net_load, 4)
                    else:
                        grid_export = round(-net_load, 4)
                    solar_used = min(solar, load_total + charge_draw)
                    total_consumed = load_total
                else:
                    total_consumed = load_total

                total_consumed = round(max(0.0, total_consumed), 4)
                tariff = self._tariff_pu(current)
                grid_based = grid_import if self.scenario.uses_renewables else total_consumed
                cost = grid_based * tariff
                carbon = grid_based * CO2_FACTOR

                abnormal = any(self.device_states[n].anomaly_in_window for n in self.device_names)
                if abnormal:
                    total_anomalies += 1

                row_vals = {
                    "timestamp": current.strftime("%Y-%m-%d %H:%M:%S"),
                    "Year": current.year,
                    "Month": current.month,
                    "Week": current.isocalendar().week,
                    "Day": current.day,
                    "DayOfWeek": current.weekday(),
                    "Hour": current.hour,
                    "Minute": current.minute,
                    "Season": season_for_month(current.month),
                    "Weather": weather_label,
                    "Temperature": temp,
                    "Humidity": humidity,
                    "OccupancyLevel": level,
                    "ElectricityTariff": tariff,
                    "RenewableEnergyStatus": "Active" if self.scenario.uses_renewables else "Not Installed",
                    "PowerOutageStatus": outage,
                    "DeviceStatus": STATUS_OK if not is_outage else STATUS_OFFLINE,
                    "DevicePowerConsumption": load_total,
                    "TotalHouseholdConsumption": total_consumed,
                    "EstimatedCost": round(cost, 3),
                    "CarbonEmissions": round(carbon, 4),
                    "AnomalyLabel": "Abnormal" if abnormal else "Normal",
                }
                if self.scenario.uses_renewables:
                    row_vals.update({
                        "SolarGeneration": round(solar, 4),
                        "BatterySOC": round(self.battery_soc, 1),
                        "GridImport": grid_import,
                        "GridExport": grid_export,
                    })

                # Accumulators.
                total_kwh += total_consumed
                self.hour_accum[current.hour] += total_consumed
                self.day_accum[date_key] = self.day_accum.get(date_key, 0.0) + total_consumed
                self.month_accum[current.month] += total_consumed

                if self.slim_mode:
                    # Compact 2021-style reference row.
                    device_row = [per_device.get(self.slim_columns[col], 0.0) for col in self.slim_columns]
                    writer.writerow([
                        current.strftime("%Y-%m-%d %H:%M:%S"),
                        temp, humidity, total_consumed,
                    ] + device_row)
                else:
                    row = [row_vals.get(col, "") for col in META_COLUMNS]
                    row += [per_device[name] for name in self.device_names]
                    writer.writerow(row)

                total_rows += 1
                current += timedelta(minutes=1)

                if total_rows % log_every_minutes == 0:
                    print(f"  ... {total_rows:,} rows", flush=True)

        return {
            "rows": total_rows,
            "devices": len(self.device_names),
            "total_kwh": round(total_kwh, 1),
            "anomalies": total_anomalies,
            "outage_minutes": outage_minutes,
            "maintenance_minutes": maintenance_minutes,
        }

    def _generator_powered(self, name: str) -> bool:
        """Business scenario: generator keeps critical office gear running."""
        if self.scenario.name != "business":
            return False
        if self.device_states.get("Generator") is None:
            return False
        return name in {
            "Desktop_PC", "Desktop_PC_2", "Monitor_1", "Monitor_2",
            "WiFi_Router", "Server_NAS", "Network_Switch", "Printer",
            "Photocopier", "LED_Lights_Living", "LED_Lights_Study",
        }

    @property
    def hash_seed(self) -> int:
        return self._djb2(self.scenario.name)
