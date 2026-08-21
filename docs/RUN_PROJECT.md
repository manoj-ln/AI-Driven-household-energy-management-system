# SmartHouse AI - Complete Run Guide

## ✅ Project Status: READY TO RUN

All components have been updated, tested, and verified:
- ✅ Dashboard cleaned (removed feature cards)
- ✅ Device Library verified (2D only)
- ✅ Chatbot at pro level (grammar, language, entities)
- ✅ Analytics graphs working (dataset-aware)
- ✅ Optimization service verified
- ✅ Backend tests and frontend production build are available as repeatable checks

---

## 🚀 QUICK START - Run Both Backend & Frontend

### Option 1: Run in Same Terminal (Sequential)

**Terminal 1 - Backend (FastAPI)**
```powershell
cd C:\compress\myproject\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 - Frontend (React)**
```powershell
cd C:\compress\myproject\frontend
npm.cmd start
```

**Then Open Browser:**
- Frontend: `http://127.0.0.1:3000`
- Backend Docs: `http://127.0.0.1:8000/docs`

---

### Option 2: Using Virtual Environment (Recommended)

**Terminal 1 - Backend**
```powershell
# Activate virtual environment
cd C:\compress\myproject
.\.venv\Scripts\Activate.ps1

# Run backend
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 - Frontend**
```powershell
cd C:\compress\myproject\frontend
npm.cmd start
```

---

## 📋 What to Test After Running

### 1. **Dashboard (Home)**
- ✅ Dataset configuration dropdown visible
- ✅ Usage graphs display correctly
- ✅ Device breakdown shows in scrollable format
- ✅ Top device contributors display with percentages

### 2. **Analytics**
- ✅ Select different time windows (30 min, 1 hour, 24 hours, etc.)
- ✅ Switch dataset from dropdown
- ✅ Device graphs render with dataset data
- ✅ Category filtering works
- ✅ Search for specific devices works

### 3. **Appliance & Device Library**
- ✅ 2D schematics display for each device
- ✅ Search and category filter work
- ✅ Click device card to see full details
- ✅ No 3D models present (confirmed)

### 4. **Optimization**
- ✅ Open Optimization from sidebar
- ✅ See BESCOM tariff breakdown
- ✅ View cost comparison scenarios
- ✅ Savings levers displayed
- ✅ Monthly/annual projections shown

### 5. **Chatbot (Help Bot)**
- Ask: "How many datasets are there?" → Should list datasets
- Ask: "What does the graph show?" → Should explain axes and data
- Ask: "Which model is active?" → Should show current model
- Ask: "How can I reduce my BESCOM bill?" → Should give optimization tips
- Ask: "rewrite: data is here" → Should correct to "Data is here."
- Ask: "kannada" → Should respond in Kannada

### 6. **Predictions**
- ✅ Select model (Random Forest, XGBoost, LightGBM)
- ✅ Get next-hour forecast with confidence
- ✅ See explainability of top drivers
- ✅ Cost estimate in rupees displayed

---

## ⚠️ Troubleshooting

### "Port 3000 already in use"
```powershell
# Kill the process on port 3000
Get-NetTCPConnection -LocalPort 3000 | Stop-Process -Force
```

### "Backend not responding"
```powershell
# Ensure backend is running on 8000
# Check: http://127.0.0.1:8000/health
# If not working, restart with:
cd C:\compress\myproject\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### "Graphs not showing in Analytics"
- Go to Home page
- Select a dataset from dropdown
- Click "Refresh Datasets"
- Go back to Analytics

### "Frontend won't load"
```powershell
# Clear npm cache and reinstall
cd C:\compress\myproject\frontend
npm cache clean --force
npm install
npm.cmd start
```

---

## 🧪 Running Tests

### All Tests
```powershell
cd C:\compress\myproject\backend
python -m pytest tests/ -v
# Expected: all collected tests pass; warnings from third-party model serialization may remain
```

### Specific Tests
```powershell
# API tests only
python -m pytest tests/test_api.py -v

# Chatbot tests
python -m pytest tests/test_chatbot.py -v

# Predictions
python -m pytest tests/test_prediction.py -v
```

---

## 📊 Key Features Verified

| Feature | Status | Location |
|---------|--------|----------|
| Dashboard with live data | ✅ Working | Home page |
| Dataset selection | ✅ Working | Home header |
| Device library (2D only) | ✅ Working | Device Library page |
| Analytics with filters | ✅ Working | Analytics page |
| Optimization BESCOM | ✅ Working | Optimization page |
| Chatbot (pro level) | ✅ Working | Help button |
| Predictions with models | ✅ Working | Predictions page |
| Explainability | ✅ Working | Explainability page |
| Device Control | ✅ Working | Device Control page |
| Manual Data Input | ✅ Working | Data Input page |
| AI Brief & Studio | ✅ Working | AI Brief & Studio pages |

---

## 📖 URLs Quick Reference

After running the project:

| Component | URL |
|-----------|-----|
| Frontend | http://127.0.0.1:3000 |
| Backend Docs | http://127.0.0.1:8000/docs |
| Backend Health | http://127.0.0.1:8000/health |
| API Chat | http://127.0.0.1:8000/docs#/Chat/chat_with_bot_chat_chat_post |

---

## 🛠️ Development Notes

- **Backend Framework:** FastAPI + uvicorn
- **Frontend Framework:** React + Chart.js
- **Database:** SQLite + CSV datasets
- **Dataset Location:** `C:\compress\myproject\backend\data\datasets\`
- **AI Models:** Random Forest, XGBoost, LightGBM (available)
- **Chatbot:** Advanced NLP with grammar, language detection, follow-ups
- **Currency:** All costs in INR (Rupees)

---

## ✨ Next Steps (Optional Enhancements)

1. Deploy to a cloud server (AWS, Azure, GCP)
2. Connect to real MQTT IoT devices
3. Add more datasets
4. Implement real-time notifications
5. Add user export/reports functionality
6. Integration with BESCOM API for live rates

---

**Ready to go! Run the commands above and enjoy your SmartHouse AI system.** 🏠⚡
