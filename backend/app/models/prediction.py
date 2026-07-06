from pydantic import BaseModel

class PredictionResult(BaseModel):
    energy_kwh: float
    confidence: float
    model: str
