import React, { useEffect, useState } from "react";
import { getOptimizationReport, formatINR } from "../services/apiService";

function Optimization() {
  const [report, setReport] = useState(null);

  useEffect(() => {
    async function loadReport() {
      const data = await getOptimizationReport();
      setReport(data);
    }
    loadReport();
  }, []);

  const safeReport = report
    ? {
        peak_hour: report.peak_hour || "N/A",
        daily_consumption: report.daily_consumption || 0,
        baseline_cost: report.baseline_cost || 0,
        optimized_cost: report.optimized_cost || 0,
        estimated_savings: report.estimated_savings || 0,
        tariff: {
          peak_rate_inr: report.tariff?.peak_rate_inr || 0,
          offpeak_rate_inr: report.tariff?.offpeak_rate_inr || 0,
          base_energy_rate_inr: report.tariff?.base_energy_rate_inr || 0,
          surcharge_rate_inr: report.tariff?.surcharge_rate_inr || 0,
          peak_energy_kwh: report.tariff?.peak_energy_kwh || 0,
          offpeak_energy_kwh: report.tariff?.offpeak_energy_kwh || 0,
          shoulder_energy_kwh: report.tariff?.shoulder_energy_kwh || 0,
          peak_cost_inr: report.tariff?.peak_cost_inr || 0,
          offpeak_cost_inr: report.tariff?.offpeak_cost_inr || 0,
          shoulder_cost_inr: report.tariff?.shoulder_cost_inr || 0,
          fixed_charge_per_kw_inr: report.tariff?.fixed_charge_per_kw_inr || 0,
          assumed_connected_load_kw: report.tariff?.assumed_connected_load_kw || 0,
        },
        recommendations: report.recommendations || [],
        opportunities: report.opportunities || [],
        cost_breakdown: report.cost_breakdown || [],
        action_plan: report.action_plan || [],
        cost_verification_log: report.cost_verification_log || [],
        monthly_projection: report.monthly_projection || {},
        annual_projection: report.annual_projection || {},
        savings_levers: report.savings_levers || [],
        scenario_comparison: report.scenario_comparison || [],
        hourly_strategy: report.hourly_strategy || [],
      }
    : null;

  return (
    <section style={{ marginBottom: "38px" }}>
      <h2>Cost Optimization</h2>
      {safeReport ? (
        <div style={{ display: "grid", gap: "20px" }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "16px" }}>
            <div className="card">
              <h3>Peak Window</h3>
              <p><strong>{safeReport.peak_hour}</strong></p>
            </div>
            <div className="card">
              <h3>Daily Consumption</h3>
              <p><strong>{safeReport.daily_consumption} kWh</strong></p>
            </div>
            <div className="card">
              <h3>Current Cost</h3>
              <p><strong>{formatINR(safeReport.baseline_cost)}</strong></p>
            </div>
            <div className="card">
              <h3>Optimized Cost</h3>
              <p><strong>{formatINR(safeReport.optimized_cost)}</strong></p>
            </div>
            <div className="card">
              <h3>Estimated Savings</h3>
              <p><strong>{formatINR(safeReport.estimated_savings)}</strong></p>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
            <div className="card">
              <h3>Tariff Analysis</h3>
              <p>Base Energy Rate: <strong>{formatINR(safeReport.tariff.base_energy_rate_inr)}</strong> / kWh</p>
              <p>Surcharge: <strong>{formatINR(safeReport.tariff.surcharge_rate_inr)}</strong> / kWh</p>
              <p>Peak Rate: <strong>{formatINR(safeReport.tariff.peak_rate_inr)}</strong> / kWh</p>
              <p>Off-Peak Rate: <strong>{formatINR(safeReport.tariff.offpeak_rate_inr)}</strong> / kWh</p>
              <p>Fixed Charge Reference: <strong>{formatINR(safeReport.tariff.fixed_charge_per_kw_inr)}</strong> / kW</p>
              <p>Assumed Connected Load: <strong>{safeReport.tariff.assumed_connected_load_kw} kW</strong></p>
              <p>Peak Energy: <strong>{safeReport.tariff.peak_energy_kwh} kWh</strong></p>
              <p>Off-Peak Energy: <strong>{safeReport.tariff.offpeak_energy_kwh} kWh</strong></p>
              <p>Shoulder Energy: <strong>{safeReport.tariff.shoulder_energy_kwh} kWh</strong></p>
              <p>Peak Cost: <strong>{formatINR(safeReport.tariff.peak_cost_inr)}</strong></p>
              <p>Off-Peak Cost: <strong>{formatINR(safeReport.tariff.offpeak_cost_inr)}</strong></p>
              <p>Shoulder Cost: <strong>{formatINR(safeReport.tariff.shoulder_cost_inr)}</strong></p>
            </div>
            <div className="card">
              <h3>Optimization Tips</h3>
              <ul>
                {safeReport.recommendations.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>
          </div>

          <div className="card">
            <h3>Device Opportunities</h3>
            <div style={{ maxHeight: "300px", overflowY: "auto", border: "1px solid #e5eef8", borderRadius: "12px" }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead style={{ background: "#f4f9ff" }}>
                  <tr>
                    <th style={{ textAlign: "left", padding: "10px" }}>Device</th>
                    <th style={{ textAlign: "left", padding: "10px" }}>Current kWh/day</th>
                    <th style={{ textAlign: "left", padding: "10px" }}>Optimized kWh/day</th>
                    <th style={{ textAlign: "left", padding: "10px" }}>Savings/day</th>
                  </tr>
                </thead>
                <tbody>
                  {safeReport.opportunities.map((item) => (
                    <tr key={item.device} style={{ borderTop: "1px solid #edf2f7" }}>
                      <td style={{ padding: "10px" }}>{item.device}</td>
                      <td style={{ padding: "10px" }}>{item.current_daily_kwh}</td>
                      <td style={{ padding: "10px" }}>{item.optimized_daily_kwh}</td>
                      <td style={{ padding: "10px" }}>{formatINR(item.daily_savings_inr)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
            <div className="card">
              <h3>Cost Breakdown</h3>
              <ul>
                {safeReport.cost_breakdown.map((item) => (
                  <li key={item.label}>
                    {item.label}: <strong>{formatINR(item.value)}</strong>
                  </li>
                ))}
              </ul>
              <h4>BESCOM Verification Log</h4>
              <ul>
                {safeReport.cost_verification_log.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
            <div className="card">
              <h3>Action Plan</h3>
              <ol>
                {safeReport.action_plan.map((step, index) => (
                  <li key={index}>{step.step}</li>
                ))}
              </ol>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
            <div className="card">
              <h3>Monthly Projection</h3>
              <p>Energy Charge: <strong>{formatINR(safeReport.monthly_projection.energy_charge_inr || 0)}</strong></p>
              <p>Fixed Charge: <strong>{formatINR(safeReport.monthly_projection.fixed_charge_inr || 0)}</strong></p>
              <p>Surcharge: <strong>{formatINR(safeReport.monthly_projection.surcharge_inr || 0)}</strong></p>
              <p>Total Bill: <strong>{formatINR(safeReport.monthly_projection.bill_total_inr || 0)}</strong></p>
              <p>Optimized Bill: <strong>{formatINR(safeReport.monthly_projection.optimized_bill_total_inr || 0)}</strong></p>
            </div>
            <div className="card">
              <h3>Annual Projection</h3>
              <p>Baseline Bill: <strong>{formatINR(safeReport.annual_projection.baseline_bill_inr || 0)}</strong></p>
              <p>Optimized Bill: <strong>{formatINR(safeReport.annual_projection.optimized_bill_inr || 0)}</strong></p>
              <p>Projected Savings: <strong>{formatINR(safeReport.annual_projection.savings_inr || 0)}</strong></p>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
            <div className="card">
              <h3>Savings Levers</h3>
              <ul>
                {safeReport.savings_levers.map((item) => (
                  <li key={item.label}>
                    <strong>{item.label}</strong>: {formatINR(item.daily_savings_inr)} per day
                    <div style={{ color: "#5d6778", marginTop: "4px" }}>{item.explanation}</div>
                  </li>
                ))}
              </ul>
            </div>
            <div className="card">
              <h3>Hourly Strategy</h3>
              <ul>
                {safeReport.hourly_strategy.map((item) => (
                  <li key={item.window}>
                    <strong>{item.window}</strong> ({item.hours}): {item.strategy}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="card">
            <h3>Scenario Comparison</h3>
            <div style={{ maxHeight: "280px", overflowY: "auto", border: "1px solid #e5eef8", borderRadius: "12px" }}>
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead style={{ background: "#f4f9ff" }}>
                  <tr>
                    <th style={{ textAlign: "left", padding: "10px" }}>Scenario</th>
                    <th style={{ textAlign: "left", padding: "10px" }}>Daily Cost</th>
                    <th style={{ textAlign: "left", padding: "10px" }}>Monthly Bill</th>
                    <th style={{ textAlign: "left", padding: "10px" }}>Peak Energy</th>
                  </tr>
                </thead>
                <tbody>
                  {safeReport.scenario_comparison.map((item) => (
                    <tr key={item.scenario} style={{ borderTop: "1px solid #edf2f7" }}>
                      <td style={{ padding: "10px" }}>{item.scenario}</td>
                      <td style={{ padding: "10px" }}>{formatINR(item.daily_cost_inr)}</td>
                      <td style={{ padding: "10px" }}>{formatINR(item.monthly_bill_inr)}</td>
                      <td style={{ padding: "10px" }}>{item.peak_energy_kwh} kWh</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      ) : (
        <p>Loading optimization report...</p>
      )}
    </section>
  );
}

export default Optimization;
