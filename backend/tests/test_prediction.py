from app.services.prediction_service import PredictionService
from app.services.anomaly_service import AnomalyService
from app.services.optimization_service import OptimizationService


def test_predict_next_hour():
    prediction = PredictionService.predict_next_hour()
    assert isinstance(prediction, dict)
    assert "energy_kwh" in prediction


def test_prediction_explainability_service():
    explainability = PredictionService.explain_next_hour_prediction()
    assert "prediction" in explainability
    assert "top_factors" in explainability
    assert isinstance(explainability["top_factors"], list)


def test_anomaly_summary_service():
    summary = AnomalyService.summary()
    assert "status" in summary
    assert "total_anomalies" in summary
    assert "records_checked" in summary


def test_optimization_report_service():
    report = OptimizationService.get_report()
    assert "estimated_savings" in report
    assert "scenario_comparison" in report
    assert "annual_projection" in report
