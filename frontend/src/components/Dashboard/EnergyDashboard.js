import React, { useEffect, useMemo, useState } from "react";
import StatCard from "./StatCard";
import Chart from "./Chart";
import { getAnalyticsSummary, getRecentUsage, getDeviceBreakdown } from "../../services/apiService";

function EnergyDashboard() {
  const [summary, setSummary] = useState(null);
  const [recentUsage, setRecentUsage] = useState([]);
  const [devices, setDevices] = useState([]);
  const [graphMode, setGraphMode] = useState("standard");
  const [displayFormat, setDisplayFormat] = useState("line");
  const [liveSeries, setLiveSeries] = useState([]);

  useEffect(() => {
    async function loadData() {
      const [summaryData, recentData, deviceData] = await Promise.all([
        getAnalyticsSummary(),
        getRecentUsage(),
        getDeviceBreakdown(),
      ]);
      setSummary(summaryData || null);
      setRecentUsage(recentData || []);
      setDevices(deviceData || []);
    }

    loadData();
  }, []);

  useEffect(() => {
    if (graphMode !== "live") {
      return undefined;
    }
    const latest = Number(recentUsage[recentUsage.length - 1]?.total_consumption || 0.8);
    const seed = Array.from({ length: 60 }, (_, index) => ({
      second: index + 1,
      value: Number((latest + Math.sin(index / 4) * 0.08 + (index % 5) * 0.01).toFixed(3)),
    }));
    setLiveSeries(seed);

    const interval = window.setInterval(() => {
      setLiveSeries((prev) => {
        const lastSecond = prev.length ? prev[prev.length - 1].second : 0;
        const nextValue = Number((latest + Math.sin(lastSecond / 4) * 0.08 + ((lastSecond + 1) % 5) * 0.01).toFixed(3));
        return [...prev.slice(-59), { second: lastSecond + 1, value: nextValue }];
      });
    }, 1000);

    return () => window.clearInterval(interval);
  }, [graphMode, recentUsage]);

  const chartLabels = (recentUsage || []).map((record) =>
    new Date(record.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
  );
  const chartData = (recentUsage || []).map((record) => record.total_consumption);

  const activeLabels = useMemo(() => {
    if (graphMode === "live") {
      return liveSeries.map((point) => `${point.second}s`);
    }
    return chartLabels;
  }, [graphMode, liveSeries, chartLabels]);

  const activeValues = useMemo(() => {
    if (graphMode === "live") {
      return liveSeries.map((point) => point.value);
    }
    return chartData;
  }, [graphMode, liveSeries, chartData]);

  const graphExplanation = graphMode === "live"
    ? "Live second-wise mode simulates how the latest usage value changes over each second so you can demonstrate continuous data flow."
    : "Standard mode shows the saved recent usage records from the backend, grouped by time.";

  return (
    <div style={{ display: "grid", gap: "22px" }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px" }}>
        <StatCard label="Current Usage" value={summary ? `${summary.current_usage} kWh` : "Loading..."} accent="#0f4c81" />
        <StatCard label="Last 24 Hours" value={summary ? `${summary.daily_consumption} kWh` : "Loading..."} accent="#166534" />
        <StatCard label="Peak Window" value={summary ? summary.peak_hour : "Loading..."} accent="#b45309" />
        <StatCard label="Average Temp" value={summary ? `${summary.average_temperature} C` : "Loading..."} accent="#9f1239" />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "minmax(0, 1.5fr) minmax(320px, 1fr)", gap: "20px" }}>
        <div
          style={{
            background: "white",
            padding: "22px",
            borderRadius: "20px",
            boxShadow: "0 12px 28px rgba(11,43,69,0.08)",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "12px", flexWrap: "wrap", marginBottom: "14px" }}>
            <div>
              <h3 style={{ marginBottom: "6px" }}>Usage Graph</h3>
              <p style={{ margin: 0, color: "#5d6778" }}>{graphExplanation}</p>
            </div>
            <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
              <select className="form-input" style={{ width: "180px" }} value={graphMode} onChange={(e) => setGraphMode(e.target.value)}>
                <option value="standard">Saved Graph</option>
                <option value="live">Live Second-wise</option>
              </select>
              <select className="form-input" style={{ width: "180px" }} value={displayFormat} onChange={(e) => setDisplayFormat(e.target.value)}>
                <option value="line">Line Chart</option>
                <option value="bar">Bar Chart</option>
                <option value="table">Table View</option>
              </select>
            </div>
          </div>

          {displayFormat === "table" ? (
            <div style={{ maxHeight: "280px", overflowY: "auto", border: "1px solid #e5eef8", borderRadius: "12px" }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead style={{ background: "#f4f9ff" }}>
                  <tr>
                    <th style={{ textAlign: "left", padding: "10px" }}>Time</th>
                    <th style={{ textAlign: "left", padding: "10px" }}>Usage (kWh)</th>
                  </tr>
                </thead>
                <tbody>
                  {activeLabels.map((label, index) => (
                    <tr key={`${label}-${index}`} style={{ borderTop: "1px solid #edf2f7" }}>
                      <td style={{ padding: "10px" }}>{label}</td>
                      <td style={{ padding: "10px" }}>{activeValues[index]}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <Chart
              labels={activeLabels}
              values={activeValues}
              datasetLabel={graphMode === "live" ? "Live usage stream" : "Home energy profile"}
              borderColor="#0f4c81"
              backgroundColor="rgba(15, 76, 129, 0.14)"
              chartType={displayFormat}
            />
          )}
          <p style={{ marginTop: "12px", color: "#5d6778" }}>
            Graph explanation: the X-axis shows time, and the Y-axis shows energy used in kWh. Higher points or bars mean higher consumption during that time window.
          </p>
        </div>

        <div
          style={{
            background: "linear-gradient(180deg, #ffffff 0%, #f7fbff 100%)",
            padding: "22px",
            borderRadius: "20px",
            boxShadow: "0 12px 28px rgba(11,43,69,0.08)",
          }}
        >
          <h3 style={{ marginBottom: "12px" }}>Top Device Contributors</h3>
          {devices.length ? (
            <div style={{ display: "grid", gap: "14px" }}>
              {devices.map((device) => (
                <div key={device.name}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px", gap: "12px" }}>
                    <strong>{device.name}</strong>
                    <span style={{ color: "#0f4c81" }}>{device.average_usage} kWh</span>
                  </div>
                  <div
                    style={{
                      width: "100%",
                      height: "10px",
                      borderRadius: "999px",
                      background: "#e6eef7",
                      overflow: "hidden",
                    }}
                  >
                    <div
                      style={{
                        width: `${device.share}%`,
                        height: "100%",
                        borderRadius: "999px",
                        background: "linear-gradient(90deg, #0f4c81 0%, #1a74b8 100%)",
                      }}
                    />
                  </div>
                  <div style={{ marginTop: "4px", color: "#637082", fontSize: "0.92rem" }}>{device.share}% share</div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ margin: 0 }}>Loading device usage...</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default EnergyDashboard;
