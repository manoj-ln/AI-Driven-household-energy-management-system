from app.services.prediction_service import PredictionService


def test_predict_next_hour():
    prediction = PredictionService.predict_next_hour()
    assert isinstance(prediction, dict)
    assert "energy_kwh" in prediction
