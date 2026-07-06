from pydantic import BaseModel

class PredictionSchema(BaseModel):
    energy_kwh: float
    confidence: float
    model: str
