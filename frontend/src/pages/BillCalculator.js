import React, { useState, useEffect } from "react";
import { calculateBill, getTariffReferences, formatINR } from "../services/apiService";

const CONNECTION_TYPES = [
  { label: "Residential", value: "residential", icon: "🏠" },
  { label: "Commercial", value: "commercial", icon: "🏢" },
  { label: "Industrial", value: "industrial", icon: "🏭" },
  { label: "Agriculture", value: "agriculture", icon: "🌾" },
];

const BILLING_PERIODS = [
  { label: "Monthly", value: "monthly" },
  { label: "Bi-monthly", value: "bi-monthly" },
];

const STATES = [
  "Karnataka (BESCOM)",
  "Karnataka (HESCOM)",
  "Karnataka (CESCOM)",
  "Karnataka (MESCOM)",
];

function BillCalculator() {
  const [form, setForm] = useState({
    state: "Karnataka (BESCOM)",
    connection_type: "residential",
    sanctioned_load_kw: "24",
    units_consumed_kwh: "1254",
    billing_period: "monthly",
    fppca_paise: "154",
    fy25_trueup_per_month: "541",
    gruha_jyothi_enrolled: true,
    gruha_jyothi_units: "100",
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [tariffRefs, setTariffRefs] = useState(null);

  const handleCalculate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const payload = {
        ...form,
        sanctioned_load_kw: parseFloat(form.sanctioned_load_kw) || 0,
        units_consumed_kwh: parseFloat(form.units_consumed_kwh) || 0,
        fppca_paise: form.fppca_paise ? parseFloat(form.fppca_paise) : null,
        fy25_trueup_per_month: form.fy25_trueup_per_month ? parseFloat(form.fy25_trueup_per_month) : null,
        gruha_jyothi_units: form.gruha_jyothi_units ? parseFloat(form.gruha_jyothi_units) : null,
        gruha_jyothi_enrolled: form.gruha_jyothi_enrolled === true || form.gruha_jyothi_enrolled === "true",
      };
      const data = await calculateBill(payload);
      if (!data || data.error) {
        setError(data?.error || "Calculation failed");
        setResult(null);
      } else {
        setResult(data);
        setError("");
      }
    } catch (err) {
      setError("Failed to calculate bill. Please check your input and try again.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleReset = () => {
    setForm({
      state: "Karnataka (BESCOM)",
      connection_type: "residential",
      sanctioned_load_kw: "24",
      units_consumed_kwh: "1254",
      billing_period: "monthly",
      fppca_paise: "154",
      fy25_trueup_per_month: "541",
      gruha_jyothi_enrolled: true,
      gruha_jyothi_units: "100",
    });
    setResult(null);
    setError("");
  };

  const inputStyle = {
    width: "100%",
    padding: "12px",
    border: "1px solid #e2e8f0",
    borderRadius: "8px",
    fontSize: "14px",
    boxSizing: "border-box",
    background: "#f8fafc",
  };

  const labelStyle = {
    display: "block",
    fontSize: "0.8rem",
    fontWeight: 600,
    color: "#475569",
    marginBottom: "6px",
  };

  return (
    <section style={{ marginBottom: "38px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px", flexWrap: "wrap", gap: "12px" }}>
        <h2 style={{ margin: 0 }}>
          ⚡ Electricity Bill Calculator
          <span style={{ display: "block", fontSize: "0.85rem", color: "#64748b", fontWeight: 400, marginTop: "4px" }}>
            Accurate bill estimates for Indian states
          </span>
        </h2>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px", alignItems: "start" }}>
        {/* Input Form */}
        <div style={{ background: "white", borderRadius: "20px", padding: "28px", boxShadow: "0 10px 25px rgba(0,0,0,0.05)" }}>
          <h3 style={{ margin: "0 0 20px 0", color: "#0f4c81" }}>Enter Your Details</h3>

          <form onSubmit={handleCalculate}>
            {/* State */}
            <div className="form-group" style={{ marginBottom: "20px" }}>
              <label style={labelStyle}>Select Your State *</label>
              <select
                className="form-input"
                style={inputStyle}
                value={form.state}
                onChange={(e) => handleChange("state", e.target.value)}
                required
              >
                {STATES.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>

            {/* Connection Type */}
            <div className="form-group" style={{ marginBottom: "20px" }}>
              <label style={labelStyle}>Connection Type *</label>
              <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
                {CONNECTION_TYPES.map((ct) => (
                  <button
                    key={ct.value}
                    type="button"
                    onClick={() => handleChange("connection_type", ct.value)}
                    style={{
                      flex: 1,
                      minWidth: "120px",
                      padding: "14px 12px",
                      border: form.connection_type === ct.value ? "2px solid #0f4c81" : "1px solid #e2e8f0",
                      borderRadius: "12px",
                      background: form.connection_type === ct.value ? "#eff4ff" : "#f8fafc",
                      cursor: "pointer",
                      textAlign: "center",
                      fontSize: "13px",
                      fontWeight: form.connection_type === ct.value ? 600 : 500,
                      color: form.connection_type === ct.value ? "#0f4c81" : "#64748b",
                      transition: "all 0.2s",
                    }}
                  >
                    <div style={{ fontSize: "1.4rem", marginBottom: "4px" }}>{ct.icon}</div>
                    {ct.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Sanctioned Load */}
            <div className="form-group" style={{ marginBottom: "20px" }}>
              <label style={labelStyle}>Sanctioned Load (kW)</label>
              <input
                type="number"
                step="0.1"
                min="0"
                className="form-input"
                style={inputStyle}
                value={form.sanctioned_load_kw}
                onChange={(e) => handleChange("sanctioned_load_kw", e.target.value)}
                placeholder="Enter sanctioned load"
              />
            </div>

            {/* Units Consumed */}
            <div className="form-group" style={{ marginBottom: "20px" }}>
              <label style={labelStyle}>Units Consumed (kWh) *</label>
              <input
                type="number"
                step="0.01"
                min="0"
                className="form-input"
                style={inputStyle}
                value={form.units_consumed_kwh}
                onChange={(e) => handleChange("units_consumed_kwh", e.target.value)}
                placeholder="Enter units consumed"
                required
              />
            </div>

            {/* Billing Period */}
            <div className="form-group" style={{ marginBottom: "20px" }}>
              <label style={labelStyle}>Billing Period *</label>
              <div style={{ display: "flex", gap: "10px" }}>
                {BILLING_PERIODS.map((bp) => (
                  <button
                    key={bp.value}
                    type="button"
                    onClick={() => handleChange("billing_period", bp.value)}
                    style={{
                      flex: 1,
                      padding: "12px",
                      border: form.billing_period === bp.value ? "2px solid #0f4c81" : "1px solid #e2e8f0",
                      borderRadius: "10px",
                      background: form.billing_period === bp.value ? "#eff4ff" : "#f8fafc",
                      cursor: "pointer",
                      fontSize: "14px",
                      fontWeight: form.billing_period === bp.value ? 600 : 500,
                      color: form.billing_period === bp.value ? "#0f4c81" : "#64748b",
                    }}
                  >
                    {bp.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Optional Bill Fields */}
            <hr style={{ border: "none", borderTop: "1px solid #e2e8f0", margin: "20px 0" }} />
            <p style={{ margin: "0 0 16px 0", fontSize: "0.8rem", color: "#94a3b8", fontStyle: "italic" }}>
              From Your Bill (optional — improves accuracy)
            </p>

            <div className="form-group" style={{ marginBottom: "20px" }}>
              <label style={labelStyle}>FPPCA (paise/unit)</label>
              <input
                type="number"
                step="0.1"
                min="0"
                className="form-input"
                style={inputStyle}
                value={form.fppca_paise}
                onChange={(e) => handleChange("fppca_paise", e.target.value)}
                placeholder="154"
              />
              <p style={{ margin: "4px 0 0 0", fontSize: "0.75rem", color: "#94a3b8" }}>
                Monthly fuel adjustment — printed on your bill as FPPCA (recent BESCOM months: 24–47 paise). Leave blank if unsure.
              </p>
            </div>

            <div className="form-group" style={{ marginBottom: "20px" }}>
              <label style={labelStyle}>FY25 True-up Charges (₹/month)</label>
              <input
                type="number"
                step="1"
                min="0"
                className="form-input"
                style={inputStyle}
                value={form.fy25_trueup_per_month}
                onChange={(e) => handleChange("fy25_trueup_per_month", e.target.value)}
                placeholder="541"
              />
              <p style={{ margin: "4px 0 0 0", fontSize: "0.75rem", color: "#94a3b8" }}>
                Fixed monthly instalment based on your FY2024-25 usage — copy the "FY25 True up Charges" line from your bill (billed May 2026 – Apr 2027). Leave blank if not shown.
              </p>
            </div>

            <div className="form-group" style={{ marginBottom: "20px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <input
                  type="checkbox"
                  id="gruha_jyothi_enrolled"
                  checked={form.gruha_jyothi_enrolled}
                  onChange={(e) => handleChange("gruha_jyothi_enrolled", e.target.checked)}
                  style={{ width: "18px", height: "18px", cursor: "pointer" }}
                />
                <label htmlFor="gruha_jyothi_enrolled" style={{ ...labelStyle, marginBottom: 0, cursor: "pointer" }}>
                  Gruha Jyothi free units (if enrolled)
                </label>
              </div>
              {form.gruha_jyothi_enrolled && (
                <input
                  type="number"
                  step="1"
                  min="0"
                  className="form-input"
                  style={{ ...inputStyle, marginTop: "10px" }}
                  value={form.gruha_jyothi_units}
                  onChange={(e) => handleChange("gruha_jyothi_units", e.target.value)}
                  placeholder="100"
                />
              )}
              <p style={{ margin: "4px 0 0 0", fontSize: "0.75rem", color: "#94a3b8" }}>
                Your household entitlement = your FY2022-23 average +10%, capped at 200 (printed on your bill). This is NOT a flat 200 for everyone. If usage exceeds entitlement, the entire bill becomes payable — no partial subsidy (cliff effect).
              </p>
            </div>

            <button
              type="submit"
              className="btn btn-primary"
              style={{ width: "100%", marginTop: "10px" }}
              disabled={loading}
            >
              {loading ? "Calculating..." : "⚡ Calculate My Bill"}
            </button>
          </form>
        </div>

        {/* Results Panel */}
        <div style={{ background: "white", borderRadius: "20px", padding: "28px", boxShadow: "0 10px 25px rgba(0,0,0,0.05)", minHeight: "500px" }}>
          {error ? (
            <div style={{ color: "#ef4444", padding: "16px", background: "#fef2f2", borderRadius: "8px" }}>{error}</div>
          ) : result ? (
            <>
              {/* Header */}
              <div style={{ textAlign: "center", marginBottom: "28px" }}>
                <h3 style={{ margin: "0 0 4px 0", color: "#64748b", fontSize: "0.85rem" }}>
                  {result.state} · {result.tariff_name} · Rates verified {result.tariff_reference?.rates_verified || "Jul 2026"}
                </h3>
                <div style={{ fontSize: "0.75rem", color: "#94a3b8", marginTop: "4px" }}>
                  {result.tariff_reference?.rate_verification_notes || ""}
                </div>
              </div>

              {/* Total */}
              <div style={{ textAlign: "center", marginBottom: "24px" }}>
                <p style={{ margin: "0 0 4px 0", fontSize: "0.8rem", color: "#64748b", textTransform: "uppercase", letterSpacing: "0.5px" }}>Total Amount Payable</p>
                <p style={{ fontSize: "2.8rem", fontWeight: 800, color: "#0f4c81", margin: 0 }}>{formatINR(result.total_amount_payable)}</p>
                <p style={{ margin: "4px 0 0 0", fontSize: "0.85rem", color: "#64748b" }}>Avg {result.average_rate_inr_per_kwh.toFixed(2)} /kWh</p>
              </div>

              {/* Slab Info */}
              {result.slab_info && (
                <div style={{ background: "#f8fafc", padding: "16px", borderRadius: "12px", marginBottom: "20px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem", marginBottom: "8px" }}>
                    <span style={{ color: "#64748b" }}>{result.slab_info.label}</span>
                    <span style={{ fontWeight: 600, color: "#0f4c81" }}>₹{result.slab_info.rate_inr_per_unit.toFixed(2)}/unit</span>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.85rem" }}>
                    <span style={{ color: "#64748b" }}>{result.slab_info.units} kWh</span>
                    <span style={{ fontWeight: 600 }}>{formatINR(result.slab_info.energy_charge_inr)}</span>
                  </div>
                </div>
              )}

              {/* Gruha Jyothi Warning */}
              {result.gruha_jyothi?.message && (
                <div style={{
                  background: result.gruha_jyothi.applies_this_month ? "#dcfce7" : "#fef3c7",
                  border: `1px solid ${result.gruha_jyothi.applies_this_month ? "#86efac" : "#fde68a"}`,
                  borderRadius: "10px",
                  padding: "12px 14px",
                  marginBottom: "18px",
                  fontSize: "0.82rem",
                  color: result.gruha_jyothi.applies_this_month ? "#166534" : "#92400e",
                }}>
                  ⚠️ {result.gruha_jyothi.message}
                </div>
              )}

              {/* Gruha Jyothi Cliff Effect (when enrolled and close to or over entitlement) */}
              {result.gruha_jyothi?.enrolled && result.gruha_jyothi?.entitlement_units && !result.gruha_jyothi?.applies_this_month && result.gruha_jyothi?.entitlement_units > 0 && (
                <div style={{ background: "#fffbeb", borderRadius: "12px", padding: "18px", marginBottom: "20px", border: "1px solid #fde68a" }}>
                  <h3 style={{ margin: "0 0 10px 0", color: "#92400e", fontSize: "0.95rem" }}>⚠️ Gruha Jyothi Cliff Effect</h3>
                  <p style={{ margin: "0 0 12px 0", fontSize: "0.78rem", color: "#92400e" }}>
                    Your entitlement is {result.gruha_jyothi.entitlement_units} units (your FY2022-23 average +10%, capped at 200). The subsidy is all-or-nothing.
                  </p>
                  <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.8rem" }}>
                    <thead>
                      <tr style={{ borderBottom: "1px solid #fde68a" }}>
                        <th style={{ textAlign: "left", padding: "6px 0", color: "#92400e" }}>Scenario</th>
                        <th style={{ textAlign: "right", padding: "6px 0", color: "#92400e" }}>Units used</th>
                        <th style={{ textAlign: "right", padding: "6px 0", color: "#92400e" }}>You pay</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td style={{ padding: "6px 0", color: "#92400e" }}>Within entitlement</td>
                        <td style={{ padding: "6px 0", textAlign: "right", color: "#16a34a" }}>{result.gruha_jyothi.entitlement_units} units</td>
                        <td style={{ padding: "6px 0", textAlign: "right", color: "#16a34a" }}>₹57.75</td>
                      </tr>
                      <tr>
                        <td style={{ padding: "6px 0", color: "#92400e" }}>One unit over</td>
                        <td style={{ padding: "6px 0", textAlign: "right", color: "#dc2626" }}>{result.gruha_jyothi.entitlement_units + 1} units</td>
                        <td style={{ padding: "6px 0", textAlign: "right", color: "#dc2626" }}>{formatINR(result.bill_breakdown.energy_charges_inr + result.bill_breakdown.fixed_charges_inr + result.bill_breakdown.electricity_tax_inr).replace(/[^\d.,]/g, "")}</td>
                      </tr>
                    </tbody>
                  </table>
                  <p style={{ margin: "8px 0 0 0", fontSize: "0.72rem", color: "#92400e" }}>
                    That single extra unit costs nearly ₹1,377. Staying under your entitlement is the single most valuable action for your bill.
                  </p>
                </div>
              )}

              {/* Bill Breakdown */}
              <div>
                <h3 style={{ margin: "0 0 14px 0", color: "#0f4c81", fontSize: "1rem" }}>Bill Breakdown</h3>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
                  <thead>
                    <tr style={{ borderBottom: "2px solid #e2e8f0" }}>
                      <th style={{ textAlign: "left", padding: "8px 0", color: "#64748b", fontWeight: 600 }}>Component</th>
                      <th style={{ textAlign: "right", padding: "8px 0", color: "#64748b", fontWeight: 600 }}>Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr><td style={{ padding: "8px 0", color: "#334155" }}>⚡ Energy Charges</td><td style={{ padding: "8px 0", textAlign: "right" }}>{formatINR(result.bill_breakdown.energy_charges_inr)}</td></tr>
                    <tr><td style={{ padding: "8px 0", color: "#334155" }}>📋 Fixed Charges</td><td style={{ padding: "8px 0", textAlign: "right" }}>{formatINR(result.bill_breakdown.fixed_charges_inr)}</td></tr>
                    <tr><td style={{ padding: "8px 0", color: "#334155" }}>⛽ Pension & Gratuity Surcharge ({result.tariff_reference?.png_surcharge || "35p/unit"})</td><td style={{ padding: "8px 0", textAlign: "right" }}>{formatINR(result.bill_breakdown.pension_and_gratuity_surcharge_inr)}</td></tr>
                    <tr><td style={{ padding: "8px 0", color: "#334155" }}>🏛️ Electricity Duty</td><td style={{ padding: "8px 0", textAlign: "right" }}>{formatINR(result.bill_breakdown.electricity_tax_inr)}</td></tr>
                    <tr><td style={{ padding: "8px 0", color: "#334155" }}>🧮 FPPCA — {form.fppca_paise}p × {form.units_consumed_kwh}u</td><td style={{ padding: "8px 0", textAlign: "right" }}>{formatINR(result.bill_breakdown.fppca_inr)}</td></tr>
                    <tr><td style={{ padding: "8px 0", color: "#334155" }}>🧮 FY25 True-up Charges</td><td style={{ padding: "8px 0", textAlign: "right" }}>{formatINR(result.bill_breakdown.fy25_trueup_charges_inr)}</td></tr>
                    {result.gruha_jyothi?.discount_inr > 0 && (
                      <tr><td style={{ padding: "8px 0", color: "#16a34a" }}>🧾 Gruha Jyothi Discount</td><td style={{ padding: "8px 0", textAlign: "right", color: "#16a34a" }}>-{formatINR(result.gruha_jyothi.discount_inr)}</td></tr>
                    )}
                  </tbody>
                  <tfoot>
                    <tr style={{ borderTop: "2px solid #e2e8f0" }}>
                      <td style={{ padding: "12px 0", fontWeight: 700 }}>Grand Total</td>
                      <td style={{ padding: "12px 0", textAlign: "right", fontWeight: 800, color: "#0f4c81" }}>{formatINR(result.total_amount_payable)}</td>
                    </tr>
                  </tfoot>
                </table>
              </div>

              {/* Action buttons */}
              <div style={{ display: "flex", gap: "10px", marginTop: "24px", marginBottom: "24px" }}>
                <button className="btn" style={{ flex: 1, background: "rgba(59,130,246,0.1)", color: "#0f4c81", border: "1px solid #bfdbfe" }}>
                  📄 Download PDF
                </button>
                <button className="btn" style={{ flex: 1, background: "rgba(59,130,246,0.1)", color: "#0f4c81", border: "1px solid #bfdbfe" }}>
                  📤 Share
                </button>
                <button className="btn" style={{ flex: 1, background: "rgba(59,130,246,0.1)", color: "#0f4c81", border: "1px solid #bfdbfe" }} onClick={handleReset}>
                  ↺ Recalculate
                </button>
              </div>

              {/* Smart Insights */}
              {result.smart_insights && (
                <div style={{ background: "white", borderRadius: "12px", padding: "18px", marginBottom: "20px", border: "1px solid #f0f2f5" }}>
                  <h3 style={{ margin: "0 0 14px 0", color: "#0f4c81", fontSize: "1rem" }}>💡 Smart Insights</h3>
                  <p style={{ margin: "0 0 12px 0", fontSize: "0.8rem", color: "#64748b" }}>Personalized tips to reduce your electricity bill</p>
                  <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                    {result.smart_insights.map((insight, idx) => (
                      <div key={idx} style={{ display: "flex", gap: "8px", fontSize: "0.85rem", color: "#334155" }}>
                        <span>{insight.includes("LED") ? "💡" : insight.includes("AC") ? "❄️" : insight.includes("Solar") ? "☀️" : "⚡"}</span>
                        <span>{insight}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* 6-Month Forecast */}
              {result.six_month_forecast && (
                <div style={{ marginBottom: "20px" }}>
                  <h3 style={{ margin: "0 0 14px 0", color: "#0f4c81", fontSize: "1rem" }}>📈 6-Month Bill Forecast</h3>
                  <p style={{ margin: "0 0 12px 0", fontSize: "0.8rem", color: "#64748b" }}>Estimated bills based on seasonal patterns</p>
                  <div style={{ display: "flex", gap: "10px", overflowX: "auto", paddingBottom: "8px" }}>
                    {result.six_month_forecast.map((item) => (
                      <div key={item.month} style={{ minWidth: "120px", background: "#f8fafc", borderRadius: "10px", padding: "14px", textAlign: "center", flexShrink: "0" }}>
                        <p style={{ margin: "0 0 6px 0", fontSize: "0.85rem", fontWeight: 600, color: "#64748b" }}>{item.month}</p>
                        <p style={{ margin: 0, fontSize: "1.2rem", fontWeight: 700, color: "#0f4c81" }}>{formatINR(item.total_inr)}</p>
                        <p style={{ margin: "2px 0 0 0", fontSize: "0.75rem", color: "#94a3b8" }}>{item.units_kwh} kWh</p>
                      </div>
                    ))}
                  </div>
                  <div style={{ display: "flex", gap: "24px", marginTop: "14px", fontSize: "0.85rem", flexWrap: "wrap" }}>
                    <div><span style={{ color: "#64748b" }}>Annual Estimate:</span> <strong style={{ color: "#0f4c81" }}>{formatINR(result.annual_estimate_inr)}</strong></div>
                    <div><span style={{ color: "#64748b" }}>Peak Month:</span> <strong style={{ color: "#0f4c81" }}>{result.peak_month}</strong></div>
                    <div><span style={{ color: "#64748b" }}>Potential Savings:</span> <strong style={{ color: "#16a34a" }}>{formatINR(result.potential_savings_inr)}</strong></div>
                  </div>
                  <p style={{ margin: "8px 0 0 0", fontSize: "0.72rem", color: "#94a3b8", fontStyle: "italic" }}>
                    ⚠️ Tariff rates are typically revised in April (start of financial year). Forecast may vary after revision.
                  </p>
                </div>
              )}

              {/* Tariff Reference */}
              {result.tariff_reference && (
                <div style={{ background: "#f8fafc", borderRadius: "12px", padding: "18px" }}>
                  <h3 style={{ margin: "0 0 14px 0", color: "#0f4c81", fontSize: "1rem" }}>{result.tariff_reference.tariff_name} — Quick Reference</h3>
                  <p style={{ margin: "0 0 12px 0", fontSize: "0.8rem", color: "#64748b" }}>{result.tariff_reference.financial_year} · Effective {result.tariff_reference.effective_date}</p>
                  <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.82rem" }}>
                    <tbody>
                      <tr><td style={{ padding: "6px 0", color: "#475569" }}>⚡ Energy charge (flat, no slabs)</td><td style={{ padding: "6px 0", textAlign: "right" }}>{result.tariff_reference.energy_charge}</td></tr>
                      <tr><td style={{ padding: "6px 0", color: "#475569" }}>📋 Fixed charge</td><td style={{ padding: "6px 0", textAlign: "right" }}>{result.tariff_reference.fixed_charge}</td></tr>
                      <tr><td style={{ padding: "6px 0", color: "#475569" }}>🏛️ Pension & Gratuity surcharge</td><td style={{ padding: "6px 0", textAlign: "right" }}>{result.tariff_reference.png_surcharge}</td></tr>
                      <tr><td style={{ padding: "6px 0", color: "#475569" }}>🧾 Electricity tax</td><td style={{ padding: "6px 0", textAlign: "right" }}>{result.tariff_reference.electricity_tax}</td></tr>
                      <tr><td style={{ padding: "6px 0", color: "#475569" }}>⛽ FPPCA (varies monthly)</td><td style={{ padding: "6px 0", textAlign: "right" }}>{result.tariff_reference.fppca_note}</td></tr>
                      <tr><td style={{ padding: "6px 0", color: "#475569" }}>📈 FY25 True-up</td><td style={{ padding: "6px 0", textAlign: "right" }}>{result.tariff_reference.fy25_trueup_note}</td></tr>
                      <tr><td style={{ padding: "6px 0", color: "#475569" }}>Example</td><td style={{ padding: "6px 0", textAlign: "right" }}>{result.tariff_reference.example_250_units_2kw}</td></tr>
                    </tbody>
                  </table>
                </div>
              )}

              {result.state_info && (
                <div style={{ background: "#f8fafc", borderRadius: "12px", padding: "18px", marginBottom: "20px" }}>
                  <h3 style={{ margin: "0 0 12px 0", color: "#0f4c81", fontSize: "1rem" }}>🏛️ About {result.state_info.escoom_name}</h3>
                  <p style={{ margin: "0 0 10px 0", fontSize: "0.82rem", color: "#475569" }}>{result.state_info.about}</p>
                  <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.78rem" }}>
                    <tbody>
                      <tr><td style={{ padding: "3px 0", color: "#64748b" }}>Districts served</td><td style={{ padding: "3px 0", textAlign: "right" }}>{result.state_info.districts?.join(", ")}</td></tr>
                      <tr><td style={{ padding: "3px 0", color: "#64748b" }}>Licence area</td><td style={{ padding: "3px 0", textAlign: "right" }}>{result.state_info.licence_area_km2.toLocaleString()} sq km</td></tr>
                      <tr><td style={{ padding: "3px 0", color: "#64748b" }}>Population covered</td><td style={{ padding: "3px 0", textAlign: "right" }}>{result.state_info.population_covered}</td></tr>
                      <tr><td style={{ padding: "3px 0", color: "#64748b" }}>24x7 Helpline</td><td style={{ padding: "3px 0", textAlign: "right" }}>{result.state_info.contact?.helpline}</td></tr>
                      <tr><td style={{ padding: "3px 0", color: "#64748b" }}>WhatsApp</td><td style={{ padding: "3px 0", textAlign: "right" }}>{result.state_info.contact?.whatsapp}</td></tr>
                      <tr><td style={{ padding: "3px 0", color: "#64748b" }}>Email</td><td style={{ padding: "3px 0", textAlign: "right" }}>{result.state_info.contact?.email}</td></tr>
                      <tr><td style={{ padding: "3px 0", color: "#64748b" }}>Website</td><td style={{ padding: "3px 0", textAlign: "right" }}>{result.state_info.contact?.website}</td></tr>
                    </tbody>
                  </table>
                </div>
              )}

              {/* How to Reduce */}
              <div style={{ background: "#f0f9ff", borderRadius: "12px", padding: "18px", marginBottom: "20px", border: "1px solid #bae6fd" }}>
                <h3 style={{ margin: "0 0 14px 0", color: "#0c4a63", fontSize: "1rem" }}>💡 How to Reduce Your {result.state_info?.escoom_name || "BESCOM"} Bill</h3>
                <ul style={{ margin: 0, paddingLeft: "18px", fontSize: "0.82rem", color: "#475569", lineHeight: 1.7 }}>
                  <li>Review your sanctioned load. At ₹150 per kW per month, every unnecessary kW costs ₹1,800 a year whether you use it or not.</li>
                  {result.gruha_jyothi?.enrolled && result.gruha_jyothi?.entitlement_units && (
                    <li>If you are on Gruha Jyothi, track your units mid-month. Crossing your entitlement of {result.gruha_jyothi.entitlement_units} units by even one unit forfeits the entire subsidy for that month. It is a cliff, not a partial reduction — your entitlement is your FY2022-23 average +10%, capped at 200, not a flat 200 for everyone.</li>
                  )}
                  <li>Geysers and air conditioners dominate {result.state_info?.region_note || "Karnataka"} bills. A geyser timer and setting the AC to 24°C rather than 18°C can cut 20–25% of their consumption.</li>
                  <li>Replace remaining incandescent and CFL bulbs with LEDs — typically 20–30 units a month across a household.</li>
                  <li>Consider rooftop solar. {result.state_info?.escoom_name || "BESCOM"} offers a rebate of ₹25 per kW on fixed charges for domestic installations up to 10 kW, and PM Surya Ghar offers central subsidy.</li>
                  <li>Pay on time. Delayed payment attracts simple interest at 1% per month.</li>
                </ul>
              </div>

              {/* Documented Gap */}
              {result.documented_gap && (
                <div style={{ background: "#fffbeb", borderRadius: "10px", padding: "14px", marginBottom: "16px", border: "1px solid #fde68a", fontSize: "0.78rem", color: "#92400e" }}>
                  <strong>📝 Documented gap:</strong> {result.documented_gap}
                </div>
              )}

              {/* Sources */}
              <div style={{ background: "#f8fafc", borderRadius: "10px", padding: "12px 16px", marginBottom: "16px", fontSize: "0.72rem", color: "#64748b" }}>
                <strong>Sources:</strong> KERC Tariff Order 27.03.2025 (LT-1 FY2026-27) · KERC Order 18.03.2025 para (h) (P&G surcharge) · GoK Notification No. 24/19.07.2018 (electricity tax) · KERC APR Order 17.04.2026 (FY25 true-up) · KERC FPPCA Order 29.06.2026 · GoK Gruha Jyothi Verification FAQ Q11. Last verified: July 2026.
              </div>
              {result.verification_log && (
                <details style={{ marginTop: "18px" }}>
                  <summary style={{ cursor: "pointer", fontSize: "0.8rem", color: "#64748b", fontWeight: 600 }}>Show calculation details</summary>
                  <ul style={{ marginLeft: "18px", marginTop: "8px", fontSize: "0.78rem", color: "#64748b" }}>
                    {result.verification_log.map((log, idx) => (
                      <li key={idx}>{log}</li>
                    ))}
                  </ul>
                </details>
              )}
            </>
          ) : (
            <div style={{ textAlign: "center", color: "#94a3b8", padding: "60px 20px" }}>
              <div style={{ fontSize: "3rem", marginBottom: "12px" }}>⚡</div>
              <p style={{ margin: 0 }}>Enter your details and click "Calculate My Bill" to see your estimated electricity bill breakdown.</p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

export default BillCalculator;