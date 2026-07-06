import React, { useEffect, useState, useContext } from "react";
import { EnergyContext } from "../context/EnergyContext";
import {
  getAnalyticsSummary,
  getDeviceBreakdown,
  getAnomalies,
  getDeviceTimeSeries,
  getDeviceTimeSeriesWindow,
  getPatternInsights,
  getDatasets,
  selectDataset,
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
  const [availableDatasets, setAvailableDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState("");
  const [datasetMode, setDatasetMode] = useState("real_only");
  const { datasetState, refreshDatasetState } = useContext(EnergyContext);

  const loadAnalytics = async () => {
    const [summaryData, breakdownData, anomaliesData, patternData, datasetsData] = await Promise.all([
      getAnalyticsSummary(),
      getDeviceBreakdown(),
      getAnomalies(),
      getPatternInsights(),
      getDatasets(),
    ]);
    setSummary(summaryData || null);
    setBreakdown(breakdownData || []);
    setAnomalies(anomaliesData || []);
    setPatternInsights(patternData || null);
    setAvailableDatasets(datasetsData?.datasets || []);
    setSelectedDataset(datasetsData?.selected_dataset || "");
    setDatasetMode(datasetsData?.mode || "real_only");
  };

  useEffect(() => {
    // Ensure global dataset state is current and then load analytics
    (async () => {
      await refreshDatasetState();
      loadAnalytics();
    })();
  }, []);

  const handleDatasetChange = async (name) => {
    // Use global selection so other pages follow the same dataset
    await selectDataset(name);
    await refreshDatasetState();
    setSelectedDataset(name);
    loadAnalytics();
    setLiveTick((t) => t + 1);
  };

  // Keep local dataset selection in sync with global EnergyContext
  useEffect(() => {
    if (datasetState) {
      setAvailableDatasets(datasetState.datasets || []);
      setSelectedDataset(datasetState.selectedDataset || "");
      setDatasetMode(datasetState.mode || "real_only");
    }
  }, [datasetState]);

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

  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All");

  const filteredSeries = deviceSeries.filter((device) => {
    const matchesSearch = device.device_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === "All" || device.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const categories = ["All", ...new Set(deviceSeries.map((d) => d.category))];

  return (
    <section style={{ marginBottom: "38px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px", flexWrap: "wrap", gap: "12px" }}>
        <h2 style={{ margin: 0 }}>Usage Patterns & Analytics</h2>
        <div style={{ display: "flex", alignItems: "center", gap: "15px" }}>
          <div style={{ 
            padding: "4px 12px", 
            borderRadius: "6px", 
            fontSize: "0.75rem", 
            fontWeight: 800,
            background: datasetMode === "real_only" ? "#fee2e2" : "#dcfce7",
            color: datasetMode === "real_only" ? "#991b1b" : "#166534",
            border: `1px solid ${datasetMode === "real_only" ? "#fecaca" : "#bbf7d0"}`
          }}>
            {datasetMode === "real_only" ? "● LIVE DATA" : "● SIMULATION"}
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <span style={{ fontWeight: 600, color: "#5b6775" }}>Active Household:</span>
            <select 
              value={selectedDataset} 
              onChange={(e) => handleDatasetChange(e.target.value)}
              className="form-input"
              style={{ minWidth: "220px", background: "#f0f2f5", border: "none", fontWeight: 700 }}
            >
              {availableDatasets.map(ds => (
                <option key={ds} value={ds}>{ds.replace(".csv", "").replace("energy_dataset_", "").replace("_", " ").toUpperCase()}</option>
              ))}
            </select>
          </div>
        </div>
      </div>
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
        <div style={{ background: "white", padding: "20px", borderRadius: "16px", position: "relative", overflow: "hidden" }}>
          {patternInsights && (() => {
            const s = (patternInsights.dominant_season || "").toLowerCase();
            const cfg = s.includes("winter")
              ? { bg: "linear-gradient(135deg,#e0f2fe,#bae6fd)", color: "#0369a1" }
              : s.includes("summer")
              ? { bg: "linear-gradient(135deg,#fef3c7,#fde68a)", color: "#b45309" }
              : s.includes("monsoon") || s.includes("rain")
              ? { bg: "linear-gradient(135deg,#e0e7ff,#c7d2fe)", color: "#4338ca" }
              : { bg: "linear-gradient(135deg,#fef9ee,#fed7aa)", color: "#c2410c" };
            return (
              <div style={{ position: "absolute", inset: 0, background: cfg.bg, borderRadius: "16px", opacity: 0.5 }} />
            );
          })()}
          <h3 style={{ marginBottom: "8px", position: "relative" }}>Dominant Season</h3>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", position: "relative" }}>
            {patternInsights ? (() => {
              const s = (patternInsights.dominant_season || "").toLowerCase();
              const cfg = s.includes("winter")
                ? { color: "#0369a1" }
                : s.includes("summer")
                ? { color: "#b45309" }
                : s.includes("monsoon") || s.includes("rain")
                ? { color: "#4338ca" }
                : { color: "#c2410c" };
              return (
                <p style={{ fontSize: "1.7rem", fontWeight: 800, color: cfg.color, margin: 0 }}>{patternInsights.dominant_season}</p>
              );
            })() : <p style={{ fontSize: "1.2rem", fontWeight: 700, color: "#166534", margin: 0 }}>Loading...</p>}
          </div>
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
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "12px", flexWrap: "wrap", marginBottom: "20px" }}>
          <div>
            <h3 style={{ marginBottom: "6px" }}>Advanced Device Explorer</h3>
            <p style={{ margin: 0, color: "#5b6775" }}>Analyze specific appliances or filter by category across your home's ecosystem.</p>
          </div>
          <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
            <input 
              type="text" 
              placeholder="Search devices..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="form-input"
              style={{ minWidth: "200px" }}
            />
            <select
              value={selectedHours}
              onChange={(event) => setSelectedHours(Number(event.target.value))}
              className="form-input"
              style={{ maxWidth: "180px", cursor: "pointer" }}
            >
              {TIME_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
        
        <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", paddingBottom: "10px", borderBottom: "1px solid #f0f2f5" }}>
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              style={{
                padding: "8px 16px",
                borderRadius: "20px",
                border: "none",
                background: selectedCategory === cat ? "#0f4c81" : "#f0f2f5",
                color: selectedCategory === cat ? "white" : "#5b6775",
                cursor: "pointer",
                fontWeight: 600,
                transition: "all 0.2s"
              }}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {loadingGraphs ? (
        <div style={{ background: "white", padding: "20px", borderRadius: "12px" }}>
          Loading device graphs...
        </div>
      ) : filteredSeries.length ? (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "20px", marginBottom: "20px" }}>
          {filteredSeries.map((device, index) => {
            const [borderColor, backgroundColor] = CHART_COLORS[index % CHART_COLORS.length];
            return (
              <div key={device.device_name} style={{ background: "white", padding: "20px", borderRadius: "16px", boxShadow: "0 10px 24px rgba(15, 76, 129, 0.08)" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: "12px", marginBottom: "12px" }}>
                  <div>
                    <h3 style={{ margin: 0 }}>{device.device_name}</h3>
                    <span style={{ fontSize: "0.8rem", color: "#888", textTransform: "uppercase", letterSpacing: "1px" }}>{device.category}</span>
                  </div>
                  <span style={{ color: borderColor, fontWeight: 700 }}>{device.total_energy_kwh} kWh</span>
                </div>
                <p style={{ marginTop: 0, color: "#5b6775" }}>
                  Share: {device.share}% {selectedHours === -1 ? "| Live" : ""}
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
          No matching devices found in the selected time window.
        </div>
      )}

      <div style={{ background: "white", padding: "20px", borderRadius: "12px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", gap: "10px", marginBottom: "10px" }}>
          <h3 style={{ margin: 0 }}>Top Device Contributors</h3>
          <span style={{ color: "#64748b", fontSize: "0.85rem", fontWeight: 700 }}>Scroll</span>
        </div>
        {breakdown && breakdown.length ? (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "15px", maxHeight: "190px", overflowY: "auto", paddingRight: "6px", alignContent: "start" }}>
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
