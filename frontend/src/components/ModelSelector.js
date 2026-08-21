import React, { useEffect, useState } from "react";
import { getAvailableModels, setModel } from "../services/apiService";

function ModelSelector({ onModelChanged }) {
  const [models, setModels] = useState([]);
  const [currentModel, setCurrentModel] = useState("");
  const [accuracies, setAccuracies] = useState({});
  const [availability, setAvailability] = useState({});
  const [accuracySource, setAccuracySource] = useState({});
  const [previewPredictions, setPreviewPredictions] = useState({});
  const [message, setMessage] = useState("");

  const loadModels = async () => {
    const data = await getAvailableModels();
    setModels(data?.models || []);
    setCurrentModel(data?.current || "");
    setAccuracies(data?.accuracies || {});
    setAvailability(data?.availability || {});
    setAccuracySource(data?.accuracy_source || {});
    setPreviewPredictions(data?.preview_predictions || {});
  };

  useEffect(() => {
    loadModels();
  }, []);

  const handleModelChange = async (modelName) => {
    const result = await setModel(modelName);
    if (result?.status === "success") {
      setCurrentModel(modelName);
      setMessage(`Model changed to ${modelName}.`);
      onModelChanged?.(modelName);
      await loadModels();
    } else {
      setMessage(result?.message || "Failed to change model.");
    }
  };

  return (
    <div style={{ background: "white", padding: "20px", borderRadius: "12px", marginBottom: "20px" }}>
      <h3>AI Model Selection</h3>
      <p>Current Model: <strong>{currentModel || "Loading..."}</strong></p>
      <p style={{ color: "#5d6778", marginTop: 0 }}>
        Accuracy comes from saved model performance when available. If a performance file is missing, the app shows an estimated fallback value and also displays a live preview forecast so you can verify the model is responding.
      </p>
      {message ? <p style={{ color: message.includes("Failed") ? "#b42318" : "#12723b" }}>{message}</p> : null}
      <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
        {models.map((model) => {
          const available = availability[model];
          return (
            <button
              key={model}
              onClick={() => handleModelChange(model)}
              disabled={!available}
              style={{
                padding: "10px 20px",
                background: currentModel === model ? "#007bff" : "#f8f9fa",
                color: currentModel === model ? "white" : "#333",
                border: "1px solid #ddd",
                borderRadius: "8px",
                cursor: available ? "pointer" : "not-allowed",
                transition: "all 0.3s",
                opacity: available ? 1 : 0.55,
                minWidth: "170px",
              }}
            >
              {model.replace(/_/g, " ").toUpperCase()}
              <br />
              <small>Accuracy: {accuracies[model] ? `${(accuracies[model] * 100).toFixed(1)}%` : "N/A"}</small>
              <br />
              <small>{accuracySource[model] || "source unknown"}</small>
              <br />
              <small>{previewPredictions[model] !== undefined && previewPredictions[model] !== null ? `Preview: ${previewPredictions[model]} kWh` : "Preview unavailable"}</small>
              <br />
              <small>{available ? "Working" : "Model file missing"}</small>
            </button>
          );
        })}
      </div>
    </div>
  );
}

export default ModelSelector;
