import React, { useEffect, useMemo, useState } from "react";
import Chart from "../components/Dashboard/Chart";
import {
  formatINR,
  getAnalyticsSummary,
  getForecast,
  getNextHourPrediction,
  getOptimizationReport,
  getPatternInsights,
} from "../services/apiService";

function InsightCard({ title, value, tone = "#0f4c81", subtitle }) {
  return (
    <div
      className="card"
      style={{
        borderRadius: "22px",
        background: "linear-gradient(180deg, #ffffff 0%, #f6fbff 100%)",
        border: "1px solid rgba(15,76,129,0.08)",
      }}
    >
      <div style={{ color: "#5d6778", marginBottom: "8px", fontSize: "0.95rem" }}>{title}</div>
      <div style={{ color: tone, fontWeight: 800, fontSize: "1.9rem", marginBottom: "6px" }}>{value}</div>
      <div style={{ color: "#5d6778", lineHeight: 1.5 }}>{subtitle}</div>
    </div>
  );
}

function IntelligenceHub() {
  const [summary, setSummary] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [pattern, setPattern] = useState(null);
  const [optimization, setOptimization] = useState(null);
  const [forecast, setForecast] = useState([]);

  useEffect(() => {
    async function loadPage() {
      const [summaryData, predictionData, patternData, optimizationData, forecastData] = await Promise.all([
        getAnalyticsSummary(),
        getNextHourPrediction(),
        getPatternInsights(),
        getOptimizationReport(),
        getForecast(24),
      ]);
      setSummary(summaryData || null);
      setPrediction(predictionData?.prediction || null);
      setPattern(patternData || null);
      setOptimization(optimizationData || null);
      setForecast(forecastData || []);
    }
    loadPage();
  }, []);

  const derived = useMemo(() => {
    const quality = Number(pattern?.quality_score || 0);
    const confidence = Number(prediction?.confidence || 0) * 100;
    const savings = Number(optimization?.estimated_savings || 0);
    const readiness = Math.min(100, Math.round((quality * 0.45) + (confidence * 0.35) + Math.min(20, savings / 5)));
    const billPressure = summary?.daily_consumption ? Math.min(100, Math.round((Number(summary.daily_consumption) / 80) * 100)) : 0;
    const resilience = optimization?.monthly_projection?.optimized_bill_total_inr
      ? Math.max(
          0,
          Math.min(
            100,
            100 - Math.round(
              ((optimization.monthly_projection.optimized_bill_total_inr - optimization.monthly_projection.bill_total_inr) / Math.max(optimization.monthly_projection.bill_total_inr, 1)) * 100
            )
          )
        )
      : 0;
    const story = quality >= 90 && confidence >= 90
      ? "You are looking at a high-trust energy view right now, with strong dataset discipline and confident forecasting supporting your decisions."
      : "You are already getting a useful energy picture, and the clearest next gain for you is to keep improving forecast trust and data coverage.";
    return { readiness, billPressure, resilience, story };
  }, [optimization, pattern, prediction, summary]);

  const forecastLabels = forecast.map((point) =>
    new Date(point.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
  );
  const forecastValues = forecast.map((point) => point.energy_kwh);

  const recommendationTiles = useMemo(() => {
    if (!optimization || !pattern || !prediction) {
      return [];
    }
    return [
      {
        title: "Decision Window",
        text: `Your strongest cost-control window is around ${summary?.peak_hour || "the current peak period"}. This is where scheduling changes create the biggest visible savings.`,
      },
      {
        title: "AI Readiness",
        text: `The current model is ${prediction.model} with ${prediction.confidence_label?.toLowerCase() || "good"} confidence. This is presentation-ready for a live demo flow.`,
      },
      {
        title: "Data Trust",
        text: `Quality score is ${pattern.quality_score}/100 with ${pattern.invalid_records} suspicious records. That gives you a strong trust story in front of reviewers.`,
      },
    ];
  }, [optimization, pattern, prediction, summary]);

  return (
    <section style={{ marginBottom: "38px" }}>
      <div
        style={{
          padding: "28px",
          borderRadius: "26px",
          background: "linear-gradient(135deg, rgba(7,30,50,0.96) 0%, rgba(15,76,129,0.94) 56%, rgba(26,116,184,0.88) 100%)",
          color: "white",
          boxShadow: "0 24px 50px rgba(7,30,50,0.22)",
          marginBottom: "22px",
        }}
      >
        <div style={{ maxWidth: "820px" }}>
          <p style={{ margin: "0 0 10px 0", letterSpacing: "0.16em", textTransform: "uppercase", opacity: 0.78 }}>
            Intelligence Hub
          </p>
          <h2 style={{ margin: "0 0 10px 0", fontSize: "2.15rem" }}>Executive Energy Brief</h2>
          <p style={{ margin: 0, opacity: 0.92, lineHeight: 1.65 }}>
            A premium decision layer for your project. It converts the current dashboard state into a boardroom-style AI brief,
            showing how trustworthy the system is, where the cost pressure lives, and what the next move should be.
          </p>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px", marginBottom: "20px" }}>
        <InsightCard title="Project Readiness" value={`${derived.readiness}/100`} tone="#166534" subtitle="Blend of data quality, forecast confidence, and savings visibility." />
        <InsightCard title="Bill Pressure Index" value={`${derived.billPressure}/100`} tone="#b45309" subtitle="A quick way to explain how intense the current daily energy profile is." />
        <InsightCard title="Forecast Confidence" value={prediction ? `${(prediction.confidence * 100).toFixed(1)}%` : "Loading..."} tone="#0f4c81" subtitle={prediction ? `${prediction.confidence_label} confidence with ${prediction.trend.toLowerCase()} short-term movement.` : "Waiting for prediction data."} />
        <InsightCard title="Savings Story" value={optimization ? formatINR(optimization.estimated_savings) : "Loading..."} tone="#9f1239" subtitle="Estimated daily savings from the current optimization layer." />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1.25fr 0.75fr", gap: "20px", marginBottom: "20px" }}>
        <div className="card" style={{ borderRadius: "22px" }}>
          <h3 style={{ marginBottom: "8px" }}>24-Hour Forecast Story</h3>
          <p style={{ marginTop: 0, color: "#5d6778" }}>
            This is a presentation-focused forecast lane. It helps explain where the next demand wave is likely to form and what that means for cost.
          </p>
          <Chart
            labels={forecastLabels}
            values={forecastValues}
            datasetLabel="Forecasted energy (kWh)"
            borderColor="#0f4c81"
            backgroundColor="rgba(15, 76, 129, 0.16)"
            chartType="line"
          />
        </div>
        <div className="card" style={{ borderRadius: "22px", background: "linear-gradient(180deg, #ffffff 0%, #f7fbff 100%)" }}>
          <h3 style={{ marginBottom: "8px" }}>AI Narrative</h3>
          <p style={{ color: "#49566a", lineHeight: 1.7 }}>{derived.story}</p>
          <p style={{ color: "#49566a", lineHeight: 1.7 }}>
            You are currently seeing the strongest usage around <strong>{summary?.peak_hour || "the active peak window"}</strong>, while your present dataset quality score is <strong>{pattern?.quality_score || 0}/100</strong>.
          </p>
          <p style={{ color: "#49566a", lineHeight: 1.7, marginBottom: 0 }}>
            Use this page when you want your project to guide the user like a decision platform instead of only showing charts.
          </p>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "16px" }}>
        {recommendationTiles.map((tile) => (
          <div key={tile.title} className="card" style={{ borderRadius: "20px", background: "linear-gradient(180deg, #ffffff 0%, #f5f9ff 100%)" }}>
            <h3 style={{ color: "#0f4c81", marginBottom: "8px" }}>{tile.title}</h3>
            <p style={{ margin: 0, color: "#5d6778", lineHeight: 1.65 }}>{tile.text}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export default IntelligenceHub;
