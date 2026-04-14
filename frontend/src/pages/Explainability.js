import React, { useEffect, useState } from "react";
import { formatINR, getPredictionExplainability } from "../services/apiService";

function Explainability() {
  const [data, setData] = useState(null);

  useEffect(() => {
    async function loadExplainability() {
      const response = await getPredictionExplainability();
      setData(response || null);
    }
    loadExplainability();
  }, []);

  const prediction = data?.prediction;
  const topFactors = data?.top_factors || [];

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
          Model Explainability
        </p>
        <h2 style={{ margin: "0 0 8px 0", fontSize: "2.2rem" }}>Prediction Explainability Screen</h2>
        <p style={{ margin: 0, maxWidth: "820px", lineHeight: 1.7, opacity: 0.92 }}>
          This screen explains why the next-hour forecast changed, using transparent and model-agnostic feature impact scores.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px", marginBottom: "20px" }}>
        <div className="card">
          <div style={{ color: "#5d6778", marginBottom: "8px" }}>Predicted Energy</div>
          <div style={{ color: "#0f4c81", fontWeight: 800, fontSize: "1.7rem" }}>{prediction ? `${prediction.energy_kwh} kWh` : "Loading..."}</div>
        </div>
        <div className="card">
          <div style={{ color: "#5d6778", marginBottom: "8px" }}>Confidence</div>
          <div style={{ color: "#166534", fontWeight: 800, fontSize: "1.7rem" }}>
            {prediction ? `${(Number(prediction.confidence || 0) * 100).toFixed(1)}%` : "Loading..."}
          </div>
        </div>
        <div className="card">
          <div style={{ color: "#5d6778", marginBottom: "8px" }}>Estimated Cost</div>
          <div style={{ color: "#b45309", fontWeight: 800, fontSize: "1.7rem" }}>
            {prediction ? formatINR(prediction.estimated_cost_inr || 0) : "Loading..."}
          </div>
        </div>
      </div>

      <div className="card" style={{ borderRadius: "20px" }}>
        <h3 style={{ marginTop: 0 }}>Top Contributing Factors</h3>
        <p style={{ color: "#5d6778" }}>{data?.note || "Loading explainability notes..."}</p>
        {topFactors.length === 0 ? (
          <p>No explainability factors available.</p>
        ) : (
          <div style={{ display: "grid", gap: "10px" }}>
            {topFactors.map((factor) => (
              <div key={factor.name} style={{ padding: "12px", borderRadius: "12px", background: "#f6fbff", border: "1px solid #dbeafe" }}>
                <strong>{factor.name.replaceAll("_", " ")}</strong>
                <div style={{ color: "#5d6778" }}>Impact score: {factor.impact}</div>
                <div style={{ color: "#5d6778" }}>Direction: {factor.direction}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}

export default Explainability;
