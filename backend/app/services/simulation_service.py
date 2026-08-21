from app.services.dataset_service import DatasetService
from app.services.prediction_service import PredictionService


class SimulationService:
    @classmethod
    def run_scenario(
        cls,
        *,
        scenario: str,
        hours: int = 24,
        rate_per_kwh: float = 6.26,
        optimization_strength: float = 18.0,
        solar_offset: float = 45.0,
        battery_shift: float = 12.0,
        appliance_upgrade: float = 10.0,
        demand_response: float = 8.0,
        occupancy_mode: str = "family",
    ) -> dict[str, object]:
        hours = max(6, min(int(hours), 168))
        rate_per_kwh = round(float(rate_per_kwh), 2)

        base_summary = DatasetService.get_summary()
        base_daily = float(base_summary.get("daily_consumption", 0.0))
        baseline_predictions = PredictionService.predict_multi_step(hours)
        if not baseline_predictions:
            baseline_predictions = cls._fallback_predictions(hours, base_daily)

        occupancy_multiplier = {
            "family": 1.0,
            "working_day": 0.88,
            "vacation": 0.62,
            "guests": 1.14,
            "students": 0.94,
        }.get(occupancy_mode, 1.0)

        normalized_baseline = cls._apply_occupancy_profile(baseline_predictions, occupancy_mode, occupancy_multiplier)
        scenario_predictions, drivers = cls._apply_scenario(
            normalized_baseline,
            scenario=scenario,
            optimization_strength=optimization_strength,
            solar_offset=solar_offset,
            battery_shift=battery_shift,
            appliance_upgrade=appliance_upgrade,
            demand_response=demand_response,
        )

        baseline_total = round(sum(float(point["energy_kwh"]) for point in normalized_baseline), 3)
        scenario_total = round(sum(float(point["energy_kwh"]) for point in scenario_predictions), 3)
        baseline_cost = round(baseline_total * rate_per_kwh, 2)
        scenario_cost = round(scenario_total * rate_per_kwh, 2)
        savings_kwh = round(baseline_total - scenario_total, 3)
        savings_inr = round(baseline_cost - scenario_cost, 2)
        peak_baseline = round(max(float(point["energy_kwh"]) for point in normalized_baseline), 3) if normalized_baseline else 0.0
        peak_scenario = round(max(float(point["energy_kwh"]) for point in scenario_predictions), 3) if scenario_predictions else 0.0

        baseline_peak_window, baseline_peak_window_kwh = cls._peak_window(normalized_baseline)
        scenario_peak_window, scenario_peak_window_kwh = cls._peak_window(scenario_predictions)
        baseline_load_factor = cls._load_factor(normalized_baseline)
        scenario_load_factor = cls._load_factor(scenario_predictions)
        self_consumption_ratio = cls._self_consumption_ratio(scenario, solar_offset, battery_shift)

        calculation_steps = [
            {
                "step": "Forecast horizon",
                "formula": "User-selected planning period",
                "value": hours,
                "unit": "hours",
            },
            {
                "step": "Baseline energy",
                "formula": "Sum of hourly forecast after occupancy profile",
                "value": baseline_total,
                "unit": "kWh",
            },
            {
                "step": "Scenario energy",
                "formula": "Baseline adjusted by scenario drivers, device-efficiency, and demand response",
                "value": scenario_total,
                "unit": "kWh",
            },
            {
                "step": "Baseline cost",
                "formula": f"{baseline_total} x {rate_per_kwh}",
                "value": baseline_cost,
                "unit": "INR",
            },
            {
                "step": "Scenario cost",
                "formula": f"{scenario_total} x {rate_per_kwh}",
                "value": scenario_cost,
                "unit": "INR",
            },
            {
                "step": "Cost savings",
                "formula": f"{baseline_cost} - {scenario_cost}",
                "value": savings_inr,
                "unit": "INR",
            },
        ]

        summary_cards = [
            {"label": "Baseline Energy", "value": baseline_total, "unit": "kWh"},
            {"label": "Scenario Energy", "value": scenario_total, "unit": "kWh"},
            {"label": "Baseline Cost", "value": baseline_cost, "unit": "INR"},
            {"label": "Scenario Cost", "value": scenario_cost, "unit": "INR"},
            {"label": "Peak Reduction", "value": round(peak_baseline - peak_scenario, 3), "unit": "kWh"},
            {"label": "Savings", "value": savings_inr, "unit": "INR"},
        ]

        monthly_projection = cls._projection(scenario_cost, savings_inr, rate_per_kwh, "month")
        yearly_projection = cls._projection(scenario_cost, savings_inr, rate_per_kwh, "year")
        phase_breakdown = cls._phase_breakdown(normalized_baseline, scenario_predictions, rate_per_kwh)
        scenario_score = cls._scenario_score(
            savings_inr=savings_inr,
            peak_reduction=max(peak_baseline - peak_scenario, 0.0),
            load_factor_gain=max(scenario_load_factor - baseline_load_factor, 0.0),
        )

        return {
            "scenario": scenario,
            "hours": hours,
            "occupancy_mode": occupancy_mode,
            "rate_per_kwh": rate_per_kwh,
            "baseline_consumption": baseline_total,
            "consumption": scenario_total,
            "baseline_cost": baseline_cost,
            "cost": scenario_cost,
            "savings": savings_inr,
            "savings_kwh": savings_kwh,
            "peak_baseline_kwh": peak_baseline,
            "peak_scenario_kwh": peak_scenario,
            "description": cls._scenario_description(scenario),
            "baseline_predictions": normalized_baseline,
            "predictions": scenario_predictions,
            "calculation_steps": calculation_steps,
            "scenario_drivers": drivers,
            "summary_cards": summary_cards,
            "comparison_table": cls._build_comparison_table(normalized_baseline, scenario_predictions, rate_per_kwh),
            "phase_breakdown": phase_breakdown,
            "monthly_projection": monthly_projection,
            "yearly_projection": yearly_projection,
            "resilience_metrics": {
                "baseline_peak_window": baseline_peak_window,
                "scenario_peak_window": scenario_peak_window,
                "baseline_peak_window_kwh": baseline_peak_window_kwh,
                "scenario_peak_window_kwh": scenario_peak_window_kwh,
                "baseline_load_factor": baseline_load_factor,
                "scenario_load_factor": scenario_load_factor,
                "self_consumption_ratio": self_consumption_ratio,
            },
            "insights": cls._build_insights(
                scenario=scenario,
                savings_inr=savings_inr,
                phase_breakdown=phase_breakdown,
                baseline_peak_window=baseline_peak_window,
                scenario_peak_window=scenario_peak_window,
            ),
            "recommendation": cls._build_recommendation(
                scenario=scenario,
                monthly_projection=monthly_projection,
                resilience_metrics={
                    "baseline_load_factor": baseline_load_factor,
                    "scenario_load_factor": scenario_load_factor,
                    "self_consumption_ratio": self_consumption_ratio,
                },
            ),
            "scenario_score": scenario_score,
        }

    @staticmethod
    def _fallback_predictions(hours: int, base_daily: float) -> list[dict]:
        per_hour = max(base_daily / max(hours, 1), 0.4)
        return [
            {
                "hour": index + 1,
                "timestamp": f"2026-01-01T{(index % 24):02d}:00:00",
                "energy_kwh": round(per_hour, 3),
            }
            for index in range(hours)
        ]

    @staticmethod
    def _extract_hour(point: dict) -> int:
        timestamp = str(point.get("timestamp", ""))
        if "T" not in timestamp:
            return 12
        return int(timestamp.split("T")[1][:2])

    @classmethod
    def _apply_occupancy_profile(cls, predictions: list[dict], occupancy_mode: str, multiplier: float) -> list[dict]:
        adjusted = []
        for point in predictions:
            hour = cls._extract_hour(point)
            energy = float(point["energy_kwh"]) * multiplier
            if occupancy_mode == "working_day":
                if 9 <= hour < 18:
                    energy *= 0.8
                elif 19 <= hour <= 23:
                    energy *= 1.08
            elif occupancy_mode == "vacation":
                if 18 <= hour <= 23:
                    energy *= 0.78
                else:
                    energy *= 0.6
            elif occupancy_mode == "guests":
                if 18 <= hour <= 23:
                    energy *= 1.15
                elif 7 <= hour < 10:
                    energy *= 1.08
            elif occupancy_mode == "students":
                if 9 <= hour < 15:
                    energy *= 0.9
                elif 20 <= hour <= 23:
                    energy *= 1.06
            adjusted.append(
                {
                    "hour": point["hour"],
                    "timestamp": point["timestamp"],
                    "energy_kwh": round(energy, 3),
                }
            )
        return adjusted

    @classmethod
    def _apply_scenario(
        cls,
        predictions: list[dict],
        *,
        scenario: str,
        optimization_strength: float,
        solar_offset: float,
        battery_shift: float,
        appliance_upgrade: float,
        demand_response: float,
    ) -> tuple[list[dict], list[dict[str, object]]]:
        if scenario == "optimized":
            return cls._apply_optimization(predictions, optimization_strength, battery_shift, appliance_upgrade)
        if scenario == "solar":
            return cls._apply_solar(predictions, solar_offset, battery_shift, appliance_upgrade)
        if scenario == "battery_backup":
            return cls._apply_battery_backup(predictions, battery_shift, demand_response)
        if scenario == "weekend_saver":
            return cls._apply_weekend_saver(predictions, optimization_strength, appliance_upgrade)
        if scenario == "green_home":
            return cls._apply_green_home(predictions, solar_offset, battery_shift, appliance_upgrade)
        if scenario == "peak_protection":
            return cls._apply_peak_protection(predictions, optimization_strength, demand_response, battery_shift)
        return (
            [
                {
                    "hour": point["hour"],
                    "timestamp": point["timestamp"],
                    "energy_kwh": round(float(point["energy_kwh"]), 3),
                }
                for point in predictions
            ],
            [
                {"label": "Optimization strength", "value": 0, "unit": "%"},
                {"label": "Solar offset", "value": 0, "unit": "%"},
                {"label": "Battery shift", "value": 0, "unit": "%"},
            ],
        )

    @classmethod
    def _apply_optimization(cls, predictions: list[dict], optimization_strength: float, battery_shift: float, appliance_upgrade: float) -> tuple[list[dict], list[dict[str, object]]]:
        reduction = optimization_strength / 100.0
        battery = battery_shift / 100.0
        upgrade = appliance_upgrade / 100.0
        adjusted = []
        for point in predictions:
            hour = cls._extract_hour(point)
            energy = float(point["energy_kwh"])
            if 18 <= hour <= 22:
                energy *= max(0.35, 1 - reduction)
            elif 10 <= hour < 18:
                energy *= max(0.55, 1 - reduction * 0.45)
            else:
                energy *= max(0.65, 1 - battery * 0.25)
            energy *= max(0.7, 1 - upgrade * 0.35)
            adjusted.append({"hour": point["hour"], "timestamp": point["timestamp"], "energy_kwh": round(energy, 3)})
        return adjusted, [
            {"label": "Peak reduction", "value": round(optimization_strength, 1), "unit": "%"},
            {"label": "Battery shift support", "value": round(battery_shift, 1), "unit": "%"},
            {"label": "Efficient appliances", "value": round(appliance_upgrade, 1), "unit": "%"},
        ]

    @classmethod
    def _apply_solar(cls, predictions: list[dict], solar_offset: float, battery_shift: float, appliance_upgrade: float) -> tuple[list[dict], list[dict[str, object]]]:
        solar = solar_offset / 100.0
        battery = battery_shift / 100.0
        upgrade = appliance_upgrade / 100.0
        adjusted = []
        for point in predictions:
            hour = cls._extract_hour(point)
            energy = float(point["energy_kwh"])
            if 8 <= hour <= 17:
                energy *= max(0.15, 1 - solar)
            elif 6 <= hour < 8 or 18 <= hour <= 20:
                energy *= max(0.3, 1 - (solar * 0.55 + battery * 0.25))
            else:
                energy *= max(0.55, 1 - battery * 0.2)
            energy *= max(0.72, 1 - upgrade * 0.28)
            adjusted.append({"hour": point["hour"], "timestamp": point["timestamp"], "energy_kwh": round(energy, 3)})
        return adjusted, [
            {"label": "Solar daytime offset", "value": round(solar_offset, 1), "unit": "%"},
            {"label": "Battery evening support", "value": round(battery_shift, 1), "unit": "%"},
            {"label": "Efficient appliances", "value": round(appliance_upgrade, 1), "unit": "%"},
        ]

    @classmethod
    def _apply_battery_backup(cls, predictions: list[dict], battery_shift: float, demand_response: float) -> tuple[list[dict], list[dict[str, object]]]:
        battery = battery_shift / 100.0
        response = demand_response / 100.0
        adjusted = []
        for point in predictions:
            hour = cls._extract_hour(point)
            energy = float(point["energy_kwh"])
            if 18 <= hour <= 22:
                energy *= max(0.35, 1 - (battery + response * 0.45))
            elif 22 <= hour or hour < 6:
                energy *= max(0.82, 1 - battery * 0.1)
            adjusted.append({"hour": point["hour"], "timestamp": point["timestamp"], "energy_kwh": round(energy, 3)})
        return adjusted, [
            {"label": "Battery peak offset", "value": round(battery_shift, 1), "unit": "%"},
            {"label": "Demand response support", "value": round(demand_response, 1), "unit": "%"},
            {"label": "Grid peak relief", "value": round((battery_shift * 0.7) + (demand_response * 0.3), 1), "unit": "%"},
        ]

    @classmethod
    def _apply_weekend_saver(cls, predictions: list[dict], optimization_strength: float, appliance_upgrade: float) -> tuple[list[dict], list[dict[str, object]]]:
        reduction = optimization_strength / 100.0
        upgrade = appliance_upgrade / 100.0
        adjusted = []
        for point in predictions:
            hour = cls._extract_hour(point)
            energy = float(point["energy_kwh"])
            if 10 <= hour <= 18:
                energy *= max(0.45, 1 - reduction * 0.85)
            else:
                energy *= max(0.7, 1 - reduction * 0.25)
            energy *= max(0.74, 1 - upgrade * 0.25)
            adjusted.append({"hour": point["hour"], "timestamp": point["timestamp"], "energy_kwh": round(energy, 3)})
        return adjusted, [
            {"label": "Weekend daytime reduction", "value": round(optimization_strength * 0.85, 1), "unit": "%"},
            {"label": "Efficient appliances", "value": round(appliance_upgrade, 1), "unit": "%"},
            {"label": "BESCOM unit savings focus", "value": round(optimization_strength, 1), "unit": "%"},
        ]

    @classmethod
    def _apply_green_home(cls, predictions: list[dict], solar_offset: float, battery_shift: float, appliance_upgrade: float) -> tuple[list[dict], list[dict[str, object]]]:
        solar = solar_offset / 100.0
        battery = battery_shift / 100.0
        upgrade = appliance_upgrade / 100.0
        adjusted = []
        for point in predictions:
            hour = cls._extract_hour(point)
            energy = float(point["energy_kwh"])
            if 7 <= hour <= 17:
                energy *= max(0.12, 1 - (solar * 0.8 + upgrade * 0.25))
            elif 18 <= hour <= 22:
                energy *= max(0.28, 1 - (battery * 0.6 + upgrade * 0.3))
            else:
                energy *= max(0.68, 1 - upgrade * 0.22)
            adjusted.append({"hour": point["hour"], "timestamp": point["timestamp"], "energy_kwh": round(energy, 3)})
        return adjusted, [
            {"label": "Green supply offset", "value": round(solar_offset, 1), "unit": "%"},
            {"label": "Battery support", "value": round(battery_shift, 1), "unit": "%"},
            {"label": "Appliance upgrade", "value": round(appliance_upgrade, 1), "unit": "%"},
        ]

    @classmethod
    def _apply_peak_protection(cls, predictions: list[dict], optimization_strength: float, demand_response: float, battery_shift: float) -> tuple[list[dict], list[dict[str, object]]]:
        reduction = optimization_strength / 100.0
        response = demand_response / 100.0
        battery = battery_shift / 100.0
        adjusted = []
        for point in predictions:
            hour = cls._extract_hour(point)
            energy = float(point["energy_kwh"])
            if 17 <= hour <= 22:
                energy *= max(0.25, 1 - (reduction * 0.65 + response * 0.45 + battery * 0.25))
            elif 12 <= hour < 17:
                energy *= max(0.55, 1 - reduction * 0.25)
            adjusted.append({"hour": point["hour"], "timestamp": point["timestamp"], "energy_kwh": round(energy, 3)})
        return adjusted, [
            {"label": "Peak demand control", "value": round(optimization_strength, 1), "unit": "%"},
            {"label": "Demand response", "value": round(demand_response, 1), "unit": "%"},
            {"label": "Battery buffer", "value": round(battery_shift, 1), "unit": "%"},
        ]

    @staticmethod
    def _scenario_description(scenario: str) -> str:
        descriptions = {
            "normal": "Baseline planning mode with no extra savings driver applied.",
            "optimized": "Demand-shifting mode that trims peak-hour usage and smooths daily load.",
            "solar": "Solar-assisted mode that offsets daytime energy and reduces evening pressure with battery-style support.",
            "battery_backup": "Battery-support mode that cuts evening grid load and protects peak-hour demand.",
            "weekend_saver": "Weekend saver mode that aggressively reduces high daytime consumption blocks.",
            "green_home": "Balanced clean-energy mode that combines solar-style offset, battery support, and efficient appliance behavior.",
            "peak_protection": "Peak protection mode focused on reducing the evening stress window with demand response and battery help.",
        }
        return descriptions.get(scenario, descriptions["normal"])

    @classmethod
    def _build_comparison_table(cls, baseline: list[dict], scenario: list[dict], rate_per_kwh: float) -> list[dict[str, object]]:
        rows = []
        for base_point, scenario_point in zip(baseline[:24], scenario[:24]):
            base_energy = round(float(base_point["energy_kwh"]), 3)
            scenario_energy = round(float(scenario_point["energy_kwh"]), 3)
            rows.append(
                {
                    "time": base_point["timestamp"],
                    "baseline_kwh": base_energy,
                    "scenario_kwh": scenario_energy,
                    "saved_kwh": round(base_energy - scenario_energy, 3),
                    "saved_inr": round((base_energy - scenario_energy) * rate_per_kwh, 2),
                }
            )
        return rows

    @classmethod
    def _phase_breakdown(cls, baseline: list[dict], scenario: list[dict], rate_per_kwh: float) -> list[dict[str, object]]:
        buckets = {
            "Early Morning": lambda h: 5 <= h < 8,
            "Morning": lambda h: 8 <= h < 12,
            "Afternoon": lambda h: 12 <= h < 17,
            "Evening Peak": lambda h: 17 <= h < 22,
            "Late Night": lambda h: h >= 22 or h < 5,
        }
        rows = []
        for label, matcher in buckets.items():
            baseline_total = 0.0
            scenario_total = 0.0
            for base_point, scenario_point in zip(baseline, scenario):
                hour = cls._extract_hour(base_point)
                if matcher(hour):
                    baseline_total += float(base_point["energy_kwh"])
                    scenario_total += float(scenario_point["energy_kwh"])
            rows.append(
                {
                    "phase": label,
                    "baseline_kwh": round(baseline_total, 3),
                    "scenario_kwh": round(scenario_total, 3),
                    "saved_kwh": round(baseline_total - scenario_total, 3),
                    "saved_inr": round((baseline_total - scenario_total) * rate_per_kwh, 2),
                }
            )
        return rows

    @staticmethod
    def _projection(scenario_cost: float, savings_inr: float, rate_per_kwh: float, period: str) -> dict[str, float]:
        multiplier = 30 if period == "month" else 365
        fixed_charge = 120.0 if period == "month" else 1440.0
        baseline_period_cost = round((scenario_cost + savings_inr) * multiplier, 2)
        scenario_period_cost = round(scenario_cost * multiplier, 2)
        total_bill = round(scenario_period_cost + fixed_charge, 2)
        return {
            "baseline_cost_inr": baseline_period_cost,
            "scenario_cost_inr": scenario_period_cost,
            "fixed_charge_inr": fixed_charge,
            "total_bill_inr": total_bill,
            "savings_inr": round(savings_inr * multiplier, 2),
            "effective_rate_inr": rate_per_kwh,
        }

    @classmethod
    def _peak_window(cls, points: list[dict]) -> tuple[str, float]:
        if not points:
            return "N/A", 0.0
        peak = max(points, key=lambda point: float(point["energy_kwh"]))
        hour = cls._extract_hour(peak)
        return f"{hour:02d}:00 - {(hour + 1) % 24:02d}:00", round(float(peak["energy_kwh"]), 3)

    @staticmethod
    def _load_factor(points: list[dict]) -> float:
        if not points:
            return 0.0
        total = sum(float(point["energy_kwh"]) for point in points)
        average = total / len(points)
        peak = max(float(point["energy_kwh"]) for point in points) or 1.0
        return round(average / peak, 3)

    @staticmethod
    def _self_consumption_ratio(scenario: str, solar_offset: float, battery_shift: float) -> float:
        if scenario not in {"solar", "green_home"}:
            return 0.0
        ratio = min(95.0, (solar_offset * 0.75) + (battery_shift * 0.35))
        return round(ratio, 1)

    @staticmethod
    def _scenario_score(*, savings_inr: float, peak_reduction: float, load_factor_gain: float) -> int:
        score = 55 + min(20, int(savings_inr / 8)) + min(15, int(peak_reduction * 10)) + min(10, int(load_factor_gain * 100))
        return max(0, min(100, score))

    @classmethod
    def _build_insights(
        cls,
        *,
        scenario: str,
        savings_inr: float,
        phase_breakdown: list[dict[str, object]],
        baseline_peak_window: str,
        scenario_peak_window: str,
    ) -> list[str]:
        best_phase = max(phase_breakdown, key=lambda row: float(row["saved_inr"])) if phase_breakdown else None
        insights = [
            f"This {scenario.replace('_', ' ')} plan shifts the main stress window from {baseline_peak_window} toward {scenario_peak_window}.",
            f"Projected direct savings for the selected horizon are Rs. {savings_inr:,.2f}.",
        ]
        if best_phase:
            insights.append(
                f"The strongest savings happen during {best_phase['phase']} with about Rs. {float(best_phase['saved_inr']):,.2f} saved."
            )
        return insights

    @classmethod
    def _build_recommendation(cls, *, scenario: str, monthly_projection: dict[str, float], resilience_metrics: dict[str, float]) -> dict[str, object]:
        load_factor_gain = round(
            float(resilience_metrics["scenario_load_factor"]) - float(resilience_metrics["baseline_load_factor"]),
            3,
        )
        return {
            "headline": f"{scenario.replace('_', ' ').title()} is suitable if you want better savings without losing visibility into peak-hour behavior.",
            "monthly_savings_inr": monthly_projection["savings_inr"],
            "load_factor_gain": load_factor_gain,
            "self_consumption_ratio": resilience_metrics["self_consumption_ratio"],
        }
