import React, { useEffect, useState } from "react";
import { getEfficiencyScore } from "../services/apiService";

function EfficiencyScore() {
  const [score, setScore] = useState(null);

  useEffect(() => {
    async function loadScore() {
      const data = await getEfficiencyScore();
      setScore(data);
    }
    loadScore();
  }, []);

  if (!score) return <div>Loading efficiency score...</div>;

  const getColor = (grade) => {
    switch (grade) {
      case "A": return "#16a34a";
      case "B": return "#ca8a04";
      case "C": return "#ea580c";
      case "D": return "#dc2626";
      default: return "#6c757d";
    }
  };

  const gradientColor = `conic-gradient(#16a34a 0 25%, #eab308 25% 50%, #f97316 50% 75%, #dc2626 75% 100%)`;

  return (
    <div style={{ background: "white", padding: "20px", borderRadius: "12px", marginBottom: "20px" }}>
      <h3>Energy Efficiency Score</h3>
      <div style={{ display: "grid", gridTemplateColumns: "180px 1fr", gap: "20px", alignItems: "center" }}>
        <div style={{ textAlign: "center" }}>
          <div
            style={{
              width: "120px",
              height: "120px",
              borderRadius: "50%",
              background: `${gradientColor}`,
              padding: "10px",
              margin: "0 auto",
            }}
          >
            <div
              style={{
                width: "100%",
                height: "100%",
                borderRadius: "50%",
                background: "white",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexDirection: "column",
                color: getColor(score.grade),
                fontWeight: "bold",
              }}
            >
              <div style={{ fontSize: "28px" }}>{score.score}</div>
              <div style={{ fontSize: "14px" }}>Grade {score.grade}</div>
            </div>
          </div>
        </div>
        <div>
          <p style={{ marginTop: 0, color: "#5d6778" }}>
            The ring uses four colors to explain performance bands. Green is best, yellow is good, orange needs improvement, and red means the home is inefficient.
          </p>
          <div style={{ display: "flex", gap: "14px", flexWrap: "wrap", marginBottom: "12px" }}>
            <span style={{ color: "#16a34a" }}>A: Excellent</span>
            <span style={{ color: "#ca8a04" }}>B: Good</span>
            <span style={{ color: "#ea580c" }}>C: Moderate</span>
            <span style={{ color: "#dc2626" }}>D: Poor</span>
          </div>
          <h4>Recommendations:</h4>
          <ul>
            {score.recommendations.map((rec, index) => (
              <li key={index}>{rec}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default EfficiencyScore;
