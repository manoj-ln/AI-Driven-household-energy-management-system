import React, { useEffect, useState } from "react";
import EnergyDashboard from "../components/Dashboard/EnergyDashboard";
import { getDatasetMode, setDatasetMode, getDatasets, selectDataset } from "../services/apiService";

const featureCards = [
  {
    title: "Smart Home View",
    text: "Track your home's energy profile with live charts, device history, and software-only monitoring.",
  },
  {
    title: "Prediction Engine",
    text: "Forecast the next usage window with trained-model support and cost estimates in rupees.",
  },
  {
    title: "Smart Optimization",
    text: "Compare baseline, optimized, and solar-style scenarios to present practical energy savings.",
  },
  {
    title: "Executive AI Brief",
    text: "Translate raw energy data into a decision-ready story with readiness scoring, forecast briefing, and strategic insights.",
  },
  {
    title: "Presentation Studio",
    text: "Turn analytics into a polished narrative layer for viva, review, and final project demonstration.",
  },
];

function Home() {
  const [datasetMode, setDatasetModeState] = useState("auto");
  const [datasetName, setDatasetName] = useState("");
  const [datasets, setDatasets] = useState([]);
  const [isLoadingDatasets, setIsLoadingDatasets] = useState(true);
  const [datasetError, setDatasetError] = useState("");
  const [datasetStatus, setDatasetStatus] = useState("");

  const loadDatasetControls = async () => {
    setIsLoadingDatasets(true);
    setDatasetError("");
    const [modeResponse, datasetsResponse] = await Promise.all([getDatasetMode(), getDatasets()]);

    if (modeResponse?.mode) {
      setDatasetModeState(modeResponse.mode);
    }

    if (!datasetsResponse) {
      setDatasetError(
        "Dataset endpoints are not responding. Restart backend and refresh this page to load dataset files."
      );
      setDatasets([]);
      setIsLoadingDatasets(false);
      return;
    }

    const files = Array.isArray(datasetsResponse?.datasets) ? datasetsResponse.datasets : [];
    setDatasets(files);

    if (datasetsResponse?.selected_dataset) {
      setDatasetName(datasetsResponse.selected_dataset);
    } else if (files.length > 0) {
      setDatasetName(files[0]);
    } else {
      setDatasetName("");
      setDatasetError(
        "No dataset files found. Ensure CSV files exist in backend/data/datasets."
      );
    }
    setIsLoadingDatasets(false);
  };

  useEffect(() => {
    loadDatasetControls();
  }, []);

  const handleDatasetChange = async (event) => {
    const nextMode = event.target.value;
    setDatasetModeState(nextMode);
    const response = await setDatasetMode(nextMode);
    if (response?.status === "success") {
      setDatasetStatus(`Dataset mode changed to ${response.mode}.`);
      await loadDatasetControls();
      return;
    }
    setDatasetStatus("Could not change dataset mode.");
  };

  const handleDatasetFileChange = async (event) => {
    const selected = event.target.value;
    if (!selected) {
      return;
    }
    setDatasetName(selected);
    const response = await selectDataset(selected);
    if (response?.status === "success") {
      setDatasetStatus(`Selected dataset: ${response.selected_dataset}.`);
      await loadDatasetControls();
      return;
    }
    setDatasetStatus("Could not select dataset file.");
  };

  return (
    <section style={{ marginBottom: "38px" }}>
      <div
        style={{
          padding: "28px",
          borderRadius: "24px",
          background: "linear-gradient(135deg, rgba(10,43,69,0.95) 0%, rgba(16,74,125,0.92) 52%, rgba(26,116,184,0.88) 100%)",
          color: "white",
          marginBottom: "22px",
          boxShadow: "0 20px 45px rgba(11,43,69,0.22)",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            position: "absolute",
            inset: "auto -80px -80px auto",
            width: "220px",
            height: "220px",
            borderRadius: "50%",
            background: "radial-gradient(circle, rgba(255,255,255,0.18) 0%, rgba(255,255,255,0.02) 70%)",
          }}
        />
        <p style={{ margin: "0 0 8px 0", letterSpacing: "0.16em", textTransform: "uppercase", opacity: 0.78 }}>
          SmartHouse AI
        </p>
        <h2 style={{ fontSize: "2.15rem", marginBottom: "10px", maxWidth: "760px" }}>
          A software-first platform for home energy forecasting, analytics, optimization, and device intelligence.
        </h2>
        <p style={{ margin: 0, maxWidth: "760px", lineHeight: 1.6, opacity: 0.92 }}>
          The project now presents like a complete SmartHouse product experience: manual readings flow into analytics,
          device graphs update by time window, predictions work with a compatible saved model path, and the help bot
          supports grammar, language, device status, and past-data questions.
        </p>
        <div style={{ marginTop: "14px", display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
          <label htmlFor="dataset-mode" style={{ fontWeight: 700 }}>Dataset selection</label>
          <select
            id="dataset-mode"
            className="form-input"
            style={{ width: "260px", background: "white", color: "#123", border: "none" }}
            value={datasetMode}
            onChange={handleDatasetChange}
            disabled={isLoadingDatasets}
          >
            <option value="auto">Auto (real then synthetic fallback)</option>
            <option value="real_only">Real only</option>
            <option value="synthetic_demo">Synthetic demo</option>
          </select>
          <span style={{ opacity: 0.9 }}>Step 1: choose mode. Step 2: choose file.</span>
        </div>
        <div style={{ marginTop: "10px", display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
          <label htmlFor="dataset-file" style={{ fontWeight: 700 }}>Dataset file</label>
          <select
            id="dataset-file"
            className="form-input"
            style={{ width: "320px", background: "white", color: "#123", border: "none" }}
            value={datasetName}
            onChange={handleDatasetFileChange}
            disabled={isLoadingDatasets || datasets.length === 0}
          >
            {datasets.length === 0 ? (
              <option value="">{isLoadingDatasets ? "Loading dataset files..." : "No dataset files available"}</option>
            ) : (
              datasets.map((name) => (
                <option key={name} value={name}>
                  {name}
                </option>
              ))
            )}
          </select>
          <button
            type="button"
            className="btn"
            style={{ background: "rgba(255,255,255,0.22)", color: "white", borderRadius: "10px" }}
            onClick={loadDatasetControls}
            disabled={isLoadingDatasets}
          >
            {isLoadingDatasets ? "Refreshing..." : "Refresh Datasets"}
          </button>
        </div>
        <p style={{ marginTop: "8px", marginBottom: 0, opacity: 0.95 }}>
          Active mode: <strong>{datasetMode}</strong> | Active file: <strong>{datasetName || "N/A"}</strong> | Available files: <strong>{datasets.length}</strong>
        </p>
        {datasetError ? <p style={{ marginTop: "8px", marginBottom: 0, color: "#ffd4d4" }}>{datasetError}</p> : null}
        {datasetStatus ? <p style={{ marginTop: "8px", marginBottom: 0, opacity: 0.9 }}>{datasetStatus}</p> : null}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px", marginBottom: "24px" }}>
        {featureCards.map((card) => (
          <div
            key={card.title}
            className="card"
            style={{
              borderRadius: "20px",
              border: "1px solid rgba(15,76,129,0.08)",
              background: "linear-gradient(180deg, #ffffff 0%, #f5f9ff 100%)",
            }}
          >
            <h3 style={{ marginBottom: "10px", color: "#0f4c81" }}>{card.title}</h3>
            <p style={{ margin: 0, color: "#556070", lineHeight: 1.55 }}>{card.text}</p>
          </div>
        ))}
      </div>

      <EnergyDashboard />
    </section>
  );
}

export default Home;
