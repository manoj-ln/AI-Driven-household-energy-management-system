from app.services.dataset_service import DatasetService


class OptimizationService:
    @classmethod
    def get_report(cls) -> dict[str, object]:
        summary = DatasetService.get_summary()
        recent = DatasetService.get_recent_data(24)
        device_breakdown = DatasetService.get_device_breakdown()

        daily = float(summary.get("daily_consumption", 0.0))
        peak_window = summary.get("peak_hour", "N/A")
        base_energy_rate = 5.90
        surcharge_rate = 0.36
        bescom_energy_rate = round(base_energy_rate + surcharge_rate, 2)
        fixed_charge_per_kw = 120.0
        assumed_connected_load_kw = max(1.0, round(max(daily / 24.0, 0.8), 2))

        peak_hours = [row for row in recent if 18 <= int(row["hour"]) <= 22]
        offpeak_hours = [row for row in recent if int(row["hour"]) < 7 or int(row["hour"]) >= 22]
        shoulder_hours = [row for row in recent if row not in peak_hours and row not in offpeak_hours]
        peak_energy = round(sum(float(row["total_consumption"]) for row in peak_hours), 3)
        offpeak_energy = round(sum(float(row["total_consumption"]) for row in offpeak_hours), 3)
        shoulder_energy = round(sum(float(row["total_consumption"]) for row in shoulder_hours), 3)
        peak_cost = round(peak_energy * bescom_energy_rate, 2)
        offpeak_cost = round(offpeak_energy * bescom_energy_rate, 2)
        shoulder_cost = round(shoulder_energy * bescom_energy_rate, 2)

        shiftable_energy = round(peak_energy * 0.22, 3)
        shift_savings = round(shiftable_energy * bescom_energy_rate, 2)
        appliance_savings = []
        for device in device_breakdown[:5]:
            usage = float(device["average_usage"]) * 24
            appliance_savings.append(
                {
                    "device": device["name"],
                    "current_daily_kwh": round(usage, 3),
                    "optimized_daily_kwh": round(usage * 0.88, 3),
                    "daily_savings_inr": round((usage * 0.12) * bescom_energy_rate, 2),
                    "recommended_action": "Reduce runtime during peak hours" if usage >= 3 else "Shift usage to off-peak windows",
                }
            )

        optimized_daily = round(max(daily - shiftable_energy, 0.0), 3)
        optimized_cost = round(max((daily * bescom_energy_rate) - shift_savings, 0.0), 2)
        baseline_cost = round(daily * bescom_energy_rate, 2)
        optimized_peak_energy = round(max(peak_energy - shiftable_energy, 0.0), 3)
        monthly_energy_charge = round(baseline_cost * 30, 2)
        monthly_fixed_charge = round(assumed_connected_load_kw * fixed_charge_per_kw, 2)
        monthly_surcharge = round(daily * surcharge_rate * 30, 2)
        monthly_bill_total = round(monthly_energy_charge + monthly_fixed_charge, 2)
        optimized_monthly_energy = round(optimized_cost * 30, 2)
        optimized_monthly_bill_total = round(optimized_monthly_energy + monthly_fixed_charge, 2)
        annual_baseline_bill = round(monthly_bill_total * 12, 2)
        annual_optimized_bill = round(optimized_monthly_bill_total * 12, 2)
        annual_savings = round(annual_baseline_bill - annual_optimized_bill, 2)

        savings_levers = [
            {
                "label": "Shift evening peak usage",
                "daily_savings_inr": shift_savings,
                "explanation": "Move flexible loads away from 6 PM to 10 PM to reduce peak-hour unit spend.",
            },
            {
                "label": "Trim top device runtime",
                "daily_savings_inr": round(sum(item["daily_savings_inr"] for item in appliance_savings[:2]), 2),
                "explanation": "The top two contributors usually create the fastest savings when their runtime is reduced by 10-15%.",
            },
            {
                "label": "Flatten the load profile",
                "daily_savings_inr": round(max((daily * 0.05) * bescom_energy_rate, 0.0), 2),
                "explanation": "Spreading demand across the day improves efficiency and avoids repeated heavy-load overlaps.",
            },
        ]

        scenario_comparison = [
            {
                "scenario": "Current usage",
                "daily_cost_inr": baseline_cost,
                "monthly_bill_inr": monthly_bill_total,
                "peak_energy_kwh": peak_energy,
            },
            {
                "scenario": "Peak load shifting",
                "daily_cost_inr": round(max(baseline_cost - shift_savings, 0.0), 2),
                "monthly_bill_inr": round(max((baseline_cost - shift_savings) * 30, 0.0) + monthly_fixed_charge, 2),
                "peak_energy_kwh": optimized_peak_energy,
            },
            {
                "scenario": "Full optimized plan",
                "daily_cost_inr": optimized_cost,
                "monthly_bill_inr": optimized_monthly_bill_total,
                "peak_energy_kwh": optimized_peak_energy,
            },
        ]

        hourly_strategy = [
            {"window": "Early morning", "hours": "05:00-07:00", "strategy": "Best for water heating and appliance preparation"},
            {"window": "Daytime", "hours": "10:00-16:00", "strategy": "Good for washing and cooking loads when occupancy allows"},
            {"window": "Evening peak", "hours": "18:00-22:00", "strategy": "Keep only essential devices active"},
            {"window": "Late night", "hours": "22:00-06:00", "strategy": "Use for charging, delayed washing, and other flexible loads"},
        ]

        return {
            "peak_hour": peak_window,
            "daily_consumption": round(daily, 3),
            "estimated_savings": round(shift_savings + sum(item["daily_savings_inr"] for item in appliance_savings[:3]), 2),
            "baseline_cost": baseline_cost,
            "optimized_cost": optimized_cost,
            "optimized_daily_consumption": optimized_daily,
            "tariff": {
                "peak_rate_inr": bescom_energy_rate,
                "offpeak_rate_inr": bescom_energy_rate,
                "peak_energy_kwh": peak_energy,
                "offpeak_energy_kwh": offpeak_energy,
                "shoulder_energy_kwh": shoulder_energy,
                "peak_cost_inr": peak_cost,
                "offpeak_cost_inr": offpeak_cost,
                "shoulder_cost_inr": shoulder_cost,
                "fixed_charge_per_kw_inr": fixed_charge_per_kw,
                "energy_rate_inr": bescom_energy_rate,
                "base_energy_rate_inr": base_energy_rate,
                "surcharge_rate_inr": surcharge_rate,
                "assumed_connected_load_kw": assumed_connected_load_kw,
            },
            "recommendations": [
                "Move washing, water heating, and charging loads away from the heavy evening window.",
                "Reduce simultaneous use of the top 2 devices to lower BESCOM unit charges.",
                "Use shorter runtime on high-load appliances first, because that gives the biggest rupee savings.",
                "Use device schedules to flatten spikes and improve the energy efficiency score.",
            ],
            "action_plan": [
                {"step": "Schedule flexible appliances after 10 PM or before 7 AM."},
                {"step": "Trim the top device contributors by 10-15% where possible."},
                {"step": "Use the monthly projection to track both fixed charge and energy charge together."},
            ],
            "opportunities": appliance_savings,
            "cost_breakdown": [
                {"label": "Current daily energy cost", "value": baseline_cost},
                {"label": "Shiftable load savings", "value": shift_savings},
                {"label": "Projected optimized energy cost", "value": optimized_cost},
            ],
            "monthly_projection": {
                "energy_charge_inr": monthly_energy_charge,
                "fixed_charge_inr": monthly_fixed_charge,
                "surcharge_inr": monthly_surcharge,
                "bill_total_inr": monthly_bill_total,
                "optimized_bill_total_inr": optimized_monthly_bill_total,
            },
            "annual_projection": {
                "baseline_bill_inr": annual_baseline_bill,
                "optimized_bill_inr": annual_optimized_bill,
                "savings_inr": annual_savings,
            },
            "savings_levers": savings_levers,
            "scenario_comparison": scenario_comparison,
            "hourly_strategy": hourly_strategy,
            "cost_verification_log": [
                "BESCOM residential base energy charge applied at Rs. 5.90 per unit.",
                "BESCOM surcharge applied at Rs. 0.36 per unit, giving an effective energy rate of Rs. 6.26.",
                "Reference fixed charge stored at Rs. 120 per kW for monthly bill calculations.",
                "This page uses the BESCOM energy rate for daily and monthly optimization comparisons.",
            ],
        }
