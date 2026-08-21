"""Weather, season, holiday and calendar-event simulation."""

import math
import random
from datetime import date, datetime, timedelta

# ---------------------------------------------------------------- seasons ---
SEASONS = {
    12: "Winter", 1: "Winter", 2: "Winter",
    3: "Summer", 4: "Summer", 5: "Summer",
    6: "Monsoon", 7: "Monsoon", 8: "Monsoon", 9: "Monsoon",
    10: "Post-Monsoon", 11: "Post-Monsoon",
}
SEASON_BY_MONTH = SEASONS


def season_for_month(month: int) -> str:
    return SEASONS.get(month, "Post-Monsoon")


def weather_label(temperature: float, cloud: float, rain: float, month: int) -> str:
    """Return a human weather label from conditions."""
    if rain >= 4.0:
        return "Storm"
    if rain >= 0.2:
        return "Rainy"
    if cloud >= 0.65:
        return "Cloudy"
    season = season_for_month(month)
    if season == "Summer" and temperature >= 37:
        return "Heatwave"
    if season == "Summer" and temperature >= 33:
        return "Dry Weather"
    if season == "Winter" and temperature <= 15:
        return "Cold Wave"
    if season == "Monsoon":
        return "High Humidity"
    if cloud >= 0.3:
        return "Cloudy"
    return "Sunny"


# ------------------------------------------------------------- temperature --
# Base daily temperature model for a North-Indian city (Delhi-like).
BASE_TEMP = {
    1: (7, 20), 2: (10, 24), 3: (14, 29), 4: (20, 36), 5: (25, 41),
    6: (28, 40), 7: (27, 36), 8: (26, 35), 9: (24, 33), 10: (18, 30),
    11: (12, 26), 12: (8, 22),
}


class WeatherEngine:
    """Deterministic-but-noisy per-minute weather generator."""

    def __init__(self, seed: int, year: int, cold_bias: float = 0.0, hot_bias: float = 0.0):
        self.rng = random.Random(seed)
        self.year = year
        self.cold_bias = cold_bias   # +1 = 1C colder year (used for 2023)
        self.hot_bias = hot_bias     # +1 = 1C hotter year (used for 2025)
        self._smooth = 0.0
        self.last_weather = (24.0, 60.0, "Sunny")

    def compute(self, current: datetime) -> tuple[float, float, str]:
        """Returns (temperature_c, humidity_pct, weather_label)."""
        doy = current.timetuple().tm_yday
        month = current.month
        hour = current.hour + current.minute / 60.0

        lo, hi = BASE_TEMP[month]
        # Seasonal annual wave + slow random year offset, smoothed.
        annual = (lo + hi) / 2.0
        amplitude = (hi - lo) / 2.0
        # Day-of-year sine peak around mid-July (doy 197).
        seasonal = annual + amplitude * math.sin(2 * math.pi * (doy - 104) / 365.0)

        # Intra-day wave: min at ~5am, max at ~3pm.
        daily = -amplitude * 0.55 * math.cos(2 * math.pi * (hour - 5.0) / 24.0)

        noise = self.rng.uniform(-0.9, 0.9)
        self._smooth = self._smooth * 0.92 + noise * 0.08
        temperature = seasonal + daily + self._smooth + self.cold_bias + self.hot_bias

        # Humidity: monsoon rainy months higher, dry summer lower.
        if month in (7, 8, 9):
            humidity = self.rng.uniform(62, 88)
        elif month in (3, 4, 5):
            humidity = self.rng.uniform(28, 52)
        elif month in (12, 1, 2):
            humidity = self.rng.uniform(50, 75)
        else:
            humidity = self.rng.uniform(45, 70)

        # Cloud/rain model
        rain_base = 0.0
        if month in (7, 8, 9):
            rain_base = self.rng.uniform(0, 1.2)
        elif month in (6, 10):
            rain_base = self.rng.uniform(0, 0.5)
        elif month in (3, 4, 5):
            rain_base = self.rng.uniform(0, 0.1)
        else:
            rain_base = self.rng.uniform(0, 0.2)

        if rain_base >= 0.9:
            rain = rain_base + self.rng.uniform(0.5, 4.0)
        elif rain_base >= 0.45:
            rain = rain_base + self.rng.uniform(0.05, 0.7)
        else:
            rain = rain_base + self.rng.uniform(0, 0.08)

        cloud = 0.12 + (0.75 if rain > 1.0 else 0.45 if rain > 0.3 else 0.0)
        cloud += self.rng.uniform(0, 0.2)
        if month in (7, 8, 9):
            cloud = min(0.98, cloud + 0.15)

        temperature = max(2.0, min(47.0, temperature))
        label = weather_label(temperature, min(cloud, 1.0), rain, month)
        return round(temperature, 1), round(humidity, 1), label


# ------------------------------------------------------------------ events --
EASTER = None  # placeholder; computed at runtime


def _easter(year: int) -> date:
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l_ = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l_) // 451
    month = (h + l_ - 7 * m + 114) // 31
    day = ((h + l_ - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def holidays_for(year: int) -> dict[date, str]:
    """Return {date: holiday_name} for major Indian holidays."""
    holidays = {
        date(year, 1, 1): "New Year",
        date(year, 1, 26): "Republic Day",
        date(year, 8, 15): "Independence Day",
        date(year, 10, 2): "Gandhi Jayanti",
        date(year, 12, 25): "Christmas",
        date(year, 5, 1): "Labour Day",
        date(year, 8, 1): "Ugadi/Ona",   # region-specific; placeholder
        date(year, 6, 1): "Bakrid",       # approx, seen as generic festival
    }
    # Festivals that shift every year (approx. dates, lunar-based).
    approx_lunar = {
        2021: {"Diwali": date(2021, 11, 4), "Holi": date(2021, 3, 29),
               "Eid": date(2021, 5, 13), "Ganesh": date(2021, 9, 10)},
        2022: {"Diwali": date(2022, 10, 24), "Holi": date(2022, 3, 18),
               "Eid": date(2022, 5, 3), "Ganesh": date(2022, 8, 31)},
        2023: {"Diwali": date(2023, 11, 12), "Holi": date(2023, 3, 8),
               "Eid": date(2023, 4, 22), "Ganesh": date(2023, 9, 19)},
        2024: {"Diwali": date(2024, 10, 31), "Holi": date(2024, 3, 25),
               "Eid": date(2024, 4, 10), "Ganesh": date(2024, 9, 7)},
        2025: {"Diwali": date(2025, 10, 20), "Holi": date(2025, 3, 14),
               "Eid": date(2025, 3, 31), "Ganesh": date(2025, 8, 27)},
        2026: {"Diwali": date(2026, 11, 8), "Holi": date(2026, 3, 4),
               "Eid": date(2026, 3, 20), "Ganesh": date(2026, 9, 15)},
    }
    lunar = approx_lunar.get(year, {})
    for name, day in lunar.items():
        holidays[day] = name
    return holidays
