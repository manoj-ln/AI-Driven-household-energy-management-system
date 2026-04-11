import React, { useMemo, useState } from "react";
import { formatINR, runSimulation } from "../services/apiService";
import Chart from "./Dashboard/Chart";

function Simulation() {
  const [form, setForm] = useState({
    scenario: "green_home",
    hours: 24,
    rate_per_kwh: 6.26,
    optimization_strength: 18,
    solar_offset: 45,
    battery_shift: 12,
    appliance_upgrade: 10,
    demand_response: 8,
    occupancy_mode: "family",
  });
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (field, value) => {
    setForm((prev) => ({
      ...prev,
      [field]: ["scenario", "occupancy_mode"].includes(field) ? value : Number(value),
    }));
  };

  const handleRunSimulation = async () => {
    setLoading(true);
    try {
      const data = await runSimulation(form);
      setResults(data);
    } catch (error) {
      console.error("Simulation error:", error);
    } finally {
      setLoading(false);
    }
  };

  const chartData = useMemo(() => {
    if (!results?.predictions?.length) {
      return { labels: [], scenarioValues: [], baselineValues: [] };
    }
    return {
      labels: results.predictions.map((point) =>
        new Date(point.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      ),
      scenarioValues: results.predictions.map((point) => point.energy_kwh),
      baselineValues: (results.baseline_predictions || []).map((point) => point.energy_kwh),
    };
  }, [results]);

  return (
    <section style={{ marginBottom: "38px", animation: "fadeIn 1s ease-in-out" }}>
      <h2 style={{ color: "#0f4c81", marginBottom: "20px" }}>Advanced Simulation</h2>
      <div className="card" style={{ maxWidth: "1240px", margin: "0 auto" }}>
        <h3 style={{ color: "#0f4c81", marginBottom: "8px" }}>Scenario Planning Studio</h3>
        <p style={{ marginTop: 0, color: "#5d6778", lineHeight: 1.6 }}>
          Build a planning scenario with occupancy behavior, BESCOM tariff, efficient appliances, demand response,
          solar-style offset, and battery shifting. The planner compares baseline and scenario hour by hour, then
          projects the result into monthly and yearly views.
        </p>

        <form onSubmit={(e) => { e.preventDefault(); handleRunSimulation(); }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px" }}>
            <div className="form-group">
              <label className="form-label">Scenario</label>
              <select value={form.scenario} onChange={(e) => handleChange("scenario", e.target.value)} className="form-input">
                <option value="normal">Normal</option>
                <option value="optimized">Optimized</option>
                <option value="solar">Solar Assisted</option>
                <option value="battery_backup">Battery Backup</option>
                <option value="weekend_saver">Weekend Saver</option>
                <option value="green_home">Green Home</option>
                <option value="peak_protection">Peak Protection</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Occupancy Mode</label>
              <select value={form.occupancy_mode} onChange={(e) => handleChange("occupancy_mode", e.target.value)} className="form-input">
                <option value="family">Family at Home</option>
                <option value="working_day">Working Day</option>
                <option value="vacation">Vacation / Low Use</option>
                <option value="guests">Guests at Home</option>
                <option value="students">Students Schedule</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Planning Horizon</label>
              <input type="number" min="6" max="168" className="form-input" value={form.hours} onChange={(e) => handleChange("hours", e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">Tariff Rate (INR/kWh)</label>
              <input type="number" min="0" step="0.1" className="form-input" value={form.rate_per_kwh} onChange={(e) => handleChange("rate_per_kwh", e.target.value)} />
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "16px", marginTop: "12px" }}>
            <div className="card" style={{ background: "#f7fbff" }}>
              <label className="form-label">Optimization Strength: {form.optimization_strength}%</label>
              <input type="range" min="0" max="60" value={form.optimization_strength} onChange={(e) => handleChange("optimization_strength", e.target.value)} style={{ width: "100%" }} />
              <small style={{ color: "#5d6778" }}>Controls how aggressively the plan cuts peak demand.</small>
            </div>
            <div className="card" style={{ background: "#f7fbff" }}>
              <label className="form-label">Solar Offset: {form.solar_offset}%</label>
              <input type="range" min="0" max="90" value={form.solar_offset} onChange={(e) => handleChange("solar_offset", e.target.value)} style={{ width: "100%" }} />
              <small style={{ color: "#5d6778" }}>Represents daytime clean-energy offset for grid usage.</small>
            </div>
            <div className="card" style={{ background: "#f7fbff" }}>
              <label className="form-label">Battery Shift: {form.battery_shift}%</label>
              <input type="range" min="0" max="40" value={form.battery_shift} onChange={(e) => handleChange("battery_shift", e.target.value)} style={{ width: "100%" }} />
              <small style={{ color: "#5d6778" }}>Softens evening demand by shifting part of the load.</small>
            </div>
            <div className="card" style={{ background: "#f7fbff" }}>
              <label className="form-label">Appliance Upgrade: {form.appliance_upgrade}%</label>
              <input type="range" min="0" max="40" value={form.appliance_upgrade} onChange={(e) => handleChange("appliance_upgrade", e.target.value)} style={{ width: "100%" }} />
              <small style={{ color: "#5d6778" }}>Shows the benefit of efficient devices replacing older ones.</small>
            </div>
            <div className="card" style={{ background: "#f7fbff" }}>
              <label className="form-label">Demand Response: {form.demand_response}%</label>
              <input type="range" min="0" max="40" value={form.demand_response} onChange={(e) => handleChange("demand_response", e.target.value)} style={{ width: "100%" }} />
              <small style={{ color: "#5d6778" }}>Represents planned reaction to peak-hour grid pressure.</small>
            </div>
          </div>

          <button type="submit" disabled={loading} className="btn btn-primary" style={{ width: "100%", marginTop: "16px" }}>
            {loading ? "Running Scenario Planning..." : "Run Advanced Simulation"}
          </button>
        </form>

        {results && (
          <div style={{ marginTop: "24px", display: "grid", gap: "20px" }}>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))", gap: "14px" }}>
              {results.summary_cards.map((card) => (
                <div key={card.label} className="card" style={{ background: "linear-gradient(180deg, #ffffff 0%, #f6fbff 100%)" }}>
                  <div style={{ color: "#5d6778", marginBottom: "6px" }}>{card.label}</div>
                  <div style={{ color: "#0f4c81", fontSize: "1.35rem", fontWeight: 700 }}>
                    {card.unit === "INR" ? formatINR(card.value) : `${card.value} ${card.unit}`}
                  </div>
                </div>
              ))}
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1.3fr 0.7fr", gap: "20px" }}>
              <div className="card" style={{ background: "linear-gradient(135deg, #eff7ff 0%, #ffffff 100%)" }}>
                <h4 style={{ color: "#0f4c81", marginBottom: "10px" }}>Planning Summary</h4>
                <p style={{ marginTop: 0, color: "#556070" }}>{results.description}</p>
                <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
                  {results.scenario_drivers.map((driver) => (
                    <span key={driver.label} style={{ padding: "8px 12px", borderRadius: "999px", background: "#e8f1fb", color: "#0f4c81" }}>
                      {driver.label}: {driver.value}{driver.unit}
                    </span>
                  ))}
                </div>
              </div>
              <div className="card" style={{ background: "linear-gradient(135deg, #f4fff4 0%, #ffffff 100%)" }}>
                <h4 style={{ color: "#166534", marginBottom: "10px" }}>Scenario Score</h4>
                <div style={{ fontSize: "2.3rem", fontWeight: 800, color: "#166534" }}>{results.scenario_score}/100</div>
                <p style={{ color: "#5d6778", marginBottom: "8px" }}>{results.recommendation?.headline}</p>
                <p style={{ margin: 0 }}>Monthly savings: <strong>{formatINR(results.recommendation?.monthly_savings_inr || 0)}</strong></p>
                <p style={{ margin: "8px 0 0" }}>Load factor gain: <strong>{results.recommendation?.load_factor_gain || 0}</strong></p>
              </div>
            </div>

            <div className="card">
              <h4 style={{ color: "#0f4c81", marginBottom: "10px" }}>How It Is Calculated</h4>
              <div style={{ display: "grid", gap: "10px" }}>
                {results.calculation_steps.map((step) => (
                  <div key={step.step} style={{ display: "flex", justifyContent: "space-between", gap: "12px", padding: "12px 14px", borderRadius: "12px", background: "#f7fbff" }}>
                    <div>
                      <strong>{step.step}</strong>
                      <div style={{ color: "#5d6778", fontSize: "0.92rem" }}>{step.formula}</div>
                    </div>
                    <div style={{ color: "#0f4c81", fontWeight: 700 }}>
                      {step.unit === "INR" ? formatINR(step.value) : `${step.value} ${step.unit}`}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="card">
              <h4 style={{ color: "#0f4c81", marginBottom: "10px" }}>Baseline vs Scenario Load Curve</h4>
              <p style={{ marginTop: 0, color: "#5d6778" }}>
                Compare the original forecast with the adjusted plan to see where the savings actually happen.
              </p>
              <Chart
                labels={chartData.labels}
                values={chartData.scenarioValues}
                datasetLabel="Scenario energy (kWh)"
                borderColor="#166534"
                backgroundColor="rgba(22, 101, 52, 0.18)"
                chartType="line"
                extraDatasets={[
                  {
                    label: "Baseline energy (kWh)",
                    data: chartData.baselineValues,
                    borderColor: "#0f4c81",
                    backgroundColor: "rgba(15, 76, 129, 0.08)",
                    tension: 0.35,
                    fill: false,
                    pointRadius: 2,
                    pointHoverRadius: 4,
                    borderWidth: 2,
                  },
                ]}
              />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
              <div className="card">
                <h4 style={{ color: "#0f4c81", marginBottom: "10px" }}>Monthly Projection</h4>
                <p>Baseline monthly cost: <strong>{formatINR(results.monthly_projection?.baseline_cost_inr || 0)}</strong></p>
                <p>Scenario monthly cost: <strong>{formatINR(results.monthly_projection?.scenario_cost_inr || 0)}</strong></p>
                <p>Fixed charge: <strong>{formatINR(results.monthly_projection?.fixed_charge_inr || 0)}</strong></p>
                <p>Total bill: <strong>{formatINR(results.monthly_projection?.total_bill_inr || 0)}</strong></p>
                <p>Monthly savings: <strong>{formatINR(results.monthly_projection?.savings_inr || 0)}</strong></p>
              </div>
              <div className="card">
                <h4 style={{ color: "#0f4c81", marginBottom: "10px" }}>Yearly Projection</h4>
                <p>Baseline yearly cost: <strong>{formatINR(results.yearly_projection?.baseline_cost_inr || 0)}</strong></p>
                <p>Scenario yearly cost: <strong>{formatINR(results.yearly_projection?.scenario_cost_inr || 0)}</strong></p>
                <p>Fixed charge: <strong>{formatINR(results.yearly_projection?.fixed_charge_inr || 0)}</strong></p>
                <p>Total bill: <strong>{formatINR(results.yearly_projection?.total_bill_inr || 0)}</strong></p>
                <p>Yearly savings: <strong>{formatINR(results.yearly_projection?.savings_inr || 0)}</strong></p>
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
              <div className="card">
                <h4 style={{ color: "#0f4c81", marginBottom: "10px" }}>Resilience Metrics</h4>
                <p>Baseline peak window: <strong>{results.resilience_metrics?.baseline_peak_window}</strong></p>
                <p>Scenario peak window: <strong>{results.resilience_metrics?.scenario_peak_window}</strong></p>
                <p>Baseline peak energy: <strong>{results.resilience_metrics?.baseline_peak_window_kwh} kWh</strong></p>
                <p>Scenario peak energy: <strong>{results.resilience_metrics?.scenario_peak_window_kwh} kWh</strong></p>
                <p>Baseline load factor: <strong>{results.resilience_metrics?.baseline_load_factor}</strong></p>
                <p>Scenario load factor: <strong>{results.resilience_metrics?.scenario_load_factor}</strong></p>
                <p>Self-consumption ratio: <strong>{results.resilience_metrics?.self_consumption_ratio}%</strong></p>
              </div>
              <div className="card">
                <h4 style={{ color: "#0f4c81", marginBottom: "10px" }}>Key Insights</h4>
                <ul>
                  {(results.insights || []).map((insight) => (
                    <li key={insight}>{insight}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="card">
              <h4 style={{ color: "#0f4c81", marginBottom: "10px" }}>Phase Savings Breakdown</h4>
              <div style={{ maxHeight: "260px", overflowY: "auto", border: "1px solid #e5eef8", borderRadius: "12px" }}>
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead style={{ background: "#f4f9ff" }}>
                    <tr>
                      <th style={{ textAlign: "left", padding: "10px" }}>Phase</th>
                      <th style={{ textAlign: "left", padding: "10px" }}>Baseline</th>
                      <th style={{ textAlign: "left", padding: "10px" }}>Scenario</th>
                      <th style={{ textAlign: "left", padding: "10px" }}>Saved kWh</th>
                      <th style={{ textAlign: "left", padding: "10px" }}>Saved INR</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(results.phase_breakdown || []).map((row) => (
                      <tr key={row.phase} style={{ borderTop: "1px solid #edf2f7" }}>
                        <td style={{ padding: "10px" }}>{row.phase}</td>
                        <td style={{ padding: "10px" }}>{row.baseline_kwh}</td>
                        <td style={{ padding: "10px" }}>{row.scenario_kwh}</td>
                        <td style={{ padding: "10px" }}>{row.saved_kwh}</td>
                        <td style={{ padding: "10px" }}>{formatINR(row.saved_inr)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="card">
              <h4 style={{ color: "#0f4c81", marginBottom: "10px" }}>Hourly Comparison Table</h4>
              <div style={{ maxHeight: "320px", overflowY: "auto", border: "1px solid #e5eef8", borderRadius: "12px" }}>
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead style={{ background: "#f4f9ff" }}>
                    <tr>
                      <th style={{ textAlign: "left", padding: "10px" }}>Time</th>
                      <th style={{ textAlign: "left", padding: "10px" }}>Baseline</th>
                      <th style={{ textAlign: "left", padding: "10px" }}>Scenario</th>
                      <th style={{ textAlign: "left", padding: "10px" }}>Saved kWh</th>
                      <th style={{ textAlign: "left", padding: "10px" }}>Saved INR</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.comparison_table.map((row, index) => (
                      <tr key={`${row.time}-${index}`} style={{ borderTop: "1px solid #edf2f7" }}>
                        <td style={{ padding: "10px" }}>{new Date(row.time).toLocaleString()}</td>
                        <td style={{ padding: "10px" }}>{row.baseline_kwh}</td>
                        <td style={{ padding: "10px" }}>{row.scenario_kwh}</td>
                        <td style={{ padding: "10px" }}>{row.saved_kwh}</td>
                        <td style={{ padding: "10px" }}>{formatINR(row.saved_inr)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

export default Simulation;
