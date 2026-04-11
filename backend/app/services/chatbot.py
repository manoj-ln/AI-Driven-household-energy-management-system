"""
Advanced Help Bot service for the Smart AI household energy project.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List

from app.services.control_service import ControlService
from app.services.dataset_service import DatasetService
from app.services.optimization_service import OptimizationService
from app.services.prediction_service import PredictionService


def _format_inr(value: float) -> str:
    return f"Rs. {value:,.2f}"


class HelpBot:
    GREETINGS = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}

    def classify_intent(self, message: str) -> str:
        message_lower = message.lower().strip()
        if message_lower in self.GREETINGS or any(word in message_lower for word in ["help", "start conversation", "start chat"]):
            return "greeting"
        if any(keyword in message_lower for keyword in ["last 1 month", "last one month", "past 1 month", "past one month", "this month", "last month"]) and any(keyword in message_lower for keyword in ["energy", "usage", "used", "bill", "amount", "cost"]):
            return "monthly_usage"
        if any(keyword in message_lower for keyword in ["how many data", "dataset count", "records are there", "how much data", "samples"]):
            return "dataset_info"
        if any(keyword in message_lower for keyword in ["graph", "chart", "plot", "axis", "device graphs"]):
            return "graph_help"
        if any(keyword in message_lower for keyword in ["cost optimization", "save money", "reduce bill", "electricity bill", "optimize cost", "bescom bill", "reduce my bill", "cost saving"]):
            return "cost_optimization"
        if any(keyword in message_lower for keyword in ["switched off", "turned off", "off devices", "devices are off"]):
            return "off_devices"
        if any(keyword in message_lower for keyword in ["change model", "model", "ml module", "algorithm", "xgboost", "random forest", "lightgbm"]):
            return "model_info"
        if any(keyword in message_lower for keyword in ["grammar", "spell", "rewrite", "correct"]):
            return "grammar"
        if any(keyword in message_lower for keyword in ["language", "translate", "english", "hindi", "telugu", "tamil", "malayalam"]):
            return "language"
        if any(keyword in message_lower for keyword in ["data quality", "verify data", "analyze data", "dataset", "season", "temperature", "month", "day period"]):
            return "data_quality"
        if any(keyword in message_lower for keyword in ["device", "devices", "status", "running", "info"]):
            return "device_info"
        if any(keyword in message_lower for keyword in ["history", "historical", "past data", "trend", "previous"]):
            return "past_data"
        if any(word in message_lower for word in ["predict", "forecast", "future"]):
            return "predict_device"
        return "project_help"

    def generate_response(self, message: str) -> Dict[str, Any]:
        intent = self.classify_intent(message)
        handlers = {
            "greeting": self._handle_greeting,
            "dataset_info": self._handle_dataset_info,
            "graph_help": self._handle_graph_help,
            "cost_optimization": self._handle_cost_optimization,
            "monthly_usage": self._handle_monthly_usage,
            "predict_device": self._handle_prediction,
            "device_info": self._handle_device_info,
            "off_devices": self._handle_off_devices,
            "past_data": self._handle_past_data,
            "data_quality": self._handle_data_quality,
            "model_info": self._handle_model_info,
            "project_help": self._handle_project_help,
        }
        if intent in handlers:
            return handlers[intent](message)
        if intent == "grammar":
            return self._reply(
                "Send the sentence or paragraph and I will rewrite it in cleaner English for your project report or presentation.",
                intent,
                message,
            )
        if intent == "language":
            return self._reply(
                "I can explain your project in simple English and help rewrite points for report writing, viva answers, and presentation slides.",
                intent,
                message,
            )
        return self._handle_project_help(message)

    def _reply(self, text: str, intent: str, message: str) -> Dict[str, Any]:
        return {
            "response": text,
            "intent": intent,
            "timestamp": datetime.utcnow().isoformat(),
            "suggestions": self._suggest_follow_ups(intent),
        }

    def _handle_greeting(self, message: str) -> Dict[str, Any]:
        text = (
            "Hello! What help do you need with Smart AI?\n\n"
            "I can help with:\n"
            "- device status and switched-off devices\n"
            "- dataset count and data quality verification\n"
            "- graph and chart explanation\n"
            "- verified device predictions\n"
            "- model selection for Random Forest, XGBoost, and LightGBM\n"
            "- cost optimization and BESCOM bill guidance"
        )
        return self._reply(text, "greeting", message)

    def _handle_project_help(self, message: str) -> Dict[str, Any]:
        insights = DatasetService.get_pattern_insights()
        summary = DatasetService.get_summary()
        text = (
            "This project helps you track home energy usage, compare devices, predict future consumption, and estimate rupee-based cost.\n\n"
            f"Current snapshot:\n"
            f"- Dataset records available: {insights['record_count']}\n"
            f"- Daily energy in the latest 24 hours: {summary['daily_consumption']:.2f} kWh\n"
            f"- Current usage: {summary['current_usage']:.2f} kWh\n"
            f"- Peak window: {summary['peak_hour']}\n\n"
            "Ask me about the part you want to inspect, and I will explain it using the current project data."
        )
        return self._reply(text, "project_help", message)

    def _handle_dataset_info(self, message: str) -> Dict[str, Any]:
        insights = DatasetService.get_pattern_insights()
        history = DatasetService.get_historical_data(7)
        device_series = DatasetService.get_device_time_series(1440)
        lines = [
            "Dataset summary:",
            f"- Normalized records available: {insights['record_count']}",
            f"- Historical days summarized: {len(history)}",
            f"- Devices with graphable series: {len(device_series)}",
            f"- Quality score: {insights['quality_score']}/100",
            f"- Invalid or suspicious records: {insights['invalid_records']}",
            f"- Temperature range checked: {insights['temperature_range']}",
        ]
        return self._reply("\n".join(lines), "dataset_info", message)

    def _handle_graph_help(self, message: str) -> Dict[str, Any]:
        summary = DatasetService.get_summary()
        series = DatasetService.get_device_time_series(180)
        top_devices = summary.get("top_devices", [])
        chart_lines = [
            "Graph explanation:",
            "- X-axis shows time.",
            "- Y-axis shows energy used in kWh.",
            "- Each device graph uses the latest available data and extends it into a usable time series when history is sparse.",
            f"- The latest 24-hour peak window is {summary['peak_hour']}.",
        ]
        if top_devices:
            chart_lines.append(f"- Top contributor right now: {top_devices[0]['name']} at {top_devices[0]['average_usage']:.3f} kWh average usage.")
        if series:
            chart_lines.append(f"- Device graphs currently available: {len(series)}.")
        chart_lines.append("- If a device is switched OFF in Device Control, its graph is expected to flatten toward zero.")
        return self._reply("\n".join(chart_lines), "graph_help", message)

    def _handle_device_info(self, message: str) -> Dict[str, Any]:
        devices = ControlService.get_devices()
        if not devices:
            return self._reply("No devices are registered yet.", "device_info", message)
        running_devices = [device for device in devices if device.get("is_on")]
        off_devices = [device for device in devices if not device.get("is_on")]
        lines = [
            f"Registered devices: {len(devices)}",
            f"Running devices: {len(running_devices)}",
            f"Switched-off devices: {len(off_devices)}",
            f"All devices running: {'Yes' if not off_devices else 'No'}",
            "",
        ]
        for device in devices[:12]:
            lines.append(
                f"- {device.get('name', 'Unknown')} | usage: {device.get('average_usage', 0)} kWh | status: {'ON' if device.get('is_on') else 'OFF'}"
            )
        return self._reply("\n".join(lines), "device_info", message)

    def _handle_off_devices(self, message: str) -> Dict[str, Any]:
        devices = ControlService.get_devices()
        off_devices = [device for device in devices if not device.get("is_on")]
        if not off_devices:
            return self._reply("All registered devices are currently ON.", "off_devices", message)
        lines = [f"Switched-off devices: {len(off_devices)}", ""]
        for device in off_devices:
            lines.append(
                f"- {device.get('name', 'Unknown')} | location: {device.get('location', 'Home')} | last known usage: {device.get('average_usage', 0)} kWh"
            )
        return self._reply("\n".join(lines), "off_devices", message)

    def _handle_model_info(self, message: str) -> Dict[str, Any]:
        data = PredictionService.get_available_models()
        lines = [f"Current model: {data['current']}", ""]
        for model in data["models"]:
            preview_value = data.get("preview_predictions", {}).get(model)
            preview_text = f"{preview_value:.3f} kWh next-hour preview" if preview_value is not None else "preview unavailable"
            lines.append(
                f"- {model}: accuracy {(data['accuracies'][model] * 100):.1f}% | source: {data['accuracy_source'][model]} | status: {'Working' if data['availability'][model] else 'Unavailable'} | {preview_text}"
            )
        lines.append("")
        lines.append("You can change the active model from the AI Model Selection panel in Predictions and the next-hour forecast will refresh.")
        return self._reply("\n".join(lines), "model_info", message)

    def _handle_past_data(self, message: str) -> Dict[str, Any]:
        history = DatasetService.get_historical_data(7)
        if not history:
            return self._reply("I could not find historical data yet.", "past_data", message)
        total = sum(float(row.get("total_consumption", 0)) for row in history)
        average = total / len(history)
        top_day = max(history, key=lambda row: float(row.get("total_consumption", 0)))
        response = [
            "Past 7-day consumption summary:",
            f"- Total usage: {total:.2f} kWh",
            f"- Average per day: {average:.2f} kWh",
            f"- Peak day: {top_day.get('date')} at {top_day.get('total_consumption')} kWh",
        ]
        return self._reply("\n".join(response), "past_data", message)

    def _handle_monthly_usage(self, message: str) -> Dict[str, Any]:
        history = DatasetService.get_historical_data(30)
        if not history:
            return self._reply("I could not find enough historical data for a one-month summary yet.", "monthly_usage", message)
        total = sum(float(row.get("total_consumption", 0)) for row in history)
        total_cost = round(total * 6.26, 2)
        average = total / len(history)
        highest_day = max(history, key=lambda row: float(row.get("total_consumption", 0)))
        response = [
            "Last-month energy summary:",
            f"- Days available in the dataset: {len(history)}",
            f"- Total energy used: {total:.2f} kWh",
            f"- Average per available day: {average:.2f} kWh",
            f"- Estimated total amount at BESCOM rate: {_format_inr(total_cost)}",
            f"- Highest recorded day: {highest_day.get('date')} with {float(highest_day.get('total_consumption', 0)):.2f} kWh",
        ]
        if len(history) < 30:
            response.append(f"- Note: only {len(history)} days are available right now, so this is based on the current stored history rather than a full 30-day month.")
        return self._reply("\n".join(response), "monthly_usage", message)

    def _handle_data_quality(self, message: str) -> Dict[str, Any]:
        insights = DatasetService.get_pattern_insights()
        response = [
            "Dataset quality and pattern verification:",
            f"- Records checked: {insights['record_count']}",
            f"- Quality score: {insights['quality_score']}/100",
            f"- Invalid records: {insights['invalid_records']}",
            f"- Dominant season in data: {insights['dominant_season']}",
            f"- Dominant day period in data: {insights['dominant_day_period']}",
            f"- Current day period: {insights['current_day_period']}",
            f"- Check time: {datetime.fromisoformat(insights['current_timestamp']).strftime('%d %b %Y %I:%M %p')}",
            f"- Temperature range checked: {insights['temperature_range']}",
        ]
        for note in insights.get("notes", [])[:3]:
            response.append(f"- Note: {note}")
        return self._reply("\n".join(response), "data_quality", message)

    def _handle_cost_optimization(self, message: str) -> Dict[str, Any]:
        report = OptimizationService.get_report()
        lines = [
            "Advanced cost optimization summary:",
            f"- Daily cost now: {_format_inr(report['baseline_cost'])}",
            f"- Optimized daily cost: {_format_inr(report['optimized_cost'])}",
            f"- Daily savings: {_format_inr(report['estimated_savings'])}",
            f"- Monthly energy cost estimate: {_format_inr(report['monthly_projection']['energy_charge_inr'])}",
            f"- Monthly fixed charge estimate: {_format_inr(report['monthly_projection']['fixed_charge_inr'])}",
            f"- Monthly surcharge estimate: {_format_inr(report['monthly_projection']['surcharge_inr'])}",
            f"- Projected monthly total: {_format_inr(report['monthly_projection']['bill_total_inr'])}",
            "",
            "How it is calculated:",
            f"- BESCOM base energy rate: {_format_inr(report['tariff']['base_energy_rate_inr'])} per unit",
            f"- BESCOM surcharge: {_format_inr(report['tariff']['surcharge_rate_inr'])} per unit",
            f"- Effective rate used: {_format_inr(report['tariff']['energy_rate_inr'])} per unit",
        ]
        for lever in report.get("savings_levers", [])[:3]:
            lines.append(f"- {lever['label']}: save up to {_format_inr(lever['daily_savings_inr'])} per day")
        return self._reply("\n".join(lines), "cost_optimization", message)

    def _handle_prediction(self, message: str) -> Dict[str, Any]:
        message_lower = message.lower()
        device = None
        hours = 24
        devices = {
            "washing machine": "washing_machine",
            "washer": "washing_machine",
            "fan": "fan",
            "refrigerator": "refrigerator",
            "fridge": "refrigerator",
            "air conditioner": "air_conditioner",
            "ac": "air_conditioner",
            "heater": "heater",
            "oven": "oven",
            "microwave": "microwave",
            "light": "light",
            "bulb": "light",
            "tv": "tv",
            "television": "tv",
        }
        for device_name, device_id in devices.items():
            if device_name in message_lower:
                device = device_id
                break
        hour_match = re.search(r"(\d+)\s*hours?", message_lower)
        if hour_match:
            hours = min(int(hour_match.group(1)), 168)
        if not device:
            device = "home_energy"
        prediction_result = PredictionService.predict_device_usage(device, hours)
        response = [
            f"Verified energy prediction for {prediction_result['display_name']}:",
            f"- Duration: {hours} hours",
            f"- Total energy: {prediction_result['total_energy_kwh']:.2f} kWh",
            f"- Average power: {prediction_result['average_power_kw']:.2f} kW",
            f"- Estimated cost with BESCOM energy rate: {_format_inr(prediction_result['estimated_cost_inr'])}",
            f"- Practical daily limit: {prediction_result['practical_limit_kwh_per_day']:.2f} kWh",
            f"- Validation result: {'Practical' if prediction_result['is_practical'] else 'Adjusted'}",
            "",
            "Verification checks:",
        ]
        for note in prediction_result["validation_notes"]:
            response.append(f"- {note}")
        return self._reply("\n".join(response), "predict_device", message)

    def _suggest_follow_ups(self, intent: str) -> List[str]:
        suggestion_map = {
            "greeting": [
                "How many datasets are there?",
                "What does the graph show?",
                "Which model is active?",
            ],
            "dataset_info": [
                "Analyze data quality",
                "What does the graph show?",
                "How can I reduce my BESCOM bill?",
            ],
            "graph_help": [
                "Top device contributors",
                "Predict fan for 12 hours",
                "Analyze data quality",
            ],
            "model_info": [
                "Predict refrigerator for 24 hours",
                "How many datasets are there?",
                "How can I reduce my BESCOM bill?",
            ],
            "cost_optimization": [
                "Which devices are switched off?",
                "Top device contributors",
                "Predict washing machine for 24 hours",
            ],
            "device_info": [
                "Which devices are switched off?",
                "What does the graph show?",
                "How many datasets are there?",
            ],
            "predict_device": [
                "Which model is active?",
                "Analyze data quality",
                "How can I reduce my BESCOM bill?",
            ],
            "monthly_usage": [
                "What does the graph show?",
                "How can I reduce my BESCOM bill?",
                "Which model is active?",
            ],
        }
        return suggestion_map.get(
            intent,
            ["How many datasets are there?", "What does the graph show?", "How can I reduce my BESCOM bill?"],
        )


help_bot = HelpBot()


def get_chatbot_response(message: str) -> Dict[str, Any]:
    return help_bot.generate_response(message)
