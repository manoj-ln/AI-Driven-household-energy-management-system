"""Occupancy + calendar-day behaviour engine (scenario specific)."""

import random
from datetime import date, datetime, timedelta

from .environment import holidays_for

# Hourly people-at-home for typical weekdays/weekends per scenario.
# --------------------------------------------------------------------------
WORKING_WEEKDAY = {
    0: 4, 1: 4, 2: 4, 3: 4, 4: 4, 5: 2, 6: 4, 7: 4, 8: 2, 9: 1,
    10: 1, 11: 1, 12: 1, 13: 1, 14: 1, 15: 1, 16: 1, 17: 3, 18: 4,
    19: 4, 20: 4, 21: 4, 22: 4, 23: 4,
}
WORKING_WEEKEND = {
    0: 4, 1: 4, 2: 4, 3: 4, 4: 4, 5: 3, 6: 4, 7: 4, 8: 4, 9: 4,
    10: 4, 11: 4, 12: 4, 13: 4, 14: 4, 15: 4, 16: 4, 17: 4, 18: 4,
    19: 4, 20: 4, 21: 4, 22: 4, 23: 4,
}

BUSINESS_WEEKDAY = {
    0: 2, 1: 2, 2: 2, 3: 1, 4: 1, 5: 1, 6: 2, 7: 2, 8: 2, 9: 2,
    10: 2, 11: 2, 12: 2, 13: 2, 14: 2, 15: 2, 16: 2, 17: 2, 18: 2,
    19: 2, 20: 2, 21: 2, 22: 2, 23: 2,
}
BUSINESS_WEEKEND = {
    0: 2, 1: 2, 2: 1, 3: 1, 4: 1, 5: 1, 6: 2, 7: 2, 8: 2, 9: 2,
    10: 2, 11: 2, 12: 2, 13: 1, 14: 1, 15: 1, 16: 1, 17: 2, 18: 2,
    19: 2, 20: 2, 21: 2, 22: 2, 23: 2,
}

ECO_WEEKDAY = {
    0: 4, 1: 4, 2: 4, 3: 4, 4: 4, 5: 2, 6: 4, 7: 4, 8: 3, 9: 1,
    10: 1, 11: 1, 12: 1, 13: 1, 14: 1, 15: 1, 16: 2, 17: 3, 18: 4,
    19: 4, 20: 4, 21: 4, 22: 4, 23: 4,
}
ECO_WEEKEND = {
    0: 4, 1: 4, 2: 4, 3: 4, 4: 4, 5: 3, 6: 4, 7: 4, 8: 4, 9: 4,
    10: 4, 11: 4, 12: 4, 13: 4, 14: 4, 15: 4, 16: 4, 17: 4, 18: 4,
    19: 4, 20: 4, 21: 4, 22: 4, 23: 4,
}

BASE_WEEKDAY = {
    0: 2, 1: 2, 2: 2, 3: 2, 4: 2, 5: 1, 6: 2, 7: 2, 8: 1, 9: 1,
    10: 1, 11: 1, 12: 1, 13: 1, 14: 1, 15: 1, 16: 1, 17: 2, 18: 2,
    19: 2, 20: 2, 21: 2, 22: 2, 23: 2,
}
BASE_WEEKEND = {
    0: 2, 1: 2, 2: 2, 3: 2, 4: 2, 5: 1, 6: 2, 7: 2, 8: 2, 9: 2,
    10: 2, 11: 2, 12: 2, 13: 2, 14: 2, 15: 2, 16: 2, 17: 2, 18: 2,
    19: 2, 20: 2, 21: 2, 22: 2, 23: 2,
}

OCCUPANCY_PROFILES = {
    "working": (WORKING_WEEKDAY, WORKING_WEEKEND),
    "business": (BUSINESS_WEEKDAY, BUSINESS_WEEKEND),
    "eco": (ECO_WEEKDAY, ECO_WEEKEND),
    "base": (BASE_WEEKDAY, BASE_WEEKEND),
}

LEVEL_NAMES = {
    0: "Empty House", 1: "Single Occupant", 2: "Couple", 3: "Family",
    4: "Family", 5: "Joint Family", 6: "Guests",
}


class DayPlan:
    """Behavioural flags for a single calendar day."""

    def __init__(self, current: date):
        self.date = current
        self.is_weekend = current.weekday() >= 5
        self.is_holiday = False
        self.holiday_name = None
        self.is_vacation = False
        self.has_guests = False
        self.has_party = False
        self.movie_night = False
        self.cricket_night = False
        self.exam_day = False
        self.school_off = False
        self.wfh_day = False
        self.travel_day = False
        self.peak_business = False
        self.festival = False


class OccupancyEngine:
    """Per-day and per-minute occupancy + activity drivers."""

    def __init__(self, scenario_name: str, seed: int):
        self.scenario = scenario_name
        self.rng = random.Random(seed)
        self.holidays = holidays_for(2021)
        self.profile = OCCUPANCY_PROFILES.get(scenario_name, OCCUPANCY_PROFILES["base"])
        self._year_plans: dict[int, dict[date, DayPlan]] = {}

    # ------------------------------------------------------------------
    def build_calendar(self, years: list[int]) -> None:
        for year in years:
            self._build_year(year)

    def _build_year(self, year: int) -> None:
        plans: dict[date, DayPlan] = {}
        self.holidays = holidays_for(year)

        start = date(year, 1, 1)
        end = date(year, 12, 31)
        current = start
        while current <= end:
            plan = DayPlan(current)
            if current in self.holidays:
                plan.is_holiday = True
                plan.holiday_name = self.holidays[current]
                if any(name in plan.holiday_name for name in ("Diwali", "New Year", "Christmas", "Holi", "Eid", "Ganesh", "Gandhi", "Independence", "Republic")):
                    plan.festival = True
            if self.scenario == "working":
                # School breaks: May + first 2 weeks June + last 2 weeks Dec.
                if current.month == 5 or (current.month == 6 and current.day <= 15) or (current.month == 12 and current.day >= 16):
                    plan.school_off = True
                # Exam periods: Mar & Sep weekdays.
                if current.month in (3, 9) and current.weekday() < 5:
                    plan.exam_day = True
            if self.scenario == "business":
                # Tax filing (Apr/Jun), peak season (Nov/Dec), inventory (early Feb).
                if current.month in (4, 6, 11, 12) or (current.month == 2 and current.day <= 10):
                    plan.peak_business = True
            plans[current] = plan
            current += timedelta(days=1)

        # Stable pseudo-random per-day event assignment.
        for current, plan in plans.items():
            dkey = f"{self.scenario}:{current.isoformat()}"
            self.rng.seed((hash(dkey) & 0xFFFFFFFF) ^ (year * 1000003))
            r = self.rng.random

            if self.scenario == "working":
                if not plan.is_weekend and not plan.is_holiday and current.weekday() in (0, 4):
                    if r() < 0.55:
                        plan.wfh_day = True
                        plan.holiday_name = "Work From Home"
                if current.month == 5 and current.day in (16, 17, 18, 19, 20):
                    plan.is_vacation = True
                if current.month == 12 and current.day in (23, 24):
                    plan.is_vacation = True
                if plan.is_weekend and r() < 0.1:
                    plan.has_guests = True
                if plan.is_weekend and r() < 0.25:
                    plan.movie_night = True
                if not plan.is_weekend and r() < 0.03:
                    plan.cricket_night = True
                if r() < 0.022:
                    plan.has_party = True
                if plan.festival:
                    plan.has_party = True

            elif self.scenario == "business":
                if plan.is_weekend and r() < 0.5:
                    plan.peak_business = True
                    plan.wfh_day = True
                if current.day == 12 and current.month in (3, 7, 9, 11):
                    plan.travel_day = True
                    plan.holiday_name = "Business Travel"
                if current.weekday() == 0 and current.day <= 7:
                    plan.wfh_day = True
                if plan.festival or r() < 0.02:
                    plan.has_party = True

            elif self.scenario == "eco":
                if r() < 0.02:
                    plan.is_vacation = True
                if plan.is_weekend and r() < 0.12:
                    plan.has_guests = True
                if plan.is_weekend and r() < 0.3:
                    plan.movie_night = True
                if plan.festival:
                    plan.has_party = True

            else:  # base (2021-style data)
                if plan.is_weekend and r() < 0.1:
                    plan.has_guests = True
                if plan.is_weekend and r() < 0.2:
                    plan.movie_night = True
                if plan.festival:
                    plan.has_party = True

        self._year_plans[year] = plans

    def plan_for(self, current: datetime) -> DayPlan:
        return self._year_plans[current.year][current.date()]

    # ------------------------------------------------------------------
    def occupancy_level(self, current: datetime) -> tuple[int, str]:
        """Returns (people, level_name)."""
        plan = self.plan_for(current)
        weekday_map, weekend_map = self.profile
        hour = current.hour

        if plan.is_holiday or plan.is_weekend:
            base = weekend_map[hour]
        else:
            base = weekday_map[hour]

        people = base
        if plan.is_vacation:
            people = max(2, weekday_map[hour])
        elif plan.travel_day:
            people = 0 if 9 <= hour <= 20 else 1
        elif plan.has_guests:
            people = min(6, base + 2)
        elif plan.wfh_day and not plan.is_weekend:
            people = max(2, base + 1)
        elif plan.peak_business and self.scenario == "business":
            people = max(2, base)

        level = "Guests" if plan.has_guests else (LEVEL_NAMES.get(people, "Family"))
        return people, level

    def is_holiday(self, current: datetime) -> bool:
        return self.plan_for(current).is_holiday
