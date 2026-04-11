# Output Steps

## Project Run

### Backend
```powershell
cd C:\myproject\backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Frontend
```powershell
cd C:\myproject\frontend
npm.cmd start
```

## Open in Browser

- Frontend: `http://127.0.0.1:3000`
- Backend docs: `http://127.0.0.1:8000/docs`

## Main Project Output Areas

- Dashboard: usage summary, live and saved graphs
- Analytics: device graphs, pattern insights, historical usage
- Predictions: model selection and next-hour forecast
- Simulation: advanced scenario planning and savings comparison
- Optimization: BESCOM-based cost analysis and savings levers
- Device Control: add, edit, delete, and toggle devices
- Manual Home Usage Input: appliance-based daily usage entry
- Help Bot: project questions, graph explanation, dataset details, and predictions

## Notes

- Currency is shown in INR.
- The project is configured for software-based home energy monitoring and planning.
- If the frontend shows old data, restart the backend and frontend once.
