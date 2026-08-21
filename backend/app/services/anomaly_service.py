import numpy as np
from sklearn.ensemble import IsolationForest

from app.services.dataset_service import DatasetService


class AnomalyService:
    @staticmethod
    def detect(method: str = "zscore") -> list[dict[str, object]]:
        records = DatasetService.get_recent_data(72)
        if len(records) < 12:
            return []

        values = [AnomalyService._value_to_kwh(record) for record in records]
        if not any(values):
            return []

        if method == "zscore":
            anomalies = AnomalyService._zscore_anomaly(values, records)
        elif method == "iqr":
            anomalies = AnomalyService._iqr_anomaly(values, records)
        elif method == "isolation_forest":
            anomalies = AnomalyService._isolation_forest_anomaly(values, records)
        else:
            anomalies = AnomalyService._zscore_anomaly(values, records)

        anomalies = sorted(anomalies, key=lambda item: item.get("severity", 0), reverse=True)
        return anomalies[:6]

    @staticmethod
    def summary() -> dict[str, object]:
        recent = DatasetService.get_recent_data(72)
        if len(recent) < 12:
            return {
                "status": "limited_data",
                "records_checked": len(recent),
                "total_anomalies": 0,
                "highest_spike_kwh": 0.0,
                "latest_alert": None,
            }

        anomalies = AnomalyService.detect("zscore")
        highest_spike = max((float(item.get("energy_kwh", 0.0)) for item in anomalies), default=0.0)
        return {
            "status": "ok" if not anomalies else "attention_needed",
            "records_checked": len(recent),
            "total_anomalies": len(anomalies),
            "highest_spike_kwh": round(highest_spike, 3),
            "latest_alert": anomalies[0] if anomalies else None,
        }

    @staticmethod
    def _value_to_kwh(record):
        if "energy_kwh" in record:
            return float(record["energy_kwh"])
        if "total_consumption" in record:
            return float(record["total_consumption"])
        if "energy_consumption" in record:
            return float(record["energy_consumption"])
        if "power" in record:
            return float(record["power"]) / 1000.0
        return 0.0

    @staticmethod
    def _zscore_anomaly(values, records, threshold=2.2):
        mean = np.mean(values)
        std = np.std(values)
        if std == 0:
            return []

        anomalies = []
        for value, record in zip(values, records):
            z_score = abs((value - mean) / std)
            if z_score > threshold:
                anomalies.append({
                    "timestamp": record["timestamp"].isoformat() if hasattr(record["timestamp"], "isoformat") else record["timestamp"],
                    "details": f"Usage deviated from the recent pattern (Z-score {z_score:.2f})",
                    "energy_kwh": round(float(value), 3),
                    "method": "zscore",
                    "severity": round(float(z_score), 2),
                    "type": "high" if value > mean else "low",
                })
        return anomalies

    @staticmethod
    def _iqr_anomaly(values, records, multiplier=1.5):
        q1 = np.percentile(values, 25)
        q3 = np.percentile(values, 75)
        iqr = q3 - q1
        lower_bound = q1 - multiplier * iqr
        upper_bound = q3 + multiplier * iqr

        anomalies = []
        for value, record in zip(values, records):
            if value < lower_bound or value > upper_bound:
                distance = max(lower_bound - value, value - upper_bound, 0.0)
                anomalies.append({
                    "timestamp": record["timestamp"].isoformat() if hasattr(record["timestamp"], "isoformat") else record["timestamp"],
                    "details": f"Usage fell outside the interquartile range [{lower_bound:.3f}, {upper_bound:.3f}]",
                    "energy_kwh": round(float(value), 3),
                    "method": "iqr",
                    "severity": round(float(distance), 3),
                    "type": "high" if value > upper_bound else "low",
                })
        return anomalies

    @staticmethod
    def _isolation_forest_anomaly(values, records, contamination=0.12):
        if len(values) < 10:
            return []

        x_values = np.array(values).reshape(-1, 1)
        clf = IsolationForest(contamination=contamination, random_state=42)
        clf.fit(x_values)
        predictions = clf.predict(x_values)
        scores = clf.decision_function(x_values)

        anomalies = []
        for pred, score, value, record in zip(predictions, scores, values, records):
            if pred == -1:
                anomalies.append({
                    "timestamp": record["timestamp"].isoformat() if hasattr(record["timestamp"], "isoformat") else record["timestamp"],
                    "details": "Usage pattern differs strongly from the recent baseline",
                    "energy_kwh": round(float(value), 3),
                    "method": "isolation_forest",
                    "severity": round(abs(float(score)), 3),
                    "type": "high",
                })
        return anomalies
