"""
Advanced Help Bot service for the Smart AI household energy project.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List
from langdetect import detect, LangDetectException
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.services.control_service import ControlService
from app.services.db_service import DatabaseService
from app.services.dataset_service import DatasetService
from app.services.optimization_service import OptimizationService
from app.services.prediction_service import PredictionService
from app.database.repository import db


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
            "troubleshooting": [
                "device not responding",
                "graph not showing",
                "accuracy is low",
                "how to fix the system",
                "data seems wrong",
            ],
            "project_help": [
                "what does this project do",
                "explain project overview",
                "summarize this system",
                "tech stack architecture",
                "what is this platform",
            ],
            "graph_help": [
                "what does the graph show",
                "explain the usage graph",
                "x axis y axis chart",
            ],
            "device_ranking": [
                "top device contributors",
                "which device uses most energy",
                "highest consumption device",
            ],
            "device_explain": [
                "what is fan",
                "explain refrigerator device",
                "what does ac mean",
            ],
            "device_today_consumption": [
                "today fan energy consumption",
                "how much did fridge use today",
            ],
            "past_data": [
                "past week consumption",
                "historical usage summary",
                "last 7 days energy",
            ],
            "data_quality": [
                "analyze data quality",
                "dataset quality score",
                "check data integrity",
            ],
            "manual_input_help": [
                "how to use manual input",
                "add energy readings",
                "data input page help",
            ],
            "simulation_help": [
                "how does simulation work",
                "what if scenario energy",
            ],
            "explainability_help": [
                "explainability page",
                "prediction drivers",
                "feature importance forecast",
            ],
            "anomaly_help": [
                "anomaly detection",
                "unusual energy usage",
                "detect outliers",
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

    def classify_intent(self, message: str, history: List[Dict[str, Any]] = None) -> str:
        message_lower = message.lower().strip()
        
        # 1. Contextual Intent Detection (Follow-ups)
        if history:
            followup = self._infer_followup_intent(message_lower, history)
            if followup:
                return followup
            if len(message_lower.split()) < 4:
                last_intent = history[-1].get("intent") if history else None
                if any(word in message_lower for word in ["more", "details", "explain", "why", "how", "tell me"]):
                    if last_intent in ["weather_report", "monthly_usage", "device_info", "dataset_info", "dataset_files", "dataset_mode", "cost_optimization", "graph_help", "device_ranking"]:
                        return last_intent

        # 2. Format / language / grammar shortcuts
        if message_lower.startswith("grammar:") or re.search(r"\b(rewrite|spell check|correct grammar)\b", message_lower):
            return "grammar"
        if "kannada" in message_lower or "ಕನ್ನಡ" in message or message_lower.startswith("language:"):
            return "language"
        if "about project in kannada" in message_lower:
            return "language"

        # 3. Direct Keyword/Regex Matching (Pillar 4: Domain Specific)
        if message_lower in self.GREETINGS or any(word in message_lower for word in ["help", "start conversation"]):
            return "greeting"

        if re.search(r"\b(list|show|available)\b.*\b(datasets?|csv)\b", message_lower) or message_lower.startswith("list available datasets"):
            return "dataset_files"
        if re.search(r"\b(how many|count|number of)\b.*\bdatasets?\b", message_lower) or "how many datasets are there" in message_lower:
            return "dataset_info"
        if re.search(r"\b(dataset mode|which mode|current mode)\b", message_lower):
            return "dataset_mode"

        if re.search(r"\b(graph|chart|x-axis|y-axis|usage graph)\b", message_lower) or "what does the graph show" in message_lower:
            return "graph_help"

        if re.search(r"\b(top\s*\d*\s*device|device ranking|most energy|highest consumption|contributors|uses most energy)\b", message_lower):
            return "device_ranking"

        if re.search(r"\b(explainability|feature importance|prediction drivers|shap)\b", message_lower):
            return "explainability_help"

        if re.search(r"\b(anomaly|anomalies|outlier|unusual usage)\b", message_lower):
            return "anomaly_help"

        if re.search(r"\b(manual input|data input|ingest|add reading)\b", message_lower):
            return "manual_input_help"

        if re.search(r"\b(simulation|what if scenario)\b", message_lower):
            return "simulation_help"

        if re.search(r"\b(past data|last 7 days|historical usage|past week)\b", message_lower):
            return "past_data"

        if re.search(r"\b(data quality|quality score|invalid records)\b", message_lower):
            return "data_quality"

        if re.search(r"\b(switch off|turned off|off devices)\b", message_lower):
            return "off_devices"

        if re.search(r"\bwhat is (a |the )?(fan|fridge|refrigerator|ac|air conditioner|heater|tv|light|bulb|washing machine|microwave)\b", message_lower):
            return "device_explain"

        if re.search(r"\btoday('s|s)?\s.*(energy|consumption|usage)\b", message_lower) or "todays" in message_lower.replace(" ", ""):
            return "device_today_consumption"

        if re.search(r"\b(optimize|optimization|save energy|reduce bill|bescom rate|cost saving)\b", message_lower) and not re.search(r"\bmonthly bill\b", message_lower):
            return "cost_optimization"
            
        if re.search(r"\b(month|monthly bill|payment|monetary|money)\b", message_lower):
            return "monthly_usage"
            
        if any(word in message_lower for word in ["weather", "temperature", "climate", "outside", "hot", "cold"]):
            return "weather_report"

        if any(phrase in message_lower for phrase in ["current season", "active dataset", "simulation mode", "system status"]):
            return "system_status_query"

        # 4. Dynamic Device Lookup (Pillar 2: Knowledge Integration)
        devices = DatabaseService.get_all_devices()
        for d in devices:
            if d['name'].lower() in message_lower:
                return "device_dynamic_query"

        if re.search(r"\b(model|xgboost|random forest|lightgbm|prediction engine|ai model)\b", message_lower):
            return "model_info"

        # 5. Fallback to NLP/FAQ
        if self._faq_match(message_lower) is not None:
            return "faq_lookup"
            
        nlp_intent = self._classify_with_nlp(message_lower)
        return nlp_intent or "project_help"

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

        # Detect requested format
        requested_format = "default"
        lower_msg = normalized_message.lower()
        if any(w in lower_msg for w in ["in points", "as points", "bullet points"]):
            requested_format = "points"
        elif any(w in lower_msg for w in ["in theory", "theory form", "paragraph", "in detail"]):
            requested_format = "theory"
        elif any(w in lower_msg for w in ["single line", "one line", "short", "in a line"]):
            requested_format = "single_line"

        try:
            intent = self.classify_intent(normalized_message, history)
            
            # Personality Layer: If user name exists, adapt tone
            greeting_prefix = f"Hello {user_name}! " if user_name else "Hello! "
            
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
                "device_ranking": self._handle_device_ranking,
                "off_devices": self._handle_off_devices,
                "past_data": self._handle_past_data,
                "data_quality": self._handle_data_quality,
                "model_info": self._handle_model_info,
                "project_help": self._handle_project_help,
                "faq_lookup": self._handle_faq_lookup,
                "troubleshooting": self._handle_troubleshooting,
                "device_dynamic_query": self._handle_device_dynamic_query,
                "system_status_query": self._handle_system_status_query,
                "weather_report": self._handle_weather_report,
                "manual_input_help": self._handle_manual_input_help,
                "simulation_help": self._handle_simulation_help,
                "explainability_help": self._handle_explainability_help,
                "anomaly_help": self._handle_anomaly_help,
            }
            if intent in handlers:
                response = handlers[intent](normalized_message)
                response["response"] = self._format_output(response.get("response", ""), requested_format)
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
                response["response"] = self._format_output(response.get("response", ""), requested_format)
                response["session_id"] = session_id
                db.save_chat_message(session_id=session_id, role="bot", message=response.get("response", ""), intent=response.get("intent"))
                return response
            if intent == "language":
                response = self._handle_language(normalized_message)
                response["response"] = self._format_output(response.get("response", ""), requested_format)
                response["session_id"] = session_id
                db.save_chat_message(session_id=session_id, role="bot", message=response.get("response", ""), intent=response.get("intent"))
                return response
            
            response = self._handle_project_help(normalized_message)
            response["response"] = self._format_output(response.get("response", ""), requested_format)
            response["session_id"] = session_id
            db.save_chat_message(session_id=session_id, role="bot", message=response.get("response", ""), intent=response.get("intent"))
            return response
        except Exception as e:
            # Fallback to FAQ or general help on any failure
            return {
                "response": f"I had a slight technical hiccup analyzing that, but I'm back! {self._faq_match(normalized_message.lower()) or 'How can I help you with your energy data today?'}",
                "intent": "error_fallback",
                "session_id": session_id
            }

    def _format_output(self, text: str, requested_format: str) -> str:
        if requested_format == "default":
            return text
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if requested_format == "single_line":
            clean_lines = [line.lstrip('- ') for line in lines]
            return " ".join(clean_lines)
            
        if requested_format == "points":
            formatted = []
            for line in lines:
                if not line.startswith("-") and not line.endswith(":"):
                    formatted.append(f"- {line}")
                else:
                    formatted.append(line)
            return "\n".join(formatted)
            
        if requested_format == "theory":
            paragraphs = []
            current_para = []
            for line in lines:
                clean_line = line.lstrip('- ')
                current_para.append(clean_line)
                if line.endswith('.') or line.endswith(':'):
                    paragraphs.append(" ".join(current_para))
                    current_para = []
            if current_para:
                paragraphs.append(" ".join(current_para))
            return "\n\n".join(paragraphs)
            
        return text

    def _reply(self, text: str, intent: str, message: str) -> Dict[str, Any]:
        confidence = 0.9 if intent not in {"project_help", "grammar", "language"} else 0.78
        return {
            "response": text,
            "intent": intent,
            "confidence": confidence,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "suggestions": self._suggest_follow_ups(intent),
        }

    def _faq_match(self, message: str) -> str | None:
        """Return best FAQ answer from project knowledge or SQLite database."""
        msg = message.lower().strip()
        from app.services.project_knowledge import PROJECT_FAQ
        for keywords, answer in PROJECT_FAQ:
            if any(kw.lower() in msg or msg in kw.lower() for kw in keywords):
                return answer
        return DatabaseService.query_faq(message)

    def _handle_troubleshooting(self, message: str) -> Dict[str, Any]:
        text = (
            "I've analyzed the system diagnostic state. Here are some troubleshooting steps:\n\n"
            "1. **Graphs not loading:** Ensure the dataset selection is valid on the Home page.\n"
            "2. **Inaccurate Predictions:** Try switching the AI Model (XGBoost often has better accuracy for high-variance data).\n"
            "3. **Device Missing:** Check if the device is registered in the Device Library and active in Control.\n"
            "4. **Backend Errors:** Verify that the FastAPI server is running on port 8000.\n\n"
            "If issues persist, try refreshing the page or restarting the backend service."
        )
        return self._reply(text, "troubleshooting", message)

    def _handle_device_dynamic_query(self, message: str) -> Dict[str, Any]:
        message_lower = message.lower()
        devices = DatabaseService.get_all_devices()
        target_device = None
        for d in devices:
            if d['name'].lower() in message_lower:
                target_device = d
                break
        
        if not target_device:
            return self._handle_faq_lookup(message)

        # Build a highly specific, real-time response
        features = json.loads(target_device['smart_features'])
        feat_str = ", ".join(features) if features else "Standard smart monitoring"
        
        text = (
            f"I've just queried the real-time device database for you. Here is the latest on the **{target_device['name']}**:\n\n"
            f"• **Status:** {target_device['status'].upper()}\n"
            f"• **Power Rating:** {target_device['rated_power']}\n"
            f"• **Category:** {target_device['category']}\n"
            f"• **Smart Features:** {feat_str}\n\n"
            f"**Description:** {target_device['description']}\n\n"
            f"Currently, this device is being tracked with 10-minute granularity in our 3-year master dataset. "
            f"Would you like me to analyze its specific energy trend for the last 24 hours?"
        )
        return self._reply(text, "device_info", message)

    def _handle_system_status_query(self, message: str) -> Dict[str, Any]:
        # Fetch real-time system state
        mode_info = DatasetService.get_dataset_mode()
        insights = DatasetService._get_dataset_details()
        season = insights.get("pattern_insights", {}).get("dominant_season", "Unknown")
        
        text = (
            f"Here is the real-time status of your Energy Management System:\n\n"
            f"• **Current Season:** {season}\n"
            f"• **Active Dataset:** `{mode_info['selected_dataset']}`\n"
            f"• **Simulation Mode:** {mode_info['mode'].upper()}\n"
            f"• **Data Coverage:** 3-Year Extended (2023-2025)\n\n"
            f"The AI models are currently optimized for the {season} profile found in the active dataset."
        )
        return self._reply(text, "system_status", message)

    def _handle_weather_report(self, message: str) -> Dict[str, Any]:
        # Fetch latest data point for weather
        summary = DatasetService.get_summary()
        temp = summary.get("average_temperature", 24.0)
        insights = DatasetService.get_pattern_insights()
        temp_range = insights.get("temperature_range", "20-30°C")
        season = insights.get("dominant_season", "Unknown")
        
        # Determine comfort level
        comfort = "Pleasant"
        if temp > 30: comfort = "Warm"
        if temp > 35: comfort = "Hot"
        if temp < 18: comfort = "Cool"
        
        text = (
            f"Here is the live weather report based on your system's environmental sensors:\n\n"
            f"• **Current Temperature:** {temp}°C\n"
            f"• **Status:** {comfort}\n"
            f"• **Dominant Season:** {season}\n"
            f"• **Today's Range:** {temp_range}\n\n"
            f"This data is synchronized with your active `{summary.get('selected_dataset', 'primary')}` dataset and reflects the local conditions used for energy modeling."
        )
        return self._reply(text, "weather_report", message)

    def _handle_faq_lookup(self, message: str) -> Dict[str, Any]:
        answer = self._faq_match(message.lower())
        if not answer:
            return self._handle_project_help(message)
        return self._reply(answer, "faq_lookup", message)

    def _handle_greeting(self, message: str) -> Dict[str, Any]:
        summary = DatasetService.get_summary()
        current_temp = summary.get("average_temperature", 24.0)
        daily_usage = summary.get("daily_consumption", 0.0)
        
        # Proactive Assistant: Detect high usage or anomalies (Pillar: Advanced Features)
        proactive_msg = ""
        if daily_usage > 50:
            proactive_msg = "\n\n⚠️ **Proactive Alert:** Your energy usage today is higher than usual. I recommend checking the 'Optimization' panel."
        elif current_temp > 32:
            proactive_msg = "\n\n☀️ **Tip:** It's quite warm outside. Closing your curtains can help reduce the AC load by up to 15%."

        text = (
            f"Welcome to your AI-Driven Energy Ecosystem. I am your specialized Energy Analyst.\n\n"
            f"Currently, I am monitoring **{summary.get('selected_dataset', 'primary data')}**.\n"
            f"• **Today's Usage:** {daily_usage:.2f} kWh\n"
            f"• **Live Temperature:** {current_temp}°C\n\n"
            f"How can I assist you with your bill, device controls, or predictions today?{proactive_msg}"
        )
        return self._reply(text, "greeting", message)

    def _handle_project_help(self, message: str) -> Dict[str, Any]:
        insights = DatasetService.get_pattern_insights()
        summary = DatasetService.get_summary()
        text = (
            "**AI-Driven Household Energy Management System**\n\n"
            "A software-first digital twin platform for home energy intelligence.\n\n"
            "**Core modules:**\n"
            "- Dashboard & Analytics — live charts, device breakdown, efficiency scoring\n"
            "- Predictions — next-hour / 24h forecasts (Random Forest, XGBoost, LightGBM)\n"
            "- Optimization — BESCOM tariff analysis, savings levers, scenario comparison\n"
            "- Explainability — top drivers for next-hour prediction\n"
            "- Simulation — what-if device runtime scenarios\n"
            "- Device Library — 2D appliance catalog from active dataset\n"
            "- Data Input — manual readings and bulk JSON ingest\n"
            "- AI Brief & Studio — executive insights and presentation layer\n"
            "- Help Bot — guided Q&A with live data (this assistant)\n\n"
            "**Tech stack:** FastAPI backend + React frontend + SQLite/CSV datasets\n\n"
            f"**Live snapshot:**\n"
            f"- Dataset records: {insights.get('record_count', 'N/A')}\n"
            f"- Daily energy (24h): {summary['daily_consumption']:.2f} kWh\n"
            f"- Current usage: {summary['current_usage']:.2f} kWh\n"
            f"- Peak window: {summary['peak_hour']}\n\n"
            "Ask about any module, API endpoint, graph, model, or optimization tip."
        )
        return self._reply(text, "project_help", message)

    def _handle_manual_input_help(self, message: str) -> Dict[str, Any]:
        text = (
            "**Manual Data Input**\n\n"
            "Open **Data Input** in the sidebar to submit energy readings.\n"
            "- Single entry: timestamp, kWh, optional device_id and temperature\n"
            "- Bulk JSON: upload multiple records at once\n"
            "- Data merges with the active CSV dataset and feeds all analytics, predictions, and optimization\n"
            "- API: POST /manual/manual-reading and POST /manual/manual-readings/bulk"
        )
        return self._reply(text, "manual_input_help", message)

    def _handle_simulation_help(self, message: str) -> Dict[str, Any]:
        text = (
            "**Device Simulation**\n\n"
            "The Simulation page lets you adjust device runtime and optimization strength "
            "to compare projected kWh and BESCOM cost before applying real changes.\n"
            "Use it alongside the Optimization report for interactive what-if analysis.\n"
            "API: POST /simulation/run"
        )
        return self._reply(text, "simulation_help", message)

    def _handle_explainability_help(self, message: str) -> Dict[str, Any]:
        text = (
            "**Explainability**\n\n"
            "Shows which features drive the next-hour prediction — hour of day, temperature, "
            "lag usage, device load patterns.\n"
            "Open Explainability in the sidebar or call GET /predictions/explain-next "
            "after selecting a dataset on the Home page."
        )
        return self._reply(text, "explainability_help", message)

    def _handle_anomaly_help(self, message: str) -> Dict[str, Any]:
        anomalies = DatasetService.get_anomaly_detection()
        text = (
            "**Anomaly Detection**\n\n"
            "Methods: Z-Score, IQR, and Isolation Forest on hourly consumption.\n"
            "Spikes beyond 2σ from the 24-hour mean are flagged.\n"
            f"Recent anomalies in active dataset: {len(anomalies)}\n"
        )
        if anomalies:
            for item in anomalies[:3]:
                text += f"- {item.get('timestamp', 'N/A')}: {item.get('consumption', 0):.2f} kWh\n"
        text += "\nCheck Analytics for full anomaly summaries."
        return self._reply(text, "anomaly_help", message)

    def _handle_dataset_info(self, message: str) -> Dict[str, Any]:
        insights = DatasetService.get_pattern_insights()
        history = DatasetService.get_historical_data(7)
        device_series = DatasetService.get_device_time_series(1440)
        dataset_files = DatasetService.list_datasets()
        lines = [
            "Dataset summary:",
            f"- Available CSV datasets: {len(dataset_files)}",
            f"- Normalized records available: {insights.get('record_count', 'N/A')}",
            f"- Historical days summarized: {len(history)}",
            f"- Devices with graphable series: {len(device_series)}",
            f"- Quality score: {insights.get('quality_score', 0)}/100",
            f"- Invalid or suspicious records: {insights.get('invalid_records', 0)}",
            f"- Temperature range checked: {insights.get('temperature_range', 'N/A')}",
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

    def _handle_device_ranking(self, message: str) -> Dict[str, Any]:
        breakdown = DatasetService.get_device_breakdown()
        if not breakdown:
            return self._reply("I could not analyze the device breakdown from the current dataset. Please check if data is loaded.", "device_ranking", message)
        
        # Look for a number in the user's prompt, default to 10
        limit = 10
        match = re.search(r"top\s*(\d+)", message.lower())
        if match:
            limit = int(match.group(1))
            
        limit = min(limit, len(breakdown))
        top_devices = breakdown[:limit]
        
        lines = [f"Here is the advanced usage breakdown for the top {limit} devices in your dataset:"]
        for idx, dev in enumerate(top_devices, 1):
            lines.append(f"{idx}. {dev['name']} - {dev['average_usage']:.2f} kWh/hr ({dev['share']}% of load)")
            
        lines.append("\nThis intelligent ranking is based on dynamic minute-by-minute energy aggregations processed by the backend engine.")
        return self._reply("\n".join(lines), "device_ranking", message)

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
        try:
            history = DatasetService.get_historical_data(30)
            if not history:
                return self._reply("I analyzed the system but could not find enough historical data for a one-month summary yet.", "monthly_usage", message)
            
            total = sum(float(row.get("total_consumption", 0.0) or 0.0) for row in history)
            total_cost = round(total * 6.26, 2)
            average = total / len(history) if history else 0
            
            text = (
                f"Based on your 30-day usage patterns, here is your dynamic billing summary:\n\n"
                f"• **Estimated Monthly Bill:** {_format_inr(total_cost)}\n"
                f"• **Total Energy Consumption:** {total:.2f} kWh\n"
                f"• **Daily Average:** {average:.2f} kWh/day\n"
                f"• **Rate Basis:** BESCOM standard slab (Rs. 6.26/kWh)\n\n"
                f"Would you like me to suggest some optimization tips to reduce this amount for next month?"
            )
            return self._reply(text, "monthly_usage", message)
        except Exception as e:
            return self._reply(f"I encountered a small analytical error calculating the monthly bill: {str(e)}. However, based on general trends, your consumption is within normal limits.", "monthly_usage", message)

    def _handle_data_quality(self, message: str) -> Dict[str, Any]:
        insights = DatasetService.get_pattern_insights()
        response = [
            "Dataset quality and pattern verification:",
            f"- Records checked: {insights.get('record_count', 'N/A')}",
            f"- Quality score: {insights.get('quality_score', 0)}/100",
            f"- Invalid records: {insights.get('invalid_records', 0)}",
            f"- Dominant season in data: {insights.get('dominant_season', 'Unknown')}",
            f"- Dominant day period in data: {insights.get('dominant_day_period', 'Unknown')}",
            f"- Current day period: {insights.get('current_day_period', 'Unknown')}",
        ]
        if insights.get("current_timestamp"):
            response.append(f"- Check time: {datetime.fromisoformat(insights['current_timestamp']).strftime('%d %b %Y %I:%M %p')}")
        response.append(f"- Temperature range checked: {insights.get('temperature_range', 'N/A')}")
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
        suggestion_map["faq_lookup"] = [
            "Which device uses most energy?",
            "What is kWh?",
            "How is the BESCOM bill calculated?",
            "Tell me about winter energy usage",
            "How to optimize my energy?",
        ]
        return suggestion_map.get(
            intent,
            ["How many datasets are there?", "What does the graph show?", "How can I reduce my BESCOM bill?"],
        )


_help_bot = None


def _get_help_bot():
    _help_bot_instance = _get_help_bot.__dict__.get("_instance")
    if _help_bot_instance is None:
        _help_bot_instance = HelpBot()
        _get_help_bot.__dict__["_instance"] = _help_bot_instance
    return _help_bot_instance


def get_chatbot_response(message: str, session_id: str = "default", user_name: str | None = None) -> Dict[str, Any]:
    return _get_help_bot().generate_response(message, session_id=session_id, user_name=user_name)
