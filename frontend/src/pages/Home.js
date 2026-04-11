import React from "react";
import EnergyDashboard from "../components/Dashboard/EnergyDashboard";

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
