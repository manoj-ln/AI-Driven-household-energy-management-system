import React, { useEffect, useState } from "react";
import {
  getAnalyticsSummary,
  getDeviceBreakdown,
  getAnomalies,
  getDeviceTimeSeries,
  getDeviceTimeSeriesWindow,
  getPatternInsights,
} from "../services/apiService";
import EfficiencyScore from "../components/EfficiencyScore";
import Chart from "../components/Dashboard/Chart";

const TIME_OPTIONS = [
  { label: "Last 30 Minutes", value: 30, unit: "minutes" },
  { label: "Last 1 Hour", value: 60, unit: "minutes" },
  { label: "Last 3 Hours", value: 180, unit: "minutes" },
  { label: "Last 6 Hours", value: 6 },
  { label: "Last 12 Hours", value: 12 },
  { label: "Last 24 Hours", value: 24 },
  { label: "Last 48 Hours", value: 48 },
  { label: "Last 7 Days", value: 168 },
  { label: "Live", value: -1, unit: "live" },
];

const CHART_COLORS = [
  ["#0f4c81", "rgba(15, 76, 129, 0.18)"],
  ["#b45309", "rgba(180, 83, 9, 0.18)"],
  ["#166534", "rgba(22, 101, 52, 0.18)"],
  ["#9f1239", "rgba(159, 18, 57, 0.18)"],
  ["#4c1d95", "rgba(76, 29, 149, 0.18)"],
  ["#1d4ed8", "rgba(29, 78, 216, 0.18)"],
];

function Analytics() {
  const [summary, setSummary] = useState(null);
  const [breakdown, setBreakdown] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [deviceSeries, setDeviceSeries] = useState([]);
  const [selectedHours, setSelectedHours] = useState(24);
  const [loadingGraphs, setLoadingGraphs] = useState(true);
  const [patternInsights, setPatternInsights] = useState(null);
  const [liveTick, setLiveTick] = useState(0);

  useEffect(() => {
    async function loadAnalytics() {
      const [summaryData, breakdownData, anomaliesData, patternData] = await Promise.all([
        getAnalyticsSummary(),
        getDeviceBreakdown(),
        getAnomalies(),
        getPatternInsights(),
      ]);
      setSummary(summaryData || null);
      setBreakdown(breakdownData || []);
      setAnomalies(anomaliesData || []);
      setPatternInsights(patternData || null);
    }
    loadAnalytics();
  }, []);

  useEffect(() => {
    async function loadDeviceSeries() {
      setLoadingGraphs(true);
      let series = [];
      const selected = TIME_OPTIONS.find((option) => option.value === selectedHours);
      if (selected?.unit === "minutes") {
        series = await getDeviceTimeSeriesWindow(selected.value);
      } else if (selected?.unit === "live") {
        series = await getDeviceTimeSeriesWindow(30);
      } else {
        series = await getDeviceTimeSeries(selectedHours);
      }
      setDeviceSeries(series || []);
      setLoadingGraphs(false);
    }
    loadDeviceSeries();
  }, [selectedHours, liveTick]);

  useEffect(() => {
    if (selectedHours !== -1) {
      return undefined;
    }
    const interval = window.setInterval(() => setLiveTick((prev) => prev + 1), 5000);
    return () => window.clearInterval(interval);
  }, [selectedHours]);

  return (
    <section style={{ marginBottom: "38px" }}>
      <h2>Usage Patterns & Analytics</h2>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginBottom: "20px" }}>
        <div style={{ background: "white", padding: "20px", borderRadius: "12px" }}>
          <h3>Daily Summary</h3>
          {summary ? (
            <>
              <p>Average temperature: <strong>{summary.average_temperature}°C</strong></p>
              <p>Peak hour: <strong>{summary.peak_hour}</strong></p>
              <p>24h consumption: <strong>{summary.daily_consumption} kWh</strong></p>
            </>
          ) : (
            <p>Loading summary...</p>
          )}
        </div>
        <div style={{ background: "white", padding: "20px", borderRadius: "12px" }}>
          <h3>Anomaly Detection</h3>
          {anomalies.length ? (
            <ul style={{ paddingLeft: "20px" }}>
              {anomalies.slice(0, 5).map((anomaly, index) => (
                <li key={index} style={{ marginBottom: "10px" }}>
                  <strong>{anomaly.type.toUpperCase()}</strong> usage at {new Date(anomaly.timestamp).toLocaleTimeString()}
                  <br />
                  <small>Consumption: {anomaly.consumption} kWh, Deviation: {anomaly.deviation} kWh</small>
                </li>
              ))}
            </ul>
          ) : (
            <p>No anomalies detected in recent data.</p>
          )}
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px", marginBottom: "20px" }}>
        <div style={{ background: "white", padding: "20px", borderRadius: "16px" }}>
          <h3 style={{ marginBottom: "8px" }}>Quality Score</h3>
          <p style={{ fontSize: "1.7rem", fontWeight: 700, color: "#0f4c81", margin: 0 }}>
            {patternInsights ? `${patternInsights.quality_score}/100` : "Loading..."}
          </p>
        </div>
        <div style={{ background: "white", padding: "20px", borderRadius: "16px" }}>
          <h3 style={{ marginBottom: "8px" }}>Dominant Season</h3>
          <p style={{ fontSize: "1.2rem", fontWeight: 700, color: "#166534", margin: 0 }}>
            {patternInsights ? patternInsights.dominant_season : "Loading..."}
          </p>
        </div>
        <div style={{ background: "white", padding: "20px", borderRadius: "16px" }}>
          <h3 style={{ marginBottom: "8px" }}>Most Frequent Day Period In Data</h3>
          <p style={{ fontSize: "1.2rem", fontWeight: 700, color: "#b45309", margin: 0 }}>
            {patternInsights ? patternInsights.dominant_day_period : "Loading..."}
          </p>
        </div>
        <div style={{ background: "white", padding: "20px", borderRadius: "16px" }}>
          <h3 style={{ marginBottom: "8px" }}>Temperature Range</h3>
          <p style={{ fontSize: "1.1rem", fontWeight: 700, color: "#9f1239", margin: 0 }}>
            {patternInsights ? patternInsights.temperature_range : "Loading..."}
          </p>
        </div>
        <div style={{ background: "white", padding: "20px", borderRadius: "16px" }}>
          <h3 style={{ marginBottom: "8px" }}>Current Day Period</h3>
          <p style={{ fontSize: "1.1rem", fontWeight: 700, color: "#0f4c81", margin: 0 }}>
            {patternInsights ? patternInsights.current_day_period : "Loading..."}
          </p>
        </div>
      </div>

      {patternInsights ? (
        <div style={{ background: "white", padding: "20px", borderRadius: "16px", marginBottom: "20px" }}>
          <h3 style={{ marginBottom: "10px" }}>Pattern Verification</h3>
          <p style={{ color: "#5b6775" }}>
            Records checked: <strong>{patternInsights.record_count}</strong> | Invalid records: <strong>{patternInsights.invalid_records}</strong>
          </p>
          <p style={{ color: "#5b6775" }}>
            Current local data check time: <strong>{new Date(patternInsights.current_timestamp).toLocaleString()}</strong>
          </p>
          <ul style={{ paddingLeft: "18px", marginBottom: 0 }}>
            {patternInsights.notes.map((note) => (
              <li key={note} style={{ marginBottom: "8px" }}>{note}</li>
            ))}
          </ul>
        </div>
      ) : null}

      <EfficiencyScore />

      <div style={{ background: "white", padding: "20px", borderRadius: "12px", marginBottom: "20px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
          <div>
            <h3 style={{ marginBottom: "6px" }}>Device Graphs</h3>
            <p style={{ margin: 0, color: "#5b6775" }}>Choose a short or long window, including live mode, and view one graph for every device present in the home.</p>
          </div>
          <select
            value={selectedHours}
            onChange={(event) => setSelectedHours(Number(event.target.value))}
            className="form-input"
            style={{ maxWidth: "220px", cursor: "pointer" }}
          >
            {TIME_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {loadingGraphs ? (
        <div style={{ background: "white", padding: "20px", borderRadius: "12px" }}>
          Loading device graphs...
        </div>
      ) : deviceSeries.length ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "20px", marginBottom: "20px" }}>
          {deviceSeries.map((device, index) => {
            const [borderColor, backgroundColor] = CHART_COLORS[index % CHART_COLORS.length];
            return (
              <div key={device.device_name} style={{ background: "white", padding: "20px", borderRadius: "16px", boxShadow: "0 10px 24px rgba(15, 76, 129, 0.08)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: "12px", marginBottom: "12px" }}>
                  <h3 style={{ margin: 0 }}>{device.device_name}</h3>
                  <span style={{ color: borderColor, fontWeight: 700 }}>{device.total_energy_kwh} kWh</span>
                </div>
                <p style={{ marginTop: 0, color: "#5b6775" }}>
                  Share of selected time window: {device.share}% {selectedHours === -1 ? "| Refreshing every 5 seconds" : ""}
                </p>
                <Chart
                  labels={device.points.map((point) => point.label)}
                  values={device.points.map((point) => point.energy_kwh)}
                  datasetLabel={`${device.device_name} energy`}
                  borderColor={borderColor}
                  backgroundColor={backgroundColor}
                />
              </div>
            );
          })}
        </div>
      ) : (
        <div style={{ background: "white", padding: "20px", borderRadius: "12px", marginBottom: "20px" }}>
          No device graph data available yet. Add manual readings first and then choose a time window.
        </div>
      )}

      <div style={{ background: "white", padding: "20px", borderRadius: "12px" }}>
        <h3>Top Device Contributors</h3>
        {breakdown && breakdown.length ? (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "15px" }}>
            {breakdown.map((device) => (
              <div
                key={device.name}
                style={{
                  padding: "15px",
                  border: "1px solid #ddd",
                  borderRadius: "8px",
                  textAlign: "center",
                }}
              >
                <h4>{device.name}</h4>
                <p>Avg Usage: {device.average_usage} kWh</p>
                <p>Share: {device.share}%</p>
                <div
                  style={{
                    width: "100%",
                    height: "10px",
                    background: "#e9ecef",
                    borderRadius: "5px",
                    overflow: "hidden",
                  }}
                >
                  <div
                    style={{
                      width: `${device.share}%`,
                      height: "100%",
                      background: "#007bff",
                      transition: "width 0.3s",
                    }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p>Loading device breakdown...</p>
        )}
      </div>
    </section>
  );
}

export default Analytics;
