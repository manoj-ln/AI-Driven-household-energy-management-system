import React, { useEffect, useMemo, useState } from "react";
import Chart from "../components/Dashboard/Chart";
import {
  getDeviceBreakdown,
  getEfficiencyScore,
  getHistoricalData,
  getRecentUsage,
} from "../services/apiService";

function StudioBadge({ label, value, accent }) {
  return (
    <div
      style={{
        padding: "14px 16px",
        borderRadius: "18px",
        background: "white",
        border: `1px solid ${accent}22`,
      }}
    >
      <div style={{ color: "#5d6778", fontSize: "0.9rem", marginBottom: "4px" }}>{label}</div>
      <div style={{ color: accent, fontWeight: 800, fontSize: "1.3rem" }}>{value}</div>
    </div>
f  );
}

function DevicePill({ name, share }) {
  return (
    <div
      style={{
        padding: "10px 12px",
        borderRadius: "14px",
        background: "linear-gradient(180deg, #ffffff 0%, #f8fbff 100%)",
        border: "1px solid rgba(15,76,129,0.14)",
        display: "flex",
        justifyContent: "space-between",
        gap: "10px",
        alignItems: "center",
      }}
    >
      <span style={{ color: "#17324d", fontWeight: 700 }}>{name}</span>
      <span style={{ color: "#5d6778", fontSize: "0.9rem" }}>{Number(share || 0).toFixed(1)}%</span>
    </div>
  );
}

function EnergyStudio() {
  const [history, setHistory] = useState([]);
  const [recent, setRecent] = useState([]);
  const [devices, setDevices] = useState([]);
  const [efficiency, setEfficiency] = useState(null);

  useEffect(() => {
    async function loadStudio() {
      const [historyData, recentData, deviceData, efficiencyData] = await Promise.all([
        getHistoricalData(14),
        getRecentUsage(),
        getDeviceBreakdown(),
        getEfficiencyScore(),
      ]);
      setHistory(historyData || []);
      setRecent(recentData || []);
      setDevices(deviceData || []);
      setEfficiency(efficiencyData || null);
    }
    loadStudio();
  }, []);

  const persona = useMemo(() => {
    const dailyAverage = history.length
      ? history.reduce((sum, item) => sum + Number(item.total_consumption || 0), 0) / history.length
      : 0;
    if (dailyAverage > 60) {
      return "High-intensity smart home";
    }
    if (dailyAverage > 30) {
      return "Balanced family energy profile";
    }
    return "Low-load efficient profile";
  }, [history]);

  const storyline = useMemo(() => {
    const dominantDevice = devices[0]?.name || "your main device";
    const topShare = devices[0]?.share || 0;
    const latest = recent[recent.length - 1]?.total_consumption || 0;
    return [
      `The home currently behaves like a ${persona.toLowerCase()}, with ${dominantDevice} leading the visible energy signature.`,
      `The largest contributor is holding about ${topShare}% of the recent device share, which gives you a strong explanation point during a demo.`,
      `The latest observed usage point is ${latest} kWh, helping you connect historical storytelling with current state awareness.`,
    ];
  }, [devices, persona, recent]);

  return (
    <section style={{ marginBottom: "38px" }}>
      <div
        style={{
          padding: "28px",
          borderRadius: "26px",
          background: "linear-gradient(135deg, #fff8ec 0%, #fff2d7 45%, #f8dfb2 100%)",
          color: "#4b3104",
          boxShadow: "0 20px 45px rgba(120,84,18,0.12)",
          marginBottom: "22px",
        }}
      >
        <p style={{ margin: "0 0 10px 0", letterSpacing: "0.16em", textTransform: "uppercase", opacity: 0.72 }}>
          Energy Studio
        </p>
        <h2 style={{ margin: "0 0 10px 0", fontSize: "2.1rem" }}>Presentation Layer</h2>
        <p style={{ margin: 0, lineHeight: 1.7 }}>
          This page turns raw usage into a narrative layer that most student projects do not include. It helps you present your
          system like a product story, not just a chart collection.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px", marginBottom: "20px" }}>
        <StudioBadge label="Energy Persona" value={persona} accent="#b45309" />
        <StudioBadge label="Efficiency Grade" value={efficiency ? `${efficiency.grade} / ${efficiency.score}` : "Loading..."} accent="#166534" />
        <StudioBadge label="Tracked Days" value={history.length} accent="#0f4c81" />
        <StudioBadge label="Visible Devices" value={devices.length} accent="#9f1239" />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginBottom: "20px" }}>
        <div className="card" style={{ borderRadius: "22px" }}>
          <h3 style={{ marginBottom: "8px" }}>Daily Rhythm Story</h3>
          <p style={{ marginTop: 0, color: "#5d6778" }}>
            A two-week timeline that helps you explain consistency, spikes, and system behavior over time.
          </p>
          <Chart
            labels={history.map((item) => item.date)}
            values={history.map((item) => item.total_consumption)}
            datasetLabel="Daily consumption (kWh)"
            borderColor="#b45309"
            backgroundColor="rgba(180, 83, 9, 0.16)"
            chartType="line"
          />
        </div>

        <div className="card" style={{ borderRadius: "22px" }}>
          <h3 style={{ marginBottom: "8px" }}>Device Share Canvas</h3>
          <p style={{ marginTop: 0, color: "#5d6778" }}>
            A quick presentation view for explaining which devices shape the home energy identity the most.
          </p>
          <Chart
            labels={devices.map((item) => item.name)}
            values={devices.map((item) => item.share)}
            datasetLabel="Device share (%)"
            borderColor="#0f4c81"
            backgroundColor="rgba(15, 76, 129, 0.24)"
            chartType="bar"
            yAxisLabel="Share (%)"
          />
        </div>
      </div>

      <div className="card" style={{ borderRadius: "22px", marginBottom: "20px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: "12px", flexWrap: "wrap", alignItems: "center" }}>
          <div>
            <h3 style={{ marginBottom: "8px" }}>Visible Device List</h3>
            <p style={{ marginTop: 0, color: "#5d6778" }}>
              These are the devices currently contributing to the device-share view above.
            </p>
          </div>
          <div style={{ padding: "10px 14px", borderRadius: "14px", background: "#fff4f6", color: "#9f1239", fontWeight: 800 }}>
            {devices.length} devices
          </div>
        </div>
        {devices.length ? (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "12px" }}>
            {devices.map((device) => (
              <DevicePill key={device.name} name={device.name} share={device.share} />
            ))}
          </div>
        ) : (
          <div style={{ color: "#5d6778" }}>No device data is available yet.</div>
        )}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
        <div className="card" style={{ borderRadius: "22px", background: "linear-gradient(180deg, #ffffff 0%, #fafcff 100%)" }}>
          <h3 style={{ color: "#0f4c81", marginBottom: "10px" }}>Project Storyline</h3>
          <ul style={{ margin: 0, paddingLeft: "18px", color: "#536172", lineHeight: 1.8 }}>
            {storyline.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>

        <div className="card" style={{ borderRadius: "22px", background: "linear-gradient(180deg, #ffffff 0%, #f7fbff 100%)" }}>
          <h3 style={{ color: "#0f4c81", marginBottom: "10px" }}>Viva Boost Notes</h3>
          <div style={{ display: "grid", gap: "12px" }}>
            <div style={{ padding: "12px", borderRadius: "14px", background: "#f3f8ff" }}>
              <strong>Why this is different</strong>
              <div style={{ color: "#5d6778", marginTop: "6px" }}>The project now includes an executive AI brief and a presentation layer, not just dashboards and forms.</div>
            </div>
            <div style={{ padding: "12px", borderRadius: "14px", background: "#fff7eb" }}>
              <strong>How to present it</strong>
              <div style={{ color: "#5d6778", marginTop: "6px" }}>Explain how the analytics feed forecasting, how forecasting feeds planning, and how this page converts results into decisions.</div>
            </div>
            <div style={{ padding: "12px", borderRadius: "14px", background: "#effbf4" }}>
              <strong>What reviewers will remember</strong>
              <div style={{ color: "#5d6778", marginTop: "6px" }}>A project that feels like a product: monitored, predictive, explainable, and presentation-ready.</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default EnergyStudio;
