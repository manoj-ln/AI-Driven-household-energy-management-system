import React, { useEffect, useMemo, useState } from "react";
import { getForecast, getNextHourPrediction, getPredictionAnomalies, formatINR } from "../services/apiService";
import ModelSelector from "../components/ModelSelector";
import Chart from "../components/Dashboard/Chart";

const HORIZON_OPTIONS = [6, 12, 24, 48];
const ANOMALY_METHODS = [
  { value: "zscore", label: "Z-Score" },
  { value: "iqr", label: "IQR" },
  { value: "isolation_forest", label: "Isolation Forest" },
];

function StatTile({ title, value, accent = "#0f4c81", subtitle }) {
  return (
    <div
      className="card"
      style={{
        borderRadius: "18px",
        background: "linear-gradient(180deg, #ffffff 0%, #f6fbff 100%)",
        border: "1px solid rgba(15,76,129,0.08)",
      }}
    >
      <div style={{ color: "#5d6778", marginBottom: "8px", fontSize: "0.92rem" }}>{title}</div>
      <div style={{ color: accent, fontWeight: 800, fontSize: "1.65rem", marginBottom: "6px" }}>{value}</div>
      <div style={{ color: "#5d6778", lineHeight: 1.55 }}>{subtitle}</div>
    </div>
  );
}

function Predictions() {
  const [prediction, setPrediction] = useState(null);
  const [anomalies, setAnomalies] = useState([]);
  const [anomalySummary, setAnomalySummary] = useState(null);
  const [forecast, setForecast] = useState([]);
  const [forecastHours, setForecastHours] = useState(24);
  const [anomalyMethod, setAnomalyMethod] = useState("zscore");

  const fetchPrediction = async () => {
    const data = await getNextHourPrediction();
    setPrediction(data?.prediction || null);
    setAnomalies(data?.anomalies || []);
    setAnomalySummary(data?.anomaly_summary || null);
  };

  const fetchForecast = async (hours) => {
    const data = await getForecast(hours);
    setForecast(data || []);
  };

  const fetchAnomalies = async (method) => {
    const data = await getPredictionAnomalies(method);
    setAnomalies(data || []);
  };

  useEffect(() => {
    fetchPrediction();
    fetchForecast(forecastHours);
  }, []);

  useEffect(() => {
    fetchForecast(forecastHours);
  }, [forecastHours]);

  useEffect(() => {
    fetchAnomalies(anomalyMethod);
  }, [anomalyMethod]);

  const forecastLabels = useMemo(
    () =>
      forecast.map((point) =>
        new Date(point.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      ),
    [forecast]
  );

  const forecastValues = useMemo(() => forecast.map((point) => point.energy_kwh), [forecast]);

  const forecastInsights = useMemo(() => {
    if (!forecast.length) {
      return {
        total: 0,
        average: 0,
        peak: 0,
        peakLabel: "N/A",
      };
    }
    const total = forecast.reduce((sum, point) => sum + Number(point.energy_kwh || 0), 0);
    const average = total / forecast.length;
    const peakPoint = forecast.reduce((best, point) =>
      Number(point.energy_kwh || 0) > Number(best.energy_kwh || 0) ? point : best
    );
    return {
      total: total.toFixed(2),
      average: average.toFixed(2),
      peak: Number(peakPoint.energy_kwh || 0).toFixed(2),
      peakLabel: new Date(peakPoint.timestamp).toLocaleString(),
    };
  }, [forecast]);

  const anomalyTone = anomalySummary?.status === "attention_needed" ? "#b42318" : "#166534";

  return (
    <section style={{ marginBottom: "38px" }}>
      <div
        style={{
          padding: "28px",
          borderRadius: "24px",
          background: "linear-gradient(135deg, rgba(9,32,55,0.97) 0%, rgba(15,76,129,0.94) 54%, rgba(26,116,184,0.9) 100%)",
          color: "white",
          boxShadow: "0 20px 48px rgba(9,32,55,0.22)",
          marginBottom: "22px",
        }}
      >
        <p style={{ margin: "0 0 10px 0", letterSpacing: "0.16em", textTransform: "uppercase", opacity: 0.78 }}>
          Forecast Workspace
        </p>
        <h2 style={{ margin: "0 0 8px 0", fontSize: "2.2rem" }}>Advanced Predictions</h2>
        <p style={{ margin: 0, maxWidth: "820px", lineHeight: 1.7, opacity: 0.92 }}>
          A richer prediction layer for your project. Compare model behavior, inspect forecast shape over time, review anomaly signals,
          and explain cost impact in one place.
        </p>
      </div>

      <ModelSelector
        onModelChanged={() => {
          fetchPrediction();
          fetchForecast(forecastHours);
        }}
      />

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px", marginBottom: "20px" }}>
        <StatTile
          title="Next Hour Forecast"
          value={prediction ? `${prediction.energy_kwh} kWh` : "Loading..."}
          accent="#0f4c81"
          subtitle="The immediate prediction from the currently selected ML model."
        />
        <StatTile
          title="Confidence"
          value={prediction ? `${(prediction.confidence * 100).toFixed(1)}%` : "Loading..."}
          accent="#166534"
          subtitle={prediction ? `${prediction.confidence_label} confidence with ${prediction.trend.toLowerCase()} movement.` : "Waiting for forecast confidence."}
        />
        <StatTile
          title="Estimated Cost"
          value={prediction ? formatINR(prediction.estimated_cost_inr || 0) : "Loading..."}
          accent="#b45309"
          subtitle="Projected rupee impact for the next forecasted hour."
        />
        <StatTile
          title="Alert Status"
          value={anomalySummary ? anomalySummary.status : "Loading..."}
          accent={anomalyTone}
          subtitle={anomalySummary ? `${anomalySummary.total_anomalies} anomaly signals in the recent analysis window.` : "Waiting for anomaly scan."}
        />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 0.8fr", gap: "20px", marginBottom: "20px" }}>
        <div className="card" style={{ borderRadius: "20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "12px", flexWrap: "wrap", marginBottom: "12px" }}>
            <div>
              <h3 style={{ marginBottom: "6px" }}>Forecast Horizon</h3>
              <p style={{ margin: 0, color: "#5d6778" }}>
                Extend the projection window to study forecast shape, cost pressure, and peak moments.
              </p>
            </div>
            <select
              className="form-input"
              style={{ width: "160px" }}
              value={forecastHours}
              onChange={(event) => setForecastHours(Number(event.target.value))}
            >
              {HORIZON_OPTIONS.map((hours) => (
                <option key={hours} value={hours}>
                  {hours} Hours
                </option>
              ))}
            </select>
          </div>
          <Chart
            labels={forecastLabels}
            values={forecastValues}
            datasetLabel={`Forecast (${forecastHours}h)`}
            borderColor="#0f4c81"
            backgroundColor="rgba(15, 76, 129, 0.18)"
            chartType="line"
          />
          <p style={{ marginTop: "12px", color: "#5d6778" }}>
            X-axis shows the forecast timeline and Y-axis shows predicted energy in kWh. The highest point is the forecasted peak-demand moment.
          </p>
        </div>

        <div className="card" style={{ borderRadius: "20px", background: "linear-gradient(180deg, #ffffff 0%, #f7fbff 100%)" }}>
          <h3 style={{ marginBottom: "10px" }}>Forecast Insights</h3>
          <p>Total forecast energy: <strong>{forecastInsights.total} kWh</strong></p>
          <p>Average forecast per step: <strong>{forecastInsights.average} kWh</strong></p>
          <p>Peak forecast value: <strong>{forecastInsights.peak} kWh</strong></p>
          <p>Peak forecast time: <strong>{forecastInsights.peakLabel}</strong></p>
          <div style={{ marginTop: "16px", padding: "14px", borderRadius: "14px", background: "#eef6ff" }}>
            <h4 style={{ marginTop: 0, marginBottom: "8px", color: "#0f4c81" }}>Prediction Notes</h4>
            <p style={{ margin: "0 0 6px", color: "#4d5a6d" }}>
              Confidence reflects the selected model plus recent data support.
            </p>
            <p style={{ margin: 0, color: "#4d5a6d" }}>
              Model switching refreshes both the next-hour forecast and the horizon chart so you can compare ML behavior live.
            </p>
          </div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "0.9fr 1.1fr", gap: "20px" }}>
        <div className="card" style={{ borderRadius: "20px" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "12px", flexWrap: "wrap", marginBottom: "14px" }}>
            <div>
              <h3 style={{ marginBottom: "6px" }}>Anomaly Review</h3>
              <p style={{ margin: 0, color: "#5d6778" }}>
                Review abnormal usage signals with different detection methods.
              </p>
            </div>
            <select
              className="form-input"
              style={{ width: "180px" }}
              value={anomalyMethod}
              onChange={(event) => setAnomalyMethod(event.target.value)}
            >
              {ANOMALY_METHODS.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
          </div>

          {anomalySummary ? (
            <div style={{ marginBottom: "14px", padding: "14px", borderRadius: "14px", background: anomalySummary.status === "attention_needed" ? "#fff5f5" : "#effaf3" }}>
              <p style={{ margin: "0 0 6px" }}>Records checked: <strong>{anomalySummary.records_checked}</strong></p>
              <p style={{ margin: "0 0 6px" }}>Status: <strong>{anomalySummary.status}</strong></p>
              <p style={{ margin: "0 0 6px" }}>Anomalies found: <strong>{anomalySummary.total_anomalies}</strong></p>
              <p style={{ margin: 0 }}>Highest spike: <strong>{anomalySummary.highest_spike_kwh} kWh</strong></p>
            </div>
          ) : null}

          {anomalies.length === 0 ? (
            <p style={{ margin: 0 }}>No anomalies detected in the recent usage window.</p>
          ) : (
            <div style={{ display: "grid", gap: "10px" }}>
              {anomalies.map((item, index) => (
                <div
                  key={`${item.timestamp}-${index}`}
                  style={{
                    padding: "12px",
                    borderRadius: "14px",
                    background: item.type === "high" ? "#fff7f7" : "#f7fbff",
                    border: `1px solid ${item.type === "high" ? "#f3d7d7" : "#d8e6f7"}`,
                  }}
                >
                  <strong>{item.details}</strong>
                  <div style={{ marginTop: "6px", color: "#5d6778" }}>Time: {item.timestamp}</div>
                  <div style={{ color: "#5d6778" }}>Energy: {item.energy_kwh} kWh</div>
                  <div style={{ color: "#5d6778" }}>Method: {item.method}</div>
                  <div style={{ color: "#5d6778" }}>Severity: {item.severity}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card" style={{ borderRadius: "20px", background: "linear-gradient(180deg, #ffffff 0%, #f8fbff 100%)" }}>
          <h3 style={{ marginBottom: "10px" }}>Prediction Strategy Layer</h3>
          <div style={{ display: "grid", gap: "12px" }}>
            <div style={{ padding: "14px", borderRadius: "14px", background: "#f1f7ff" }}>
              <strong>Operational Insight</strong>
              <div style={{ marginTop: "6px", color: "#5d6778" }}>
                Use the forecast horizon chart to explain when energy demand is expected to rise and how that will affect the rupee cost.
              </div>
            </div>
            <div style={{ padding: "14px", borderRadius: "14px", background: "#fff8ec" }}>
              <strong>Model Comparison Insight</strong>
              <div style={{ marginTop: "6px", color: "#5d6778" }}>
                The model selector above is no longer only a toggle. It acts like a live comparison tool because preview values, confidence, and charts update around it.
              </div>
            </div>
            <div style={{ padding: "14px", borderRadius: "14px", background: "#effaf3" }}>
              <strong>Risk Insight</strong>
              <div style={{ marginTop: "6px", color: "#5d6778" }}>
                The anomaly review helps you explain unusual spikes or drops before they distort the forecasting story.
              </div>
            </div>
            <div style={{ padding: "14px", borderRadius: "14px", background: "#fff5fb" }}>
              <strong>Presentation Value</strong>
              <div style={{ marginTop: "6px", color: "#5d6778" }}>
                This page now supports live explanation during demo, viva, and report presentation by combining forecasting, anomaly analysis, and model transparency.
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default Predictions;
