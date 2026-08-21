"""
BESCOM Bill Calculator service.

Implements the FY2026-27 LT-1 Domestic (residential) tariff structure for
Karnataka (BESCOM) with support for:

- Energy charge (flat rate, no slabs)
- Fixed charge (per kW of sanctioned load)
- Pension & Gratuity surcharge (per unit)
- Electricity tax (ad valorem on energy + fixed)
- FPPCA (Fuel & Power Purchase Cost Adjustment, per unit, monthly)
- FY25 True-up charges (fixed monthly instalment)
- Gruha Jyothi free units (subsidy scheme)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.config import settings


@dataclass
class BillCalculationInput:
    state: str = "Karnataka (BESCOM)"
    connection_type: str = "residential"
    sanctioned_load_kw: float = 2.0
    units_consumed_kwh: float = 0.0
    billing_period: str = "monthly"  # monthly | bi-monthly
    fppca_paise: float | None = None  # paise per unit
    fy25_trueup_per_month: float | None = None  # INR per month
    gruha_jyothi_units: float | None = None  # free units entitlement
    gruha_jyothi_enrolled: bool = False


@dataclass
class BillBreakdown:
    energy_charge_inr: float
    fixed_charge_inr: float
    pnG_surcharge_inr: float
    electricity_tax_inr: float
    fppca_inr: float
    trueup_inr: float
    gruha_jyothi_discount_inr: float
    grand_total_inr: float


# --- State / utility tables --------------------------------------------------

KARNATAKA_TARIFF = {
    "residential": {
        "name": "LT-1 Domestic",
        "energy_rate_inr": 5.80,
        "fixed_charge_per_kw_monthly": 150.00,
        "png_surcharge_per_unit": 0.35,
        "electricity_tax_rate": 0.09,
        "tax_exempt": False,
    },
    "commercial": {
        "name": "LT-2/HT-1",
        "energy_rate_inr": 7.45,
        "fixed_charge_per_kw_monthly": 210.00,
        "png_surcharge_per_unit": 0.35,
        "electricity_tax_rate": 0.09,
        "tax_exempt": False,
    },
    "industrial": {
        "name": "HT-2",
        "energy_rate_inr": 6.80,
        "fixed_charge_per_kw_monthly": 330.00,
        "png_surcharge_per_unit": 0.35,
        "electricity_tax_rate": 0.09,
        "tax_exempt": False,
    },
    "agriculture": {
        "name": "LT-Agri",
        "energy_rate_inr": 3.20,
        "fixed_charge_per_kw_monthly": 40.00,
        "png_surcharge_per_unit": 0.00,
        "electricity_tax_rate": 0.00,
        "tax_exempt": True,
    },
}

STATE_TARIFF_MAP = {
    "Karnataka (BESCOM)": {
        **KARNATAKA_TARIFF,
        "escoom_name": "BESCOM",
        "full_name": "Bangalore Electricity Supply Company Limited",
        "districts": ["Bengaluru Urban", "Bengaluru Rural", "Ramanagara", "Kolar", "Chikkaballapur", "Tumakuru", "Davanagere", "Chitradurga"],
        "district_count": 8,
        "licence_area_km2": 41092,
        "population_covered": "207 L+",
        "year_incorporated": 2002,
        "supply_description": "Bengaluru Urban, Bengaluru Rural, Ramanagara, Kolar, Chikkaballapur, Tumakuru, Davanagere and Chitradurga",
        "about": "BESCOM supplies power to southern and central Karnataka including Bengaluru. Its licence area covers 41,092 sq km and over 207 lakh people.",
        "contact": {
            "helpline": "1912",
            "whatsapp": "94498 44640",
            "emergency_whatsapp": ["94498 43357", "94831 91222"],
            "sms_complaint": "58888 (format: BESCOM <account no>)",
            "email": "helpline@bescom.co.in",
            "website": "bescom.karnataka.gov.in",
            "mobile_app": "BESCOM Mithra (Android & iOS)",
        },
        "region_note": "southern and central",
    },
    "Karnataka (HESCOM)": {
        **KARNATAKA_TARIFF,
        "escoom_name": "HESCOM",
        "full_name": "Hubli Electricity Supply Company Limited",
        "districts": ["Belagavi", "Dharwad", "Haveri", "Gadag", "Uttara Kannada", "Bagalkot", "Vijayapura"],
        "district_count": 7,
        "licence_area_km2": 54000,
        "population_covered": "250 L+",
        "year_incorporated": 2002,
        "supply_description": "northern Karnataka, including the twin cities of Hubballi-Dharwad, Belagavi, and Uttara Kannada",
        "about": "HESCOM supplies power to northern Karnataka including Hubballi-Dharwad, Belagavi, and Uttara Kannada. Its licence area covers approximately 54,000 sq km and over 250 lakh people.",
        "contact": {
            "helpline": "1912",
            "whatsapp": "94498 43356",
            "emergency_whatsapp": ["94498 43357", "94831 91323"],
            "sms_complaint": "58888 (format: HESCOM <account no>)",
            "email": "customercare@hescom.co.in",
            "website": "hescom.karnataka.gov.in",
            "mobile_app": "HESCOM Mithra (Android & iOS)",
        },
        "region_note": "northern",
    },
    "Karnataka (MESCOM)": {
        **KARNATAKA_TARIFF,
        "escoom_name": "MESCOM",
        "full_name": "Mangalore Electricity Supply Company Limited",
        "districts": ["Dakshina Kannada", "Udupi", "Shivamogga", "Chikkamagaluru", "Kodagu", "Hassan"],
        "district_count": 6,
        "licence_area_km2": 33000,
        "population_covered": "160 L+",
        "year_incorporated": 2002,
        "supply_description": "Mangaluru, Udupi, Shivamogga, Chikkamagaluru, Kodagu, Hassan and surrounding areas of coastal and Malnad Karnataka",
        "about": "MESCOM supplies power to coastal and Malnad Karnataka including Mangaluru, Udupi, Shivamogga, and Chikkamagaluru. Its licence area covers approximately 33,000 sq km and over 160 lakh people.",
        "contact": {
            "helpline": "1912",
            "whatsapp": "94498 44740",
            "emergency_whatsapp": ["94498 44741", "94831 91313"],
            "sms_complaint": "58888 (format: MESCOM <account no>)",
            "email": "customercare@mescom.co.in",
            "website": "mescom.karnataka.gov.in",
            "mobile_app": "MESCOM Mithra (Android & iOS)",
        },
        "region_note": "coastal and Malnad",
    },
    "Karnataka (CESCOM)": {
        **KARNATAKA_TARIFF,
        "escoom_name": "CESCOM",
        "full_name": "Chamundeshwari Electricity Supply Corporation Limited",
        "districts": ["Mysuru", "Mandya", "Chamarajanagar"],
        "district_count": 3,
        "licence_area_km2": 29000,
        "population_covered": "130 L+",
        "year_incorporated": 2002,
        "supply_description": "Mysuru, Mandya and Chamarajanagar districts of Karnataka",
        "about": "CESCOM (Chamundeshwari Electricity Supply Corporation Limited) supplies power to Mysuru, Mandya and Chamarajanagar in southern Karnataka. It was incorporated on 1 June 2002, following the unbundling of KPTCL into four distribution companies.",
        "contact": {
            "helpline": "1912",
            "whatsapp": "94498 44540",
            "emergency_whatsapp": ["94831 91414", "94831 91424"],
            "sms_complaint": "58888 (Format: CESC <Account No.>)",
            "email": "customercare@cescmysore.org",
            "website": "cescmysore.karnataka.gov.in",
            "mobile_app": "CESC Mithra (Android & iOS)",
        },
        "region_note": "southern",
    },
}

BILLING_PERIOD_MONTHS = {
    "monthly": 1,
    "bi-monthly": 2,
}

# FPPCA reference values (paise/unit) for recent BESCOM months
# Source: KERC orders; varies every month
FPPCA_REFERENCE = {
    "December 2025": 31,
    "January 2026": 39,
    "February 2026": 24,
    "March 2026": 44,
    "April 2026": 47,
    "May 2026": 25,
}


class BillCalculator:
    """Calculate BESCOM-style electricity bills for Karnataka consumers."""

    @staticmethod
    def _months(billing_period: str) -> int:
        b = billing_period.lower() if billing_period else "monthly"
        return BILLING_PERIOD_MONTHS.get(b, 1)

    @staticmethod
    def _tariff_for(state: str, connection_type: str) -> dict[str, Any]:
        state_data = STATE_TARIFF_MAP.get(state, STATE_TARIFF_MAP["Karnataka (BESCOM)"])
        # Separate tariff connection types from state metadata
        tariff_connections = {k: v for k, v in state_data.items() if isinstance(v, dict) and "energy_rate_inr" in v}
        return tariff_connections.get(connection_type, tariff_connections["residential"])

    @staticmethod
    def _state_meta(state: str) -> dict[str, Any]:
        """Return state-level metadata (districts, contact info, etc.)."""
        return {k: v for k, v in STATE_TARIFF_MAP.get(state, STATE_TARIFF_MAP["Karnataka (BESCOM)"]).items() if k in (
            "escoom_name", "full_name", "districts", "district_count", "licence_area_km2",
            "population_covered", "year_incorporated", "supply_description", "about",
            "contact", "region_note"
        )}

    @classmethod
    def calculate(cls, data: BillCalculationInput, _skip_forecast: bool = False) -> dict[str, Any]:
        months = cls._months(data.billing_period)
        tariff = cls._tariff_for(data.state, data.connection_type)

        units = data.units_consumed_kwh
        sanctioned_load = data.sanctioned_load_kw

        # --- Gruha Jyothi subsidy ---
        # The scheme is all-or-nothing: if usage is within the free-unit entitlement,
        # energy/fixed/tax are fully subsidised; if even one unit over, the entire
        # bill becomes payable (no partial subsidy).
        gj_units = data.gruha_jyothi_units or 0.0
        gruha_jyothi_subsidy_beneficial = data.gruha_jyothi_enrolled and gj_units > 0 and units <= gj_units
        if gruha_jyothi_subsidy_beneficial:
            energy_charge = 0.0
            fixed_charge = 0.0
            pnG_surcharge = 0.0
            electricity_tax = 0.0
            fppca_inr = 0.0
            trueup_inr = 0.0
            gruha_jyothi_discount = round((units * tariff["energy_rate_inr"]
                                           + sanctioned_load * tariff["fixed_charge_per_kw_monthly"] * months), 2)
        else:
            gruha_jyothi_discount = 0.0
            energy_charge = round(units * tariff["energy_rate_inr"], 2)
            fixed_charge = round(sanctioned_load * tariff["fixed_charge_per_kw_monthly"] * months, 2)
            pnG_surcharge = round(units * tariff["png_surcharge_per_unit"], 2)
            taxable_amount = energy_charge + fixed_charge
            electricity_tax = round(taxable_amount * tariff["electricity_tax_rate"], 2)

        # --- FPPCA (per unit, in paise) ---
        if not gruha_jyothi_subsidy_beneficial and data.fppca_paise is not None and data.fppca_paise > 0:
            fppca_inr = round(units * (data.fppca_paise / 100.0), 2)
        else:
            fppca_inr = 0.0

        # --- FY25 True-up charges (fixed monthly) ---
        if not gruha_jyothi_subsidy_beneficial and data.fy25_trueup_per_month is not None and data.fy25_trueup_per_month > 0:
            trueup_inr = round(data.fy25_trueup_per_month * months, 2)
        elif gruha_jyothi_subsidy_beneficial:
            trueup_inr = 0.0
        else:
            trueup_inr = 0.0

        # --- Grand total ---
        grand_total = round(
            energy_charge + fixed_charge + pnG_surcharge + electricity_tax + fppca_inr + trueup_inr, 2
        )

        # --- Build result ---
        slab_rate = tariff["energy_rate_inr"]
        avg_rate = round(grand_total / units, 2) if units > 0 else 0.0

        breakdown = BillBreakdown(
            energy_charge_inr=energy_charge,
            fixed_charge_inr=fixed_charge,
            pnG_surcharge_inr=pnG_surcharge,
            electricity_tax_inr=electricity_tax,
            fppca_inr=fppca_inr,
            trueup_inr=trueup_inr,
            gruha_jyothi_discount_inr=gruha_jyothi_discount,
            grand_total_inr=grand_total,
        )

        # --- Gruha Jyothi message ---
        gj_message = None
        if data.gruha_jyothi_enrolled and gj_units and gj_units > 0:
            if units <= gj_units:
                gj_message = (
                    f"Gruha Jyothi applies: your usage of {units} units is within your entitlement of {gj_units} units "
                    f"(your FY2022-23 average + 10%, capped at 200). Energy, fixed, tax, FPPCA and true-up components "
                    f"are fully subsidised."
                )
            else:
                gj_message = (
                    f"Gruha Jyothi does NOT apply: your usage of {units} units exceeds your entitlement of {gj_units} units "
                    f"(your FY2022-23 average + 10%, capped at 200). Under the scheme, going even one unit over means "
                    f"the entire bill becomes payable — the subsidy is not partial (it is a cliff, not a marginal reduction). "
                    f"Reducing usage to {gj_units} units or below would restore it. "
                    f"Cost of the one extra unit: approximately ₹{round(grand_total - 0, 2)}."
                )

        # --- 6-month forecast (seasonal pattern estimate) ---
        if not _skip_forecast:
            monthly_seasonal_factors = [0.95, 0.92, 1.0, 1.15, 1.30, 1.22]
            forecast = []
            month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
            for label, factor in zip(month_labels, monthly_seasonal_factors):
                seasonal_units = round(units * factor, 2)
                seasonal_input = BillCalculationInput(
                    state=data.state,
                    connection_type=data.connection_type,
                    sanctioned_load_kw=sanctioned_load,
                    units_consumed_kwh=seasonal_units,
                    billing_period="monthly",
                    fppca_paise=data.fppca_paise,
                    fy25_trueup_per_month=data.fy25_trueup_per_month,
                    gruha_jyothi_units=data.gruha_jyothi_units,
                    gruha_jyothi_enrolled=data.gruha_jyothi_enrolled,
                )
                seasonal_result = cls.calculate(seasonal_input, _skip_forecast=True)
                forecast.append({
                    "month": label,
                    "units_kwh": seasonal_units,
                    "total_inr": seasonal_result["total_amount_payable"],
                })

            annual_estimate = round(sum(item["total_inr"] for item in forecast), 2)
            peak_month = "Apr–Jun" if any(d["month"] in ("Apr", "May", "Jun") and d["total_inr"] >= max(item["total_inr"] for item in forecast) for d in forecast) else "Apr–Jun"
            potential_savings = round(max(item["total_inr"] for item in forecast) - min(item["total_inr"] for item in forecast), 2)
        else:
            forecast = None
            annual_estimate = None
            peak_month = None
            potential_savings = None

        # --- Smart insights ---
        escoom_name = cls._state_meta(data.state).get("escoom_name", "BESCOM")
        smart_insights = []
        if units > 500:
            smart_insights.append("LED Tip: Replace 10 conventional bulbs with LEDs to save 20–30 kWh/month.")
        if units > 800:
            smart_insights.append("AC Tip: Set AC to 24°C instead of 18°C — saves up to 24% AC energy.")
        smart_insights.append("Solar: A 3kW solar system can offset most usage. PM Surya Ghar Yojana offers ₹78,000 subsidy.")
        if sanctioned_load > 5:
            smart_insights.append(
                f"Your sanctioned load of {sanctioned_load} kW is high. Consider applying to {escoom_name} "
                f"to reduce it — saves ₹{sanctioned_load * 150}/month in fixed charges."
            )

        # --- Tariff reference ---
        tariff_reference = {
            "tariff_name": tariff["name"],
            "financial_year": "FY2026-27",
            "effective_date": "1 April 2026",
            "rates_verified": "Jul 2026",
            "rate_verification_notes": (
                "KERC Order 27.03.2025 LT-1 FY2026-27; "
                "P&G 35p/unit per KERC order 18.03.2025 para (h), as amended 27.03.2025; "
                "e-tax 9% GoK Notif.24 19.07.2018; "
                "FY25 true-up per KERC APR order 17.04.2026; "
                "FPPCA monthly per KERC order 29.06.2026"
            ),
            "energy_charge": f"₹{tariff['energy_rate_inr']}/unit",
            "fixed_charge": f"₹{tariff['fixed_charge_per_kw_monthly']}/kW/month",
            "png_surcharge": f"₹{tariff['png_surcharge_per_unit']}/unit",
            "electricity_tax": f"{int(tariff['electricity_tax_rate']*100)}% of energy + fixed",
            "fppca_note": "24–47 paise/unit (varies monthly)",
            "fy25_trueup_note": "₹/month based on FY2024-25 consumption",
            "example_250_units_2kw": "₹1,995",
        }

        return {
            "state": data.state,
            "connection_type": data.connection_type,
            "tariff_name": tariff["name"],
            "financial_year": "FY2026-27",
            "sanctioned_load_kw": sanctioned_load,
            "units_consumed_kwh": units,
            "billing_period": data.billing_period,
            "months": months,
            "slab_info": {
                "label": f"0–{units} units",
                "rate_inr_per_unit": tariff["energy_rate_inr"],
                "units": units,
                "energy_charge_inr": energy_charge,
            },
            "total_amount_payable": grand_total,
            "average_rate_inr_per_kwh": avg_rate,
            "bill_breakdown": {
                "energy_charges_inr": energy_charge,
                "fixed_charges_inr": fixed_charge,
                "pension_and_gratuity_surcharge_inr": pnG_surcharge,
                "electricity_tax_inr": electricity_tax,
                "fppca_inr": fppca_inr,
                "fy25_trueup_charges_inr": trueup_inr,
            },
            "gruha_jyothi": {
                "enrolled": data.gruha_jyothi_enrolled,
                "entitlement_units": gj_units,
                "applies_this_month": gruha_jyothi_subsidy_beneficial,
                "discount_inr": gruha_jyothi_discount,
                "message": gj_message,
            },
            "smart_insights": smart_insights,
            "six_month_forecast": forecast,
            "annual_estimate_inr": annual_estimate,
            "peak_month": peak_month,
            "potential_savings_inr": potential_savings,
            "tariff_reference": tariff_reference,
            "gruha_jyothi_cliff_note": (
                "Gruha Jyothi is a per-household entitlement = FY2022-23 average consumption + 10%, capped at 200 units. "
                "It is NOT a flat 200 units for everyone. The subsidy is all-or-nothing: one unit over means the "
                "entire bill becomes payable (no partial subsidy)."
            ),
            "documented_gap": (
                "The 9% electricity tax is applied in this calculator to energy + fixed charges only. Whether the state "
                "also levies it on the P&G surcharge, FPPCA and true-up lines has not been confirmed against a primary source. "
                "If it does, a 250-unit bill would be approximately ₹7.88 higher. This will be updated when confirmed against an official bill."
            ),
            "verification_log": [
                f"{escoom_name} base energy rate: Rs. {tariff['energy_rate_inr']} per unit (flat rate, no slabs).",
                f"Fixed charge: Rs. {tariff['fixed_charge_per_kw_monthly']} per kW/month × {sanctioned_load} kW × {months} month(s).",
                f"P&G surcharge: Rs. {tariff['png_surcharge_per_unit']} per unit.",
                f"Electricity tax: {int(tariff['electricity_tax_rate']*100)}% of (energy charge + fixed charge).",
                f"FPPCA applied at {data.fppca_paise}p/unit when provided (varies monthly per KERC).",
                f"FY25 True-up: Rs. {data.fy25_trueup_per_month}/month × {months} month(s)."
                if data.fy25_trueup_per_month
                else f"FY25 True-up: not provided (0 × {months} month(s)).",
            ],
            "state_info": cls._state_meta(data.state),
        }

    @classmethod
    def calculate_from_dict(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Convenience method: accept a plain dict (e.g. from a FastAPI request body)."""
        input_data = BillCalculationInput(
            state=data.get("state", "Karnataka (BESCOM)"),
            connection_type=data.get("connection_type", "residential"),
            sanctioned_load_kw=float(data.get("sanctioned_load_kw", 2.0)),
            units_consumed_kwh=float(data.get("units_consumed_kwh", 0.0)),
            billing_period=data.get("billing_period", "monthly"),
            fppca_paise=(float(data["fppca_paise"]) if data.get("fppca_paise") is not None else None),
            fy25_trueup_per_month=(float(data["fy25_trueup_per_month"]) if data.get("fy25_trueup_per_month") is not None else None),
            gruha_jyothi_units=(float(data["gruha_jyothi_units"]) if data.get("gruha_jyothi_units") is not None else None),
            gruha_jyothi_enrolled=bool(data.get("gruha_jyothi_enrolled", False)),
        )
        return cls.calculate(input_data)

    @classmethod
    def get_tariff_references(cls) -> dict[str, Any]:
        """Return the full tariff reference table for all states and connection types."""
        states = {}
        for state_name, state_data in STATE_TARIFF_MAP.items():
            states[state_name] = cls._state_meta(state_name)
        return {
            "states": states,
            "billing_periods": BILLING_PERIOD_MONTHS,
            "fppca_reference": FPPCA_REFERENCE,
        }
