from fastapi import APIRouter
from app.services.prediction_service import PredictionService
from app.services.anomaly_service import AnomalyService

router = APIRouter()

@router.get("/next-hour", response_model=dict)
async def get_next_hour_prediction():
    prediction = PredictionService.predict_next_hour()
    anomalies = AnomalyService.detect()
    anomaly_summary = AnomalyService.summary()
    return {"prediction": prediction, "anomalies": anomalies, "anomaly_summary": anomaly_summary}

@router.get("/models", response_model=dict)
async def get_available_models():
    return PredictionService.get_available_models()

@router.post("/models/{model_name}", response_model=dict)
async def set_model(model_name: str):
    return PredictionService.set_model(model_name)

@router.get("/forecast/{hours}", response_model=list)
async def get_forecast(hours: int = 7):
    return PredictionService.predict_multi_step(hours)

@router.get("/anomalies/{method}", response_model=list)
async def get_anomalies(method: str = "zscore"):
    return AnomalyService.detect(method)


@router.get("/explain-next", response_model=dict)
async def get_prediction_explainability():
    return PredictionService.explain_next_hour_prediction()
