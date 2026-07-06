import React, { useContext, useState } from "react";
import EnergyDashboard from "../components/Dashboard/EnergyDashboard";
import { EnergyContext } from "../context/EnergyContext";

function Home() {
  const [datasetStatus, setDatasetStatus] = useState("");
  const { datasetState, refreshDatasetState, applyDatasetSelection, activeDatasetLabel } = useContext(EnergyContext);
  const datasetMode = datasetState?.mode || "auto";
  const datasetName = datasetState?.selectedDataset || "";
  const datasets = datasetState?.datasets || [];
  const isLoadingDatasets = Boolean(datasetState?.loading);
  const datasetError = datasetState?.error || "";
  const datasetDetails = datasetState?.details;

  const handleDatasetFileChange = async (event) => {
    const selected = event.target.value;
    if (!selected) {
      return;
    }
    const response = await applyDatasetSelection(selected);
    if (response?.status === "success") {
      setDatasetStatus(`Selected dataset: ${response.selected_dataset}. This dataset now drives every page, graph, and model.`);
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
        <p style={{ margin: 0, maxWidth: "760px", lineHeight: 1.6, opacity: 0.92 }}>
          Dataset Configuration
        </p>
        <div style={{ marginTop: "14px", display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
          <strong style={{ fontWeight: 700 }}>Project dataset source</strong>
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
            onClick={refreshDatasetState}
            disabled={isLoadingDatasets}
          >
            {isLoadingDatasets ? "Refreshing..." : "Refresh Datasets"}
          </button>
        </div>
        <p style={{ marginTop: "8px", marginBottom: 0, opacity: 0.95 }}>
          Active mode: <strong>{datasetMode}</strong> | Active file: <strong>{datasetName || "N/A"}</strong> | Label: <strong>{activeDatasetLabel}</strong>
          {" "} | Cadence: <strong>{datasetDetails?.cadence_minutes ? `${datasetDetails.cadence_minutes} minute` : "Unknown"}</strong>
          {" "} | Coverage: <strong>{datasetDetails?.start || "N/A"} to {datasetDetails?.end || "N/A"}</strong>
        </p>
        {datasetError ? <p style={{ marginTop: "8px", marginBottom: 0, color: "#ffd4d4" }}>{datasetError}</p> : null}
        {datasetStatus ? <p style={{ marginTop: "8px", marginBottom: 0, opacity: 0.9 }}>{datasetStatus}</p> : null}
      </div>

      <EnergyDashboard key={`${datasetName}:${datasetMode}`} />
    </section>
  );
}

export default Home;
