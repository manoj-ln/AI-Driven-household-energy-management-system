import React from "react";

function StatCard({ label, value, accent = "#0f4c81" }) {
  return (
    <div
      style={{
        background: "linear-gradient(180deg, #ffffff 0%, #f7fbff 100%)",
        padding: "20px",
        borderRadius: "18px",
        boxShadow: "0 10px 25px rgba(15, 76, 129, 0.08)",
        borderTop: `4px solid ${accent}`,
      }}
    >
      <div style={{ fontSize: "13px", color: "#6a7283", textTransform: "uppercase", letterSpacing: "0.08em" }}>
        {label}
      </div>
      <div style={{ fontSize: "26px", marginTop: "12px", color: accent, fontWeight: 700 }}>{value}</div>
    </div>
  );
}

export default StatCard;
