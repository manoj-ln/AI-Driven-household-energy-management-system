# AI-Driven Household Energy Management System for Consumption Analysis and Cost Optimization

This project delivers a software-first digital twin style platform for household energy intelligence.

- Backend: FastAPI modular service-oriented backend (prediction, anomaly detection, optimization, explainability, auth)
- Frontend: streamlined React dashboard for analytics, forecasts, explainability, simulations, and chatbot guidance
- Data layer: SQLite/manual input with fallback synthetic generation for hardware-free evaluation

## Core Features

- Secure user registration and login with hashed passwords and bearer token sessions
- Energy ingestion from manual entries and bulk JSON
- Next-hour and multi-step forecasting with model selection (`random_forest`, `xgboost`, `lightgbm`)
- Anomaly detection using Z-Score, IQR, and Isolation Forest
- Explainability screen showing top drivers for the next-hour prediction
- Cost optimization reports with INR tariff assumptions and scenario comparison
- Device-level simulation and consumption analytics dashboards

## Architecture

The implementation follows a **modular service-oriented backend** (single deployable service with separated domain modules), not distributed microservices.

- `backend/app/routes/`: API contracts by domain
- `backend/app/services/`: prediction, anomaly, optimization, simulation, dataset, auth logic
- `backend/app/database/`: storage access and persistence
- `frontend/src/pages/`: dashboard, analytics, predictions, explainability, optimization views

## Dataset Description

- Source mix:
  - real manual/device readings stored in local database/json store
  - generated fallback time series when historical data is sparse
  - selectable CSV benchmark datasets for controlled demos
- Core fields used:
  - `timestamp`
  - `energy_kwh` or `energy_consumption`
  - `device_id`
  - `temperature` (optional)
- Time granularity:
  - hourly aggregation for forecasting and optimization
  - fine-grained windowed series for device-level charts

### Included CSV Datasets

- `urban_family_weekday.csv`
- `weekend_peak_entertainment.csv`
- `solar_assisted_home.csv`
- `winter_heating_profile.csv`
- `student_hostel_shared_load.csv`

Use frontend dataset controls or API endpoints:
- `GET /analytics/datasets`
- `POST /analytics/datasets/select`
- `GET /analytics/dataset-mode`
- `POST /analytics/dataset-mode`

## Model Metrics (Current Baseline)

| Model | R2 (tracked / fallback) | MAE (kWh, baseline reference) | Notes |
|---|---:|---:|---|
| Random Forest | 0.90 | 0.16 | stable baseline performer |
| XGBoost | 0.92 | 0.14 | strong short-term forecast behavior |
| LightGBM | 0.94 | 0.13 | best default confidence profile |

## Reproducible Evaluation Steps

1. Install backend dependencies.
2. Train/evaluate models from `backend/models/training/`:
   - `python preprocess.py`
   - `python train.py`
   - `python evaluate.py`
3. Start backend API and confirm `/health`.
4. Query model endpoints:
   - `/predictions/models`
   - `/predictions/next-hour`
   - `/predictions/forecast/24`
   - `/predictions/explain-next`
5. Run backend tests:
   - `pytest`
6. Launch frontend and validate analytics/prediction/explainability flows.

## Testing Coverage

- API tests include:
  - health endpoint
  - prediction endpoint response contract
  - anomaly detection contract
  - optimization report contract
  - auth register/login/token flow
  - dataset listing and selection endpoints
- Service tests include:
  - prediction output structure
  - anomaly summary consistency
  - optimization projected savings fields
  - dataset mode and dataset file selection validation

See `backend/tests/` for executable test cases.

Latest local verification result: `13 passed` (backend `pytest`).

## CI and Deployment Readiness

- GitHub Actions workflow added at `.github/workflows/ci.yml`:
  - backend: install + `pytest`
  - frontend: install + production build
- Deployment hardening checklist added at `PRODUCTION_CHECKLIST.md`.

## Run Locally

### Backend (FastAPI)

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend (Streamlined React UI)

```bash
cd frontend
npm install
npm start
```

### Manual Input CLI

```bash
python manual_input_cli.py
```

## Documentation Note

Authentication is backend-based (hashed passwords + token sessions) with stronger input validation for identifier/password policies. This replaces earlier local-only demo credential storage.

## Bottom Line

This project is now aligned as an **AI-driven household energy digital twin style system** with clear explainability, practical optimization outputs, and reproducible FastAPI-backed evaluation/test workflows.
