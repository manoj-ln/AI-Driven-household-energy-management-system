"""
Curated project-level FAQ entries for the Help Bot.
Appended to the main FAQ database on startup when empty.
"""

PROJECT_FAQ = [
    (
        [
            "what is kwh",
            "what is a kilowatt hour",
            "explain kwh",
            "unit of energy",
        ],
        "kWh (kilowatt-hour) is the standard unit for household electricity consumption. "
        "One kWh means one kilowatt of power used continuously for one hour. "
        "Your dashboard graphs, predictions, and BESCOM cost estimates in this project are all expressed in kWh.",
    ),
    (
        [
            "what is this project",
            "explain this project",
            "project overview",
            "what does smart ai do",
            "household energy management system",
        ],
        "This is an AI-Driven Household Energy Management System — a software-first digital twin platform. "
        "It ingests energy readings (manual input or CSV datasets), shows analytics dashboards, forecasts next-hour usage "
        "with Random Forest / XGBoost / LightGBM, detects anomalies, explains predictions, optimizes BESCOM costs, "
        "simulates device scenarios, and provides a Help Bot for guided Q&A. "
        "Backend: FastAPI. Frontend: React dashboard.",
    ),
    (
        [
            "tech stack",
            "architecture",
            "fastapi react",
            "how is the project built",
        ],
        "Architecture: modular service-oriented FastAPI backend (routes + services) with a React frontend. "
        "Key backend modules: prediction_service, dataset_service, optimization_service, anomaly detection, auth, chatbot. "
        "Data layer: SQLite + selectable CSV benchmark datasets (3-year hourly history). "
        "Models: random_forest, xgboost, lightgbm with tracked R² metrics.",
    ),
    (
        [
            "which device uses most energy",
            "top device contributors",
            "highest consumption device",
            "biggest energy user",
        ],
        "Open Dashboard or Analytics and check 'Top Device Contributors' — devices are ranked by average kWh and share %. "
        "You can also ask me 'top 5 devices' for a live ranking from the active dataset.",
    ),
    (
        [
            "winter energy usage",
            "tell me about winter energy",
            "heating season energy",
        ],
        "Winter profiles typically show higher heater/HVAC load and longer evening peaks. "
        "This project includes seasonal pattern analysis in dataset insights (dominant season). "
        "Use Optimization to shift heating to off-peak windows and Simulation to compare winter scenarios.",
    ),
    (
        [
            "explainability",
            "explain prediction",
            "feature importance",
            "shap drivers",
            "why this prediction",
        ],
        "The Explainability page shows top drivers for the next-hour prediction — which features (hour, temperature, lag usage, device load) "
        "most influence the forecast. Use GET /predictions/explain-next or open Explainability in the sidebar after selecting a dataset.",
    ),
    (
        [
            "anomaly detection",
            "anomalies",
            "unusual usage",
            "outlier detection",
        ],
        "Anomaly detection uses Z-Score, IQR, and Isolation Forest methods on hourly consumption. "
        "Spikes beyond 2 standard deviations from the 24-hour mean are flagged. "
        "Check Analytics for anomaly summaries tied to your active dataset.",
    ),
    (
        [
            "manual input",
            "data input",
            "how to add readings",
            "energy ingest",
        ],
        "Use the Data Input page to submit manual energy entries or bulk JSON readings. "
        "These merge with CSV dataset mode and feed the same analytics, prediction, and optimization pipeline.",
    ),
    (
        [
            "optimization page",
            "cost optimization",
            "how to optimize energy",
            "reduce bescom bill",
            "save on electricity",
        ],
        "The Optimization page shows peak/off-peak tariff analysis, device-level savings opportunities, "
        "monthly/annual BESCOM projections, scenario comparison, and an action plan. "
        "Ask me 'cost optimization summary' for live numbers from your dataset.",
    ),
    (
        [
            "simulation",
            "what if scenario",
            "device simulation",
        ],
        "Simulation lets you adjust device runtime and optimization strength to compare projected kWh and cost "
        "before applying changes. It complements the Optimization report with interactive what-if analysis.",
    ),
    (
        [
            "device library",
            "appliance library",
            "catalog devices",
        ],
        "Device Library lists all appliances in the active dataset catalog with 2D schematic cards — category, rated power, "
        "and description. Devices sync from GET /analytics/catalog based on CSV column metadata.",
    ),
    (
        [
            "predictions page",
            "forecast",
            "next hour prediction",
            "24 hour forecast",
        ],
        "Predictions provides next-hour and multi-step forecasts using the selected ML model. "
        "Switch between random_forest, xgboost, and lightgbm in the model selector; previews update automatically.",
    ),
    (
        [
            "analytics page",
            "analytics dashboard",
        ],
        "Analytics expands on the dashboard with historical trends, efficiency scoring, anomaly views, "
        "and device breakdown grids for deeper consumption analysis.",
    ),
    (
        [
            "intelligence hub",
            "ai brief",
            "executive brief",
        ],
        "AI Brief (Intelligence Hub) translates live energy data into decision-ready insights — readiness scoring, "
        "forecast briefing, and strategic recommendations for presentations.",
    ),
    (
        [
            "energy studio",
            "presentation layer",
            "studio page",
        ],
        "Energy Studio is the presentation layer: energy persona, efficiency grade, daily rhythm story, "
        "device share canvas, and viva-ready narrative notes.",
    ),
    (
        [
            "device control",
            "turn off device",
            "switch devices",
        ],
        "Device Control lets you toggle registered devices ON/OFF. OFF devices flatten in graphs. "
        "Status syncs through GET/POST /control endpoints.",
    ),
    (
        [
            "what does the graph show",
            "graph explanation",
            "usage graph",
            "x axis y axis",
        ],
        "The Usage Graph plots time (X-axis) vs energy in kWh (Y-axis). "
        "Higher points mean more consumption in that window. "
        "Switch between line, bar, and table views; use Live Second-wise mode for continuous demo streaming.",
    ),
    (
        [
            "how many datasets",
            "how many datasets are there",
            "dataset count",
        ],
        "Dataset count and file names come from GET /analytics/datasets. "
        "Select any CSV on the Home page — the same source drives dashboard, predictions, optimization, and graphs.",
    ),
    (
        [
            "list available datasets",
            "show dataset files",
            "csv files available",
        ],
        "Available datasets are listed on the Home page dropdown and via GET /analytics/datasets. "
        "Included benchmarks cover 3-year hourly history (2023–2025) with unified device columns.",
    ),
    (
        [
            "bescom bill calculation",
            "how is bill calculated",
            "tariff structure",
        ],
        "BESCOM-style billing in this project uses base energy rate (~Rs. 5.90/kWh) + surcharge (~Rs. 0.36/kWh), "
        "plus fixed charge per kW connected load. Optimization breaks down peak, off-peak, and shoulder energy costs.",
    ),
    (
        [
            "random forest xgboost lightgbm",
            "which model is best",
            "model comparison",
        ],
        "Baseline metrics: Random Forest R² 0.90, XGBoost 0.92, LightGBM 0.94. "
        "LightGBM is the strongest default; XGBoost handles high-variance short-term forecasts well. "
        "Switch models on the Predictions page.",
    ),
    (
        [
            "api endpoints",
            "rest api",
            "backend routes",
        ],
        "Key API routes: /health, /analytics/*, /predictions/*, /optimization/report, /simulation/*, "
        "/control/*, /manual/*, /chatbot/chat, /users/* for auth. Open http://localhost:8000/docs for full Swagger.",
    ),
]
