"""
Advanced Help Bot service for the Smart AI household energy project.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List
from langdetect import detect, LangDetectException
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.services.control_service import ControlService
from app.services.dataset_service import DatasetService
from app.services.optimization_service import OptimizationService
from app.services.prediction_service import PredictionService
from app.database.db import db


def _format_inr(value: float) -> str:
    return f"Rs. {value:,.2f}"


class HelpBot:
    GREETINGS = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}

    def __init__(self):
        self._intent_examples = {
            "dataset_info": [
                "how much data is available",
                "how many records are loaded",
                "show data coverage",
            ],
            "dataset_files": [
                "which csv files are available",
                "show dataset file names",
                "what datasets can i choose",
            ],
            "dataset_mode": [
                "what mode is currently active",
                "which dataset mode is selected",
                "show current mode",
            ],
            "model_info": [
                "what model is running now",
                "which ai model is currently active",
                "show current prediction engine",
            ],
            "cost_optimization": [
                "how to reduce electricity spending",
                "where can i save bill amount",
                "cost saving suggestions for home energy",
            ],
            "predict_device": [
                "estimate future usage",
                "forecast next hours consumption",
                "predict appliance load",
            ],
            "device_info": [
                "show all device status",
                "list active and inactive devices",
                "which devices are running now",
            ],
            "project_help": [
                "what does this project do",
                "explain project overview",
                "summarize this system",
            ],
        }
        self._nlp_phrases = []
        self._nlp_labels = []
        for intent, phrases in self._intent_examples.items():
            for phrase in phrases:
                self._nlp_phrases.append(phrase)
                self._nlp_labels.append(intent)
        self._vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        self._phrase_matrix = self._vectorizer.fit_transform(self._nlp_phrases)

    def classify_intent(self, message: str) -> str:
        message_lower = message.lower().strip()
        if message_lower in self.GREETINGS or any(word in message_lower for word in ["help", "start conversation", "start chat"]):
            return "greeting"
        if any(keyword in message_lower for keyword in ["last 1 month", "last one month", "past 1 month", "past one month", "this month", "last month"]) and any(keyword in message_lower for keyword in ["energy", "usage", "used", "bill", "amount", "cost"]):
            return "monthly_usage"
        if any(keyword in message_lower for keyword in ["how many data", "dataset count", "records are there", "how much data", "samples"]):
            return "dataset_info"
        if any(keyword in message_lower for keyword in ["available datasets", "list datasets", "dataset files", "which datasets"]):
            return "dataset_files"
        if any(keyword in message_lower for keyword in ["active dataset", "selected dataset", "dataset mode", "which mode"]):
            return "dataset_mode"
        if any(keyword in message_lower for keyword in ["graph", "chart", "plot", "axis", "device graphs"]):
            return "graph_help"
        if any(keyword in message_lower for keyword in ["today", "todays", "today's", "current day"]) and any(
            keyword in message_lower for keyword in ["consumption", "usage", "energy", "kwh"]
        ):
            return "device_today_consumption"
        if any(keyword in message_lower for keyword in ["what is", "define", "meaning of"]) and any(
            keyword in message_lower for keyword in ["fan", "ac", "air conditioner", "heater", "refrigerator", "fridge", "light", "tv", "oven", "microwave", "washing machine"]
        ):
            return "device_explain"
        if any(keyword in message_lower for keyword in ["grammar", "spell", "rewrite", "correct"]):
            return "grammar"
        if any(keyword in message_lower for keyword in ["language", "translate", "english", "hindi", "telugu", "tamil", "malayalam", "kannada", "ಕನ್ನಡ"]):
            return "language"
        if any(keyword in message_lower for keyword in ["cost optimization", "save money", "reduce bill", "electricity bill", "optimize cost", "bescom bill", "reduce my bill", "cost saving"]):
            return "cost_optimization"
        if any(keyword in message_lower for keyword in ["switched off", "turned off", "off devices", "devices are off"]):
            return "off_devices"
        if any(keyword in message_lower for keyword in ["change model", "model", "ml module", "algorithm", "xgboost", "random forest", "lightgbm"]):
            return "model_info"
        if any(keyword in message_lower for keyword in ["data quality", "verify data", "analyze data", "dataset", "season", "temperature", "month", "day period"]):
            return "data_quality"
        if any(keyword in message_lower for keyword in ["device", "devices", "status", "running", "info"]):
            return "device_info"
        if any(keyword in message_lower for keyword in ["history", "historical", "past data", "trend", "previous"]):
            return "past_data"
        if any(word in message_lower for word in ["predict", "forecast", "future"]):
            return "predict_device"
        nlp_intent = self._classify_with_nlp(message_lower)
        if nlp_intent:
            return nlp_intent
        return "project_help"

    def _classify_with_nlp(self, message: str) -> str | None:
        text = str(message or "").strip().lower()
        if len(text) < 4:
            return None
        vector = self._vectorizer.transform([text])
        scores = cosine_similarity(vector, self._phrase_matrix)[0]
        if len(scores) == 0:
            return None
        best_index = int(scores.argmax())
        best_score = float(scores[best_index])
        if best_score < 0.34:
            return None
        return self._nlp_labels[best_index]

    def generate_response(self, message: str, session_id: str = "default", user_name: str | None = None) -> Dict[str, Any]:
        history = db.get_chat_history(session_id=session_id, limit=8)
        normalized_message = message.strip()
        db.save_chat_message(session_id=session_id, role="user", message=normalized_message)

        intent = self.classify_intent(normalized_message)
        if intent == "project_help":
            intent = self._infer_followup_intent(normalized_message, history) or intent
        handlers = {
            "greeting": self._handle_greeting,
            "dataset_info": self._handle_dataset_info,
            "dataset_files": self._handle_dataset_files,
            "dataset_mode": self._handle_dataset_mode,
            "device_explain": self._handle_device_explain,
            "device_today_consumption": self._handle_device_today_consumption,
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
            response = handlers[intent](normalized_message)
            response["session_id"] = session_id
            if user_name:
                response["personalization"] = {"user_name": user_name}
            db.save_chat_message(
                session_id=session_id,
                role="bot",
                message=response.get("response", ""),
                intent=response.get("intent"),
            )
            return response
        if intent == "grammar":
            response = self._handle_grammar(normalized_message)
            response["session_id"] = session_id
            db.save_chat_message(session_id=session_id, role="bot", message=response.get("response", ""), intent=response.get("intent"))
            return response
        if intent == "language":
            response = self._handle_language(normalized_message)
            response["session_id"] = session_id
            db.save_chat_message(session_id=session_id, role="bot", message=response.get("response", ""), intent=response.get("intent"))
            return response
        response = self._handle_project_help(normalized_message)
        response["session_id"] = session_id
        db.save_chat_message(session_id=session_id, role="bot", message=response.get("response", ""), intent=response.get("intent"))
        return response

    def _reply(self, text: str, intent: str, message: str) -> Dict[str, Any]:
        confidence = 0.9 if intent not in {"project_help", "grammar", "language"} else 0.78
        return {
            "response": text,
            "intent": intent,
            "confidence": confidence,
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

    def _handle_dataset_files(self, message: str) -> Dict[str, Any]:
        datasets = DatasetService.list_datasets()
        if not datasets:
            return self._reply("No CSV datasets are available right now.", "dataset_files", message)
        lines = ["Available CSV datasets:"]
        for item in datasets:
            lines.append(f"- {item}")
        lines.append("")
        lines.append("You can select any dataset from the Home page dataset dropdown.")
        return self._reply("\n".join(lines), "dataset_files", message)

    def _handle_dataset_mode(self, message: str) -> Dict[str, Any]:
        mode_match = re.search(r"set\s+dataset\s+mode\s+to\s+([a-z_]+)", message.lower())
        if mode_match:
            requested_mode = mode_match.group(1).strip()
            result = DatasetService.set_dataset_mode(requested_mode)
            if result.get("status") == "success":
                return self._reply(
                    f"Dataset mode updated successfully.\n- Mode: {result.get('mode')}\n- Selected dataset: {result.get('selected_dataset')}",
                    "dataset_mode",
                    message,
                )
            return self._reply(
                f"Could not update dataset mode.\n- Reason: {result.get('message', 'Unknown error')}",
                "dataset_mode",
                message,
            )

        mode_data = DatasetService.get_dataset_mode()
        lines = [
            "Current dataset configuration:",
            f"- Mode: {mode_data.get('mode')}",
            f"- Selected dataset: {mode_data.get('selected_dataset')}",
            "- Supported modes: " + ", ".join(mode_data.get("supported_modes", [])),
        ]
        return self._reply("\n".join(lines), "dataset_mode", message)

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

    def _extract_device_key(self, message: str) -> str:
        lowered = message.lower()
        mapping = {
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
        for label, key in mapping.items():
            if label in lowered:
                return key
        return "home_energy"

    def _handle_device_explain(self, message: str) -> Dict[str, Any]:
        device_key = self._extract_device_key(message)
        catalog = PredictionService.DEVICE_PROFILES.get(device_key, PredictionService.DEVICE_PROFILES["home_energy"])
        text = (
            f"{catalog.get('display_name', device_key)} in this project means a tracked home load category used for analytics and forecasting.\n"
            f"- Typical daily hours: {catalog.get('typical_daily_hours', 0)}\n"
            f"- Rated power reference: {catalog.get('rated_kw', 0)} kW\n"
            "- It contributes to forecast, anomaly, and optimization calculations."
        )
        return self._reply(text, "device_explain", message)

    def _handle_device_today_consumption(self, message: str) -> Dict[str, Any]:
        device_key = self._extract_device_key(message)
        series = DatasetService.get_device_time_series(1440)
        device_row = None
        for row in series:
            device_id = str(row.get("device_id", "")).lower()
            device_name = str(row.get("device_name", "")).lower()
            if device_key in device_id or device_key.replace("_", " ") in device_name:
                device_row = row
                break
        if not device_row:
            if device_key == "home_energy":
                summary = DatasetService.get_summary()
                return self._reply(
                    f"Today's total home energy consumption (latest 24h window) is {summary.get('daily_consumption', 0):.2f} kWh.",
                    "device_today_consumption",
                    message,
                )
            return self._reply(
                f"I could not find today's {device_key.replace('_', ' ')} data in the current dataset. Try changing dataset file or mode.",
                "device_today_consumption",
                message,
            )
        total = float(device_row.get("total_energy_kwh", 0.0))
        response = (
            f"Today's {device_row.get('device_name', device_key)} energy consumption is {total:.2f} kWh "
            "(latest 24-hour window).\n"
            f"- Share of total tracked load: {float(device_row.get('share', 0.0)):.1f}%"
        )
        return self._reply(response, "device_today_consumption", message)

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

    def _handle_grammar(self, message: str) -> Dict[str, Any]:
        cleaned = self._extract_user_text(message)
        trigger_words = ("grammar", "rewrite", "correct", "spell")
        if any(word in cleaned.lower() for word in trigger_words):
            # strip common prompt prefixes and keep user content
            for token in ("rewrite:", "correct:", "grammar:", "spell check:"):
                cleaned = cleaned.replace(token, "")
            cleaned = cleaned.strip()
        if len(cleaned.split()) < 4:
            return self._reply(
                "Share a full sentence or paragraph and I will rewrite it in clean project-report English.",
                "grammar",
                message,
            )
        language = self._detect_language(cleaned)
        rewritten = self._rewrite_english(cleaned) if language["code"] == "en" else self._normalize_generic(cleaned)
        issues = self._grammar_diagnostics(cleaned, rewritten, language["code"])
        response = [
            f"Detected language: {language['name']} ({language['code']})",
            "Grammar review:",
        ]
        for issue in issues:
            response.append(f"- {issue}")
        response.extend([
            "",
            "Rewritten version:",
            f"- {rewritten}",
            "",
            "Tip: Keep sentences short and include numbers (kWh, INR, % confidence) in presentations.",
        ])
        return self._reply("\n".join(response), "grammar", message)

    def _handle_language(self, message: str) -> Dict[str, Any]:
        cleaned = self._extract_user_text(message)
        language = self._detect_language(cleaned)
        lowered = message.lower()
        if "kannada" in lowered or "ಕನ್ನಡ" in message or language["code"] == "kn":
            text = (
                "ಈ ಪ್ರಾಜೆಕ್ಟ್ ಮನೆಯ ವಿದ್ಯುತ್ ಬಳಕೆಯನ್ನು ಗಮನಿಸಿ ವಿಶ್ಲೇಷಿಸಲು ಸಹಾಯ ಮಾಡುತ್ತದೆ.\n"
                "- ದಿನನಿತ್ಯ ಬಳಕೆ (kWh) ಮತ್ತು ಸಾಧನ ಮಟ್ಟದ ಬಳಕೆ ತೋರಿಸುತ್ತದೆ.\n"
                "- ಮುಂದಿನ ಗಂಟೆಗಳ ಬಳಕೆಯನ್ನು AI ಮೂಲಕ ಅಂದಾಜಿಸುತ್ತದೆ.\n"
                "- ವೆಚ್ಚ ಆಪ್ಟಿಮೈಸೇಶನ್ ಸಲಹೆ ನೀಡಿ ವಿದ್ಯುತ್ ಬಿಲ್ ಕಡಿಮೆ ಮಾಡಲು ಸಹಾಯ ಮಾಡುತ್ತದೆ.\n"
                "- ಡೇಟಾಸೆಟ್ ಆಯ್ಕೆ, ಅನಾಮಲಿ ಪತ್ತೆ, ಮತ್ತು Explainability ಸಹ ಇದೆ."
            )
            return self._reply(text, "language", message)
        text = (
            "Language support summary:\n"
            f"- Detected language: {language['name']} ({language['code']})\n"
            "- I can recognize multilingual text and give grammar-oriented cleanup.\n"
            "- For English, corrections are stronger (capitalization, punctuation, contractions, spacing).\n"
            "- For other languages, I provide normalization and readability cleanup.\n"
            "- Ask: 'grammar: <your sentence>' for correction."
        )
        return self._reply(text, "language", message)

    def _infer_followup_intent(self, message: str, history: List[Dict[str, Any]]) -> str | None:
        text = message.strip().lower()
        if len(text.split()) > 5:
            return None
        recent_bot_intents = [row.get("intent") for row in history if row.get("role") == "bot" and row.get("intent")]
        if not recent_bot_intents:
            return None
        last_intent = recent_bot_intents[-1]
        followup_tokens = {"more", "details", "explain", "why", "how", "continue", "next"}
        if any(token in text for token in followup_tokens):
            return last_intent
        return None

    @staticmethod
    def _extract_user_text(message: str) -> str:
        text = str(message or "").strip()
        if ":" in text:
            tail = text.split(":", 1)[1].strip()
            if tail:
                return tail
        return text

    @staticmethod
    def _normalize_generic(text: str) -> str:
        value = re.sub(r"\s+", " ", str(text or "")).strip()
        if value and value[-1] not in ".!?":
            value += "."
        return value

    def _rewrite_english(self, text: str) -> str:
        rewritten = str(text or "")
        rewritten = re.sub(r"\s+", " ", rewritten).strip()
        replacements = {
            r"\bi\b": "I",
            r"\bdont\b": "don't",
            r"\bcant\b": "can't",
            r"\bwont\b": "won't",
            r"\bim\b": "I'm",
            r"\bive\b": "I've",
            r"\bits\b": "it's",
        }
        for pattern, replacement in replacements.items():
            rewritten = re.sub(pattern, replacement, rewritten, flags=re.IGNORECASE)
        rewritten = re.sub(r"\s+([,.!?;:])", r"\1", rewritten)
        if rewritten:
            rewritten = rewritten[0].upper() + rewritten[1:]
        if rewritten and rewritten[-1] not in ".!?":
            rewritten += "."
        return rewritten

    def _grammar_diagnostics(self, original: str, rewritten: str, lang_code: str) -> List[str]:
        issues: List[str] = []
        if re.search(r"\s{2,}", original):
            issues.append("Removed extra spaces.")
        if re.search(r"\s+[,.!?;:]", original):
            issues.append("Removed spaces before punctuation.")
        if original and original[0].islower():
            issues.append("Capitalized the first letter.")
        if original and original[-1] not in ".!?":
            issues.append("Added sentence-ending punctuation.")
        if lang_code == "en":
            if re.search(r"\bdont\b|\bcant\b|\bwont\b|\bim\b|\bive\b", original, flags=re.IGNORECASE):
                issues.append("Fixed common English contractions.")
            if not issues:
                issues.append("No major English grammar issues detected.")
        else:
            if not issues:
                issues.append("Applied language-agnostic readability normalization.")
        return issues

    def _detect_language(self, text: str) -> Dict[str, str]:
        value = str(text or "").strip()
        script_map = [
            (r"[\u0900-\u097F]", ("hi", "Hindi/Devanagari")),
            (r"[\u0C00-\u0C7F]", ("te", "Telugu")),
            (r"[\u0B80-\u0BFF]", ("ta", "Tamil")),
            (r"[\u0D00-\u0D7F]", ("ml", "Malayalam")),
            (r"[\u0C80-\u0CFF]", ("kn", "Kannada")),
        ]
        for pattern, data in script_map:
            if re.search(pattern, value):
                return {"code": data[0], "name": data[1]}
        try:
            code = detect(value) if value else "unknown"
        except LangDetectException:
            code = "unknown"
        names = {
            "en": "English",
            "hi": "Hindi",
            "te": "Telugu",
            "ta": "Tamil",
            "ml": "Malayalam",
            "kn": "Kannada",
            "fr": "French",
            "de": "German",
            "es": "Spanish",
            "it": "Italian",
            "pt": "Portuguese",
            "ar": "Arabic",
            "zh-cn": "Chinese",
            "ja": "Japanese",
            "ko": "Korean",
        }
        return {"code": code, "name": names.get(code, "Detected Language")}

    def _suggest_follow_ups(self, intent: str) -> List[str]:
        suggestion_map = {
            "greeting": [
                "How many datasets are there?",
                "What does the graph show?",
                "Which model is active?",
            ],
            "dataset_info": [
                "List available datasets",
                "Which dataset mode is active?",
                "Analyze data quality",
                "What does the graph show?",
                "How can I reduce my BESCOM bill?",
            ],
            "dataset_files": [
                "Which dataset mode is active?",
                "How many datasets are there?",
                "Analyze data quality",
            ],
            "dataset_mode": [
                "List available datasets",
                "How many datasets are there?",
                "What does the graph show?",
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
                "What is fan?",
                "Today's fan energy consumption",
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


def get_chatbot_response(message: str, session_id: str = "default", user_name: str | None = None) -> Dict[str, Any]:
    return help_bot.generate_response(message, session_id=session_id, user_name=user_name)
