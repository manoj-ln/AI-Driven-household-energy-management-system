import React, { useState, useEffect } from "react";
import { getDeviceCatalog } from "../services/apiService";

const STATIC_DEVICES = [
  { id: "1", name: "Smart Bulb", category: "Lighting", power: "9W", type: "smart_bulb", description: "Energy-efficient LED smart bulb with WiFi connectivity." },
  { id: "2", name: "Ceiling Fan", category: "Cooling", power: "75W", type: "fan", description: "Standard 3-blade ceiling fan for moderate cooling." },
  { id: "3", name: "Air Conditioner (1.5 Ton)", category: "Cooling", power: "1800W", type: "ac", description: "Inverter AC suitable for medium to large rooms." },
  { id: "4", name: "Refrigerator", category: "Kitchen", power: "180W", type: "fridge", description: "Double-door frost-free refrigerator." },
  { id: "5", name: "Microwave Oven", category: "Kitchen", power: "1000W", type: "microwave", description: "Convection microwave oven for fast cooking." },
  { id: "6", name: "Washing Machine", category: "Utility", power: "700W", type: "washing_machine", description: "Front-load fully automatic washing machine." },
  { id: "7", name: "LED TV (55 inch)", category: "Entertainment", power: "120W", type: "tv", description: "4K Ultra HD Smart LED TV." },
];

const DEVICE_COLORS = {
  smart_bulb: ["#fbbf24", "#fef3c7"],
  fan: ["#60a5fa", "#dbeafe"],
  ac: ["#38bdf8", "#e0f2fe"],
  fridge: ["#34d399", "#d1fae5"],
  microwave: ["#f87171", "#fee2e2"],
  washing_machine: ["#a78bfa", "#ede9fe"],
  tv: ["#1e293b", "#e2e8f0"],
  laptop: ["#6366f1", "#e0e7ff"],
  heater: ["#f97316", "#ffedd5"],
  kettle: ["#ef4444", "#fee2e2"],
  vacuum: ["#8b5cf6", "#f5f3ff"],
  console: ["#0ea5e9", "#e0f2fe"],
  speaker: ["#14b8a6", "#ccfbf1"],
  purifier: ["#10b981", "#d1fae5"],
  coffee: ["#92400e", "#fef3c7"],
  hair_dryer: ["#ec4899", "#fce7f3"],
  router: ["#3b82f6", "#dbeafe"],
  pc: ["#334155", "#e2e8f0"],
  lock: ["#0f4c81", "#dbeafe"],
  camera: ["#475569", "#e2e8f0"],
  dehumidifier: ["#0891b2", "#cffafe"],
  robot_vacuum: ["#7c3aed", "#ede9fe"],
  blanket: ["#be185d", "#fce7f3"],
  treadmill: ["#16a34a", "#dcfce7"],
};

function getDeviceIcon(type) {
  const icons = {
    smart_bulb: "💡", fan: "🌀", ac: "❄️", fridge: "🧊",
    microwave: "📡", washing_machine: "🫧", tv: "📺", laptop: "💻",
    heater: "🔥", kettle: "🫖", vacuum: "🧹", console: "🎮",
    speaker: "🔊", purifier: "🌿", coffee: "☕", hair_dryer: "💨",
    router: "📡", pc: "🖥️", lock: "🔐", camera: "📸",
    dehumidifier: "💧", robot_vacuum: "🤖", blanket: "🛌", treadmill: "🏃",
  };
  const lower = String(type).toLowerCase();
  if (lower.includes("ac")) return "❄️";
  if (lower.includes("fan")) return "🌀";
  if (lower.includes("light") || lower.includes("bulb")) return "💡";
  if (lower.includes("tv")) return "📺";
  if (lower.includes("fridge")) return "🧊";
  if (lower.includes("heater")) return "🔥";
  if (lower.includes("cook")) return "🍳";
  if (lower.includes("charge")) return "⚡";
  if (lower.includes("misc")) return "🔌";
  return icons[type] || "🔌";
}

function Device2DCard({ device }) {
  const type = device.type || "other";
  const [c1] = DEVICE_COLORS[type] || ["#0f4c81", "#dbeafe"];
  const icon = getDeviceIcon(type);
  return (
    <div style={{ width: "100%", height: "100%", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: "8px", background: "white", borderRadius: "16px", position: "relative", overflow: "hidden" }}>
      <div style={{ position: "absolute", inset: 0, backgroundImage: "radial-gradient(#cbd5e1 1px, transparent 1px)", backgroundSize: "20px 20px", opacity: 0.2 }} />
      <div style={{ width: "85px", height: "85px", borderRadius: "12px", background: "white", border: `2px solid ${c1}`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "2.5rem", boxShadow: `0 8px 16px ${c1}22`, position: "relative", zIndex: 1 }}>{icon}</div>
      <div style={{ fontSize: "0.7rem", fontWeight: 800, color: c1, letterSpacing: "0.1em", textTransform: "uppercase", position: "relative", zIndex: 1 }}>2D Schematic</div>
      <div style={{ position: "absolute", top: "20px", left: "20px", width: "30px", height: "1px", background: c1, opacity: 0.3 }} />
      <div style={{ position: "absolute", top: "20px", left: "20px", width: "1px", height: "30px", background: c1, opacity: 0.3 }} />
      <div style={{ position: "absolute", bottom: "20px", right: "20px", width: "30px", height: "1px", background: c1, opacity: 0.3 }} />
      <div style={{ position: "absolute", bottom: "20px", right: "20px", width: "1px", height: "30px", background: c1, opacity: 0.3 }} />
    </div>
  );
}

function DeviceLibrary() {
  const [devices, setDevices] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadCatalog() {
      setLoading(true);
      const data = await getDeviceCatalog();
      if (data && data.devices) {
        const enhanced = data.devices.map((d) => ({
          ...d,
          power: d.power || (d.category === "Cooling" ? "1500W" : "150W"),
          description: d.description || `Monitored ${d.name} in the active household energy system.`,
        }));
        setDevices(enhanced);
      } else {
        setDevices(STATIC_DEVICES);
      }
      setLoading(false);
    }
    loadCatalog();
  }, []);

  const filteredDevices = devices.filter((device) => {
    const matchesSearch = device.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = categoryFilter === "All" || device.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  const categories = ["All", ...new Set(devices.map((d) => d.category))];

  return (
    <div style={{ padding: "24px", maxWidth: "1280px", margin: "0 auto", animation: "fadeIn 0.5s ease-in-out" }}>
      <div style={{ textAlign: "center", marginBottom: "32px" }}>
        <h1 style={{ fontSize: "2.4rem", color: "#0f4c81", marginBottom: "12px", fontWeight: 800 }}>Appliance & Device Library</h1>
        <p style={{ color: "#64748b", fontSize: "1.05rem", maxWidth: "720px", margin: "0 auto", lineHeight: 1.6 }}>
          Browse monitored household appliances with 2D schematic views. Each entry shows category, rated power, and integration status with the active energy dataset.
        </p>
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: "16px", justifyContent: "space-between", alignItems: "center", background: "white", padding: "20px 24px", borderRadius: "20px", boxShadow: "0 12px 28px rgba(15, 76, 129, 0.06)", marginBottom: "24px", border: "1px solid rgba(15, 76, 129, 0.08)" }}>
        <div style={{ flex: "1", minWidth: "280px", position: "relative" }}>
          <span style={{ position: "absolute", left: "16px", top: "50%", transform: "translateY(-50%)", color: "#94a3b8" }}>🔍</span>
          <input
            type="text"
            placeholder="Search devices (AC, Fridge, Fan...)"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ width: "100%", padding: "14px 14px 14px 44px", borderRadius: "12px", border: "2px solid #f1f5f9", fontSize: "1rem", outline: "none", background: "#f8fafc", boxSizing: "border-box" }}
          />
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span style={{ fontSize: "0.9rem", fontWeight: 700, color: "#64748b" }}>Category</span>
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            style={{ padding: "12px 18px", borderRadius: "12px", border: "2px solid #f1f5f9", fontSize: "0.95rem", outline: "none", backgroundColor: "white", cursor: "pointer", fontWeight: 600, color: "#0f4c81" }}
          >
            {categories.map((cat) => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>
        <div style={{ padding: "10px 16px", borderRadius: "12px", background: "#f0f7ff", color: "#0f4c81", fontWeight: 700, fontSize: "0.9rem" }}>
          {loading ? "Loading..." : `${filteredDevices.length} device${filteredDevices.length !== 1 ? "s" : ""}`}
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "24px" }}>
        {filteredDevices.map((device) => {
          const [c1, c2] = DEVICE_COLORS[device.type] || ["#0f4c81", "#dbeafe"];
          return (
            <article
              key={device.id}
              style={{
                background: "white",
                borderRadius: "20px",
                padding: "0",
                boxShadow: "0 8px 24px rgba(0,0,0,0.04)",
                transition: "transform 0.25s ease, box-shadow 0.25s ease",
                cursor: "pointer",
                display: "flex",
                flexDirection: "column",
                border: "1px solid #e8eef5",
                overflow: "hidden",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "translateY(-6px)";
                e.currentTarget.style.boxShadow = "0 20px 40px rgba(15, 76, 129, 0.1)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow = "0 8px 24px rgba(0,0,0,0.04)";
              }}
              onClick={() => setSelectedDevice(device)}
            >
              <div style={{ height: "180px", background: "linear-gradient(135deg, #f8fafc 0%, #edf2f7 100%)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Device2DCard device={device} />
              </div>
              <div style={{ padding: "20px 22px 22px" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "10px", marginBottom: "10px" }}>
                  <h3 style={{ margin: 0, fontSize: "1.15rem", color: "#1e293b", fontWeight: 800 }}>{device.name}</h3>
                  <span style={{ background: c2, color: c1, padding: "4px 10px", borderRadius: "8px", fontSize: "0.72rem", fontWeight: 800, textTransform: "uppercase", whiteSpace: "nowrap" }}>{device.category}</span>
                </div>
                <table style={{ width: "100%", fontSize: "0.88rem", borderCollapse: "collapse", marginBottom: "12px" }}>
                  <tbody>
                    <tr>
                      <td style={{ color: "#64748b", padding: "4px 0", width: "40%" }}>Rated Power</td>
                      <td style={{ color: "#0f4c81", fontWeight: 700, padding: "4px 0" }}>{device.power}</td>
                    </tr>
                    <tr>
                      <td style={{ color: "#64748b", padding: "4px 0" }}>Type</td>
                      <td style={{ color: "#475569", padding: "4px 0", textTransform: "capitalize" }}>{(device.type || "other").replace(/_/g, " ")}</td>
                    </tr>
                    <tr>
                      <td style={{ color: "#64748b", padding: "4px 0" }}>View</td>
                      <td style={{ color: "#475569", padding: "4px 0" }}>2D Schematic</td>
                    </tr>
                  </tbody>
                </table>
                <p style={{ margin: 0, color: "#64748b", fontSize: "0.9rem", lineHeight: 1.55, display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical", overflow: "hidden" }}>
                  {device.description}
                </p>
              </div>
            </article>
          );
        })}
        {!loading && filteredDevices.length === 0 && (
          <div style={{ gridColumn: "1 / -1", textAlign: "center", padding: "40px", color: "#64748b" }}>
            <span style={{ fontSize: "2.5rem", display: "block", marginBottom: "10px" }}>🔍</span>
            <p style={{ fontSize: "1.05rem" }}>No devices found matching your search.</p>
          </div>
        )}
      </div>

      {selectedDevice && (() => {
        const [c1, c2] = DEVICE_COLORS[selectedDevice.type] || ["#0f4c81", "#dbeafe"];
        return (
          <div style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0, background: "rgba(0,0,0,0.55)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000, padding: "20px" }} onClick={() => setSelectedDevice(null)}>
            <div style={{ background: "white", borderRadius: "20px", maxWidth: "560px", width: "100%", overflow: "hidden", maxHeight: "90vh", animation: "fadeIn 0.3s ease", boxShadow: "0 24px 48px rgba(0,0,0,0.2)" }} onClick={(e) => e.stopPropagation()}>
              <div style={{ height: "200px", background: `linear-gradient(135deg, ${c2} 0%, ${c1}33 100%)`, display: "flex", alignItems: "center", justifyContent: "center", position: "relative" }}>
                <div style={{ fontSize: "5rem" }}>{getDeviceIcon(selectedDevice.type)}</div>
                <span style={{ position: "absolute", top: "14px", left: "16px", background: c1, color: "white", padding: "4px 12px", borderRadius: "16px", fontSize: "0.75rem", fontWeight: 700 }}>{selectedDevice.category}</span>
                <button type="button" onClick={() => setSelectedDevice(null)} style={{ position: "absolute", top: "14px", right: "14px", background: "white", border: "none", width: "34px", height: "34px", borderRadius: "50%", cursor: "pointer", fontSize: "1rem", boxShadow: "0 4px 10px rgba(0,0,0,0.12)" }}>✕</button>
              </div>
              <div style={{ padding: "24px 28px", overflowY: "auto" }}>
                <h2 style={{ margin: "0 0 16px 0", fontSize: "1.6rem", color: "#0f4c81" }}>{selectedDevice.name}</h2>
                <table style={{ width: "100%", borderCollapse: "collapse", marginBottom: "18px", fontSize: "0.95rem" }}>
                  <tbody>
                    <tr style={{ borderBottom: "1px solid #f1f5f9" }}>
                      <td style={{ padding: "10px 0", color: "#64748b", width: "38%" }}>Category</td>
                      <td style={{ padding: "10px 0", fontWeight: 600 }}>{selectedDevice.category}</td>
                    </tr>
                    <tr style={{ borderBottom: "1px solid #f1f5f9" }}>
                      <td style={{ padding: "10px 0", color: "#64748b" }}>Rated Power</td>
                      <td style={{ padding: "10px 0", fontWeight: 700, color: c1 }}>{selectedDevice.power}</td>
                    </tr>
                    <tr style={{ borderBottom: "1px solid #f1f5f9" }}>
                      <td style={{ padding: "10px 0", color: "#64748b" }}>Device Type</td>
                      <td style={{ padding: "10px 0", textTransform: "capitalize" }}>{(selectedDevice.type || "other").replace(/_/g, " ")}</td>
                    </tr>
                    <tr>
                      <td style={{ padding: "10px 0", color: "#64748b" }}>Visualization</td>
                      <td style={{ padding: "10px 0" }}>2D Schematic Blueprint</td>
                    </tr>
                  </tbody>
                </table>
                <h4 style={{ color: "#1e293b", margin: "0 0 8px 0", fontSize: "1rem" }}>Description</h4>
                <p style={{ color: "#475569", lineHeight: 1.65, fontSize: "0.95rem", margin: "0 0 16px 0" }}>
                  {selectedDevice.description} The {selectedDevice.name} is tracked in the AI household energy system at {selectedDevice.power} peak capacity.
                </p>
                <h4 style={{ color: "#1e293b", margin: "0 0 8px 0", fontSize: "1rem" }}>Smart Features</h4>
                <ul style={{ color: "#475569", lineHeight: 1.75, fontSize: "0.92rem", paddingLeft: "20px", margin: 0 }}>
                  <li><strong>AI Tracking:</strong> Monitored by the central prediction engine.</li>
                  <li><strong>Off-Peak Scheduling:</strong> Schedule during off-peak hours to reduce BESCOM bills.</li>
                  <li><strong>Anomaly Detection:</strong> Unusual usage flagged by backend analytics.</li>
                  <li><strong>Real-time Analytics:</strong> Historical data tracked for this device type.</li>
                </ul>
              </div>
            </div>
          </div>
        );
      })()}

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}} />
    </div>
  );
}

export default DeviceLibrary;
