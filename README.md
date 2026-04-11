# AI-Driven Household Energy Management System

This repository contains a software-only energy management project with:

- FastAPI backend for energy data ingestion, prediction, anomaly detection, and chatbot support
- React dashboard frontend for monitoring, analytics, forecasts, and manual input
- SQLite persistence and mock/simulated data support for hardware-free demos
- Security-minded frontend API handling with a single backend base URL and safer input validation

## What Works

- Manual energy reading input with validation
- Bulk reading import from JSON
- Realistic simulated readings
- Continuous simulation
- Energy analytics and top-device summaries
- Next-hour prediction and multi-step forecast
- Help bot for usage, grammar, language, device status, and past-data summaries
- INR-based cost estimates in the UI
- Software-only device status views

## Hardware Removed

The app shell no longer depends on MQTT setup or any ESP32/broker workflow. The project now focuses on the software portion only.

## Project Structure

- `backend/`: FastAPI API server, database layer, services, routes, tests
- `frontend/`: React dashboard with charts, simulations, manual input, and chatbot UI
- `manual_input_cli.py`: interactive CLI for manual data entry and verification

## Run Locally

### Backend

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm start
```

### Manual Input CLI

```bash
python manual_input_cli.py
```

## Notes

- The backend now prefers real SQLite data when available and falls back to safe mock data only when needed.
- Cost outputs in the UI and help bot are shown in Indian rupees.
- The chatbot now supports device info, running-device checks, language help, grammar help, and past-data summaries.
