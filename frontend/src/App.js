import React, { useEffect, useMemo, useState } from "react";
import Home from "./pages/Home";
import Analytics from "./pages/Analytics";
import Predictions from "./pages/Predictions";
import IntelligenceHub from "./pages/IntelligenceHub";
import Explainability from "./pages/Explainability";
import BillCalculator from "./pages/BillCalculator";
import DeviceControl from "./components/DeviceControl";
import Optimization from "./components/Optimization";
import Simulation from "./components/Simulation";
import EnergyIngestForm from "./components/EnergyIngestForm";
import Chatbot from "./components/Chatbot";
import DeviceLibrary from "./pages/DeviceLibrary";
import { EnergyProvider } from "./context/EnergyContext";
import { getCurrentUser, loginUser, registerUser, setAuthToken, updateCurrentUser, getCurrentWeather } from "./services/apiService";

function LoginScreen({ onLogin }) {
  const [mode, setMode] = useState("signin");
  const [form, setForm] = useState({
    name: "",
    age: "",
    identifier: "",
    password: "",
    otp: "",
  });
  const [message, setMessage] = useState("");

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    const run = async () => {
      if (mode === "signup") {
        if (!form.name.trim() || !form.age.trim() || !form.identifier.trim() || !form.password.trim()) {
          setMessage("Please fill name, age, identifier, and password.");
          return;
        }
        const response = await registerUser({
          name: form.name.trim(),
          age: form.age.trim(),
          identifier: form.identifier.trim(),
          password: form.password.trim(),
        });
        if (!response?.token) {
          setMessage(response?.error || "Registration failed. Please try again.");
          return;
        }
        onLogin(response.profile, response.token);
        return;
      }

      const response = await loginUser({
        identifier: form.identifier.trim(),
        password: form.password.trim(),
      });
      if (!response?.token) {
        setMessage(response?.error || "Login failed. Check identifier/password.");
        return;
      }
      onLogin(response.profile, response.token);
    };
    run();
  };

  return (
    <div style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: "24px" }}>
      <div style={{ width: "min(980px, 100%)", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "20px" }}>
        <div style={{ padding: "34px", borderRadius: "28px", background: "linear-gradient(135deg, #08253d 0%, #0f4c81 52%, #1a74b8 100%)", color: "white", boxShadow: "0 20px 40px rgba(8,37,61,0.25)" }}>
          <p style={{ margin: "0 0 10px 0", letterSpacing: "0.18em", textTransform: "uppercase", opacity: 0.8 }}>Welcome</p>
          <h1 style={{ fontSize: "2.5rem", lineHeight: 1.15, marginBottom: "8px" }}>Smart AI</h1>
          <p style={{ fontSize: "1.15rem", marginTop: 0, marginBottom: "14px", opacity: 0.92 }}>AI-Driven Household Energy Management System for Consumption Analysis and Cost Optimization</p>
          <p style={{ lineHeight: 1.7, opacity: 0.92 }}>
            Secure sign-in uses backend FastAPI authentication with hashed passwords and session-style bearer tokens.
          </p>
        </div>
        <div style={{ background: "white", padding: "30px", borderRadius: "28px", boxShadow: "0 20px 40px rgba(15,76,129,0.14)" }}>
          <div style={{ display: "flex", gap: "10px", marginBottom: "16px" }}>
            <button className="btn" style={{ background: mode === "signin" ? "#0f4c81" : "#e8eef5", color: mode === "signin" ? "white" : "#0f4c81", flex: 1 }} onClick={() => { setMode("signin"); setMessage(""); }}>
              Sign In
            </button>
            <button className="btn" style={{ background: mode === "signup" ? "#0f4c81" : "#e8eef5", color: mode === "signup" ? "white" : "#0f4c81", flex: 1 }} onClick={() => { setMode("signup"); setMessage("New user detected. Please create a new password and verify OTP."); }}>
              Sign Up
            </button>
          </div>

          {message ? <p style={{ color: "#0f4c81", background: "#f2f8ff", padding: "10px 12px", borderRadius: "12px" }}>{message}</p> : null}

          <form onSubmit={handleSubmit}>
            {mode === "signup" ? (
              <>
                <div className="form-group">
                  <label className="form-label">Name</label>
                  <input name="name" className="form-input" value={form.name} onChange={handleChange} placeholder="Enter your name" />
                </div>
                <div className="form-group">
                  <label className="form-label">Age</label>
                  <input name="age" className="form-input" value={form.age} onChange={handleChange} placeholder="Enter your age" />
                </div>
              </>
            ) : null}

            <div className="form-group">
              <label className="form-label">Mobile Number or Gmail</label>
              <input name="identifier" className="form-input" value={form.identifier} onChange={handleChange} placeholder="example@gmail.com or 9876543210" />
            </div>
            <div className="form-group">
              <label className="form-label">{mode === "signup" ? "New Password" : "Password"}</label>
              <input name="password" type="password" className="form-input" value={form.password} onChange={handleChange} placeholder="Enter password" />
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: "100%" }}>
              {mode === "signup" ? "Create Account" : "Enter Project"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

function SplashScreen() {
  return (
    <div style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: "24px", background: "radial-gradient(circle at top, #eef5ff 0%, #dfeaf7 45%, #cfdcec 100%)" }}>
      <div style={{ textAlign: "center", animation: "welcomePulse 1.6s ease-in-out infinite alternate" }}>
        <div style={{ width: "110px", height: "110px", borderRadius: "28px", margin: "0 auto 20px auto", background: "linear-gradient(135deg, #0b2b45 0%, #1a74b8 100%)", boxShadow: "0 18px 40px rgba(15,76,129,0.22)" }} />
        <p style={{ letterSpacing: "0.18em", textTransform: "uppercase", color: "#0f4c81", marginBottom: "8px" }}>Welcome Screen</p>
        <h1 style={{ color: "#0b2b45", fontSize: "2.4rem", marginBottom: "4px" }}>Smart AI</h1>
        <p style={{ color: "#436279", fontSize: "1.1rem", marginTop: 0, marginBottom: "10px" }}>Efficient Home Energy Use and Cost Savings</p>
        <p style={{ color: "#5d6778", margin: 0 }}>Loading your smart home energy workspace...</p>
      </div>
    </div>
  );
}

function AppShell({ profile, onLogout, onProfileUpdated }) {
  const [currentView, setCurrentView] = useState("dashboard");
  const [profileOpen, setProfileOpen] = useState(false);
  const [editProfile, setEditProfile] = useState(false);
  const [profileForm, setProfileForm] = useState({ name: profile?.name || "", age: profile?.age || "" });
  const [profileStatus, setProfileStatus] = useState("");
  const [weather, setWeather] = useState(null);
  const [privacyMode, setPrivacyMode] = useState(true);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);

  // Generate a mock unique ID if one doesn't exist
  const uniqueId = useMemo(() => profile?.id || `USR-${Math.floor(Math.random() * 90000) + 10000}`, [profile]);

  useEffect(() => {
    const hash = window.location.hash.replace("#", "");
    if (hash) {
      const viewMap = {
        dashboard: "dashboard",
        analytics: "analytics",
        predictions: "predictions",
        explainability: "explainability",
        intelligence: "intelligence",
        "device-control": "device-control",
        optimization: "optimization",
        simulation: "simulation",
        "data-input": "data-input",
        "devices": "devices",
        "bill": "bill",
      };
      if (viewMap[hash]) {
        setCurrentView(viewMap[hash]);
      }
    }

    // Fetch live weather
    getCurrentWeather().then(data => {
      if (data && data.status === "success") {
        setWeather(data.temperature);
      }
    }).catch(err => console.error("Weather fetch error:", err));
  }, []);

  const handleNavigation = (view) => {
    setCurrentView(view);
    window.location.hash = view;
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case "dashboard":
        return <Home />;
      case "analytics":
        return <Analytics />;
      case "predictions":
        return <Predictions />;
      case "explainability":
        return <Explainability />;
      case "intelligence":
        return <IntelligenceHub />;
      case "device-control":
        return <DeviceControl />;
      case "optimization":
        return <Optimization />;
      case "simulation":
        return <Simulation />;
      case "data-input":
        return <EnergyIngestForm />;
        case "devices":
          return <DeviceLibrary />;
        case "bill":
          return <BillCalculator />;
      default:
        return <Home />;
    }
  };

  const profileLabel = useMemo(() => profile?.name || profile?.identifier || "Guest User", [profile]);

  useEffect(() => {
    setProfileForm({ name: profile?.name || "", age: profile?.age || "" });
  }, [profile]);

  const handleProfileSave = async () => {
    const response = await updateCurrentUser({
      name: profileForm.name.trim(),
      age: profileForm.age.trim(),
    });
    if (!response?.profile) {
      setProfileStatus("Profile update failed. Please check name and age.");
      return;
    }
    onProfileUpdated(response.profile);
    setProfileStatus("Profile updated successfully.");
    setEditProfile(false);
  };

  const navItems = [
    { label: "Dashboard", view: "dashboard", icon: "📊" },
    { label: "Data Input", view: "data-input", icon: "📝" },
    { label: "Analytics", view: "analytics", icon: "📈" },
    { label: "Predictions", view: "predictions", icon: "🔮" },
    { label: "Optimization", view: "optimization", icon: "⚡" },
    { label: "Explainability", view: "explainability", icon: "🧠" },
    { label: "Simulation", view: "simulation", icon: "⚙️" },
    { label: "Device Info", view: "devices", icon: "🔌" },
    { label: "Device Control", view: "device-control", icon: "🎛️" },
    { label: "AI Brief", view: "intelligence", icon: "🤖" },
    { label: "Bill Calculator", view: "bill", icon: "⚡" },
  ];

  return (
    <div style={{ fontFamily: "'Inter', 'Segoe UI', sans-serif", background: "#f0f4f8", height: "100vh", display: "flex", overflow: "hidden" }}>
      <style>
        {`
          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
          @keyframes fadeIn {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
          }
          .card { background: white; padding: 20px; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); transition: transform 0.3s ease, box-shadow 0.3s ease; }
          .card:hover { transform: translateY(-3px); box-shadow: 0 12px 30px rgba(0,0,0,0.08); }
          .btn { padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; transition: all 0.3s ease; font-weight: 600; }
          .btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
          .btn:active { transform: translateY(0); }
          .btn-primary { background: linear-gradient(135deg, #0f4c81 0%, #1a74b8 100%); color: white; }
          .btn-success { background: linear-gradient(135deg, #166534 0%, #22c55e 100%); color: white; }
          .form-input { width: 100%; padding: 12px; border: 1px solid #e2e8f0; border-radius: 8px; transition: border-color 0.3s ease; box-sizing: border-box; background: #f8fafc; }
          .form-input:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2); }
          .sidebar-link { display: flex; align-items: center; padding: 12px 20px; margin-bottom: 8px; border-radius: 12px; cursor: pointer; transition: all 0.2s ease; font-weight: 500; color: #cbd5e1; }
          .sidebar-link:hover { background: rgba(255,255,255,0.1); color: white; transform: translateX(4px); }
          .sidebar-link.active { background: linear-gradient(90deg, rgba(59,130,246,0.2) 0%, transparent 100%); color: white; border-left: 4px solid #3b82f6; }
        `}
      </style>

      {/* Advanced Sidebar */}
      <aside style={{ width: "280px", height: "100vh", overflowY: "auto", boxSizing: "border-box", background: "linear-gradient(180deg, #08253d 0%, #0a192f 100%)", color: "white", padding: "30px 20px", display: "flex", flexDirection: "column", boxShadow: "4px 0 24px rgba(0,0,0,0.1)", zIndex: 100 }}>
        <div style={{ marginBottom: "40px", padding: "0 10px" }}>
          <div style={{ width: "48px", height: "48px", borderRadius: "14px", background: "linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: "bold", fontSize: "1.2rem", marginBottom: "16px", boxShadow: "0 8px 16px rgba(59,130,246,0.3)" }}>AI</div>
          <h1 style={{ margin: 0, fontSize: "1.5rem", fontWeight: 700, letterSpacing: "-0.5px" }}>SmartHouse</h1>
          <p style={{ margin: "4px 0 0 0", fontSize: "0.85rem", color: "#94a3b8" }}>Energy Management</p>
        </div>

        <nav style={{ flex: 1, display: "flex", flexDirection: "column" }}>
          {navItems.map((item) => (
            <div
              key={item.view}
              onClick={() => handleNavigation(item.view)}
              className={`sidebar-link ${currentView === item.view ? "active" : ""}`}
            >
              <span style={{ marginRight: "12px", fontSize: "1.2rem" }}>{item.icon}</span>
              {item.label}
            </div>
          ))}
        </nav>

        <div style={{ marginTop: "auto", padding: "20px", background: "rgba(255,255,255,0.05)", borderRadius: "16px", cursor: "pointer", transition: "background 0.3s" }} onClick={() => setProfileOpen((prev) => !prev)}>
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <div style={{ width: "40px", height: "40px", borderRadius: "50%", background: "#1e293b", display: "grid", placeItems: "center", fontWeight: "bold" }}>
              {profileLabel.charAt(0).toUpperCase()}
            </div>
            <div style={{ overflow: "hidden" }}>
              <div style={{ fontWeight: 600, fontSize: "0.95rem", whiteSpace: "nowrap", textOverflow: "ellipsis", overflow: "hidden" }}>{profileLabel}</div>
              <div style={{ fontSize: "0.8rem", color: "#94a3b8" }}>View Profile</div>
            </div>
          </div>
        </div>
      </aside>

      {profileOpen && (
        <>
        <div style={{ position: "fixed", top: 0, left: 0, right: 0, bottom: 0, zIndex: 1050 }} onClick={() => { setProfileOpen(false); setEditProfile(false); setProfileStatus(""); }} />
        <div style={{ position: "fixed", bottom: "100px", left: "20px", zIndex: 1100, width: "360px", borderRadius: "20px", padding: "24px", background: "rgba(15, 23, 42, 0.95)", backdropFilter: "blur(12px)", color: "white", boxShadow: "0 24px 48px rgba(0,0,0,0.4)", border: "1px solid rgba(255,255,255,0.1)", animation: "fadeIn 0.3s ease", maxHeight: "80vh", overflowY: "auto" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
            <h3 style={{ margin: "0", color: "#3b82f6" }}>User Profile</h3>
            <span style={{ background: "linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)", color: "#451a03", padding: "4px 8px", borderRadius: "6px", fontSize: "0.75rem", fontWeight: "700", boxShadow: "0 2px 8px rgba(245,158,11,0.3)" }}>PRO TIER</span>
          </div>
          <div style={{ lineHeight: 1.8, fontSize: "0.95rem" }}>
            <div>
              Name: {editProfile ? (
                <input
                  className="form-input"
                  style={{ marginTop: "8px", background: "rgba(255,255,255,0.1)", color: "white", border: "1px solid rgba(255,255,255,0.2)" }}
                  value={profileForm.name}
                  onChange={(event) => setProfileForm((prev) => ({ ...prev, name: event.target.value }))}
                />
              ) : <strong style={{ marginLeft: "8px" }}>{profile?.name || "Not set"}</strong>}
            </div>
            <div style={{ marginTop: editProfile ? "12px" : "4px" }}>
              Age: {editProfile ? (
                <input
                  className="form-input"
                  style={{ marginTop: "8px", background: "rgba(255,255,255,0.1)", color: "white", border: "1px solid rgba(255,255,255,0.2)" }}
                  value={profileForm.age}
                  onChange={(event) => setProfileForm((prev) => ({ ...prev, age: event.target.value }))}
                />
              ) : <strong style={{ marginLeft: "8px" }}>{profile?.age || "Not set"}</strong>}
            </div>
            <div style={{ marginTop: "4px" }}>Contact: <strong style={{ marginLeft: "8px" }}>{profile?.identifier ? (privacyMode ? "***" + profile.identifier.slice(-4) : profile.identifier) : "Not set"}</strong></div>
            <div style={{ marginTop: "4px" }}>Unique ID: <span style={{ marginLeft: "8px", fontFamily: "monospace", color: "#34d399", background: "rgba(52, 211, 153, 0.1)", padding: "2px 6px", borderRadius: "4px" }}>{uniqueId}</span></div>
            
            <div style={{ display: "flex", gap: "10px", marginTop: "16px", marginBottom: "16px" }}>
              <div style={{ flex: 1, background: "rgba(255,255,255,0.05)", padding: "12px", borderRadius: "12px", textAlign: "center" }}>
                <div style={{ fontSize: "1.2rem", fontWeight: "700", color: "#3b82f6" }}>104</div>
                <div style={{ fontSize: "0.7rem", color: "#94a3b8", textTransform: "uppercase", letterSpacing: "0.5px" }}>Active Devices</div>
              </div>
              <div style={{ flex: 1, background: "rgba(255,255,255,0.05)", padding: "12px", borderRadius: "12px", textAlign: "center" }}>
                <div style={{ fontSize: "1.2rem", fontWeight: "700", color: "#34d399" }}>2.4M</div>
                <div style={{ fontSize: "0.7rem", color: "#94a3b8", textTransform: "uppercase", letterSpacing: "0.5px" }}>Data Points</div>
              </div>
            </div>

            <hr style={{ border: "none", borderTop: "1px solid rgba(255,255,255,0.1)", margin: "16px 0" }}/>
            <div style={{ display: "flex", justifyContent: "space-between", color: "#94a3b8", fontSize: "0.85rem", marginBottom: "6px" }}>
              <span>BESCOM Energy Rate</span>
              <strong style={{ color: "white" }}>Rs. 6.15 / unit</strong>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", color: "#94a3b8", fontSize: "0.85rem" }}>
              <span>Fixed Charge Ref</span>
              <strong style={{ color: "white" }}>Rs. 150 / kW</strong>
            </div>
            
            <hr style={{ border: "none", borderTop: "1px solid rgba(255,255,255,0.1)", margin: "16px 0" }}/>
            <h4 style={{ margin: "0 0 10px 0", color: "#3b82f6", display: "flex", alignItems: "center", gap: "8px" }}>
              <span>🔒</span> Privacy & Security
            </h4>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", background: "rgba(255,255,255,0.05)", padding: "10px", borderRadius: "8px", cursor: "pointer" }} onClick={() => setPrivacyMode(!privacyMode)}>
              <div style={{ fontSize: "0.85rem" }}>
                <strong>Data Privacy Mode</strong>
                <div style={{ color: "#94a3b8", fontSize: "0.75rem", marginTop: "2px" }}>Mask sensitive contact details</div>
              </div>
              <div style={{ width: "36px", height: "20px", background: privacyMode ? "#3b82f6" : "#475569", borderRadius: "10px", position: "relative", transition: "all 0.3s" }}>
                <div style={{ width: "16px", height: "16px", background: "white", borderRadius: "50%", position: "absolute", top: "2px", left: privacyMode ? "18px" : "2px", transition: "all 0.3s", boxShadow: "0 2px 4px rgba(0,0,0,0.2)" }} />
              </div>
            </div>

            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", background: "rgba(255,255,255,0.05)", padding: "10px", borderRadius: "8px", cursor: "pointer", marginTop: "8px" }} onClick={() => setNotificationsEnabled(!notificationsEnabled)}>
              <div style={{ fontSize: "0.85rem" }}>
                <strong>Real-time AI Alerts</strong>
                <div style={{ color: "#94a3b8", fontSize: "0.75rem", marginTop: "2px" }}>Receive anomaly notifications</div>
              </div>
              <div style={{ width: "36px", height: "20px", background: notificationsEnabled ? "#34d399" : "#475569", borderRadius: "10px", position: "relative", transition: "all 0.3s" }}>
                <div style={{ width: "16px", height: "16px", background: "white", borderRadius: "50%", position: "absolute", top: "2px", left: notificationsEnabled ? "18px" : "2px", transition: "all 0.3s", boxShadow: "0 2px 4px rgba(0,0,0,0.2)" }} />
              </div>
            </div>

            <div style={{ fontSize: "0.75rem", color: "#64748b", marginTop: "16px", display: "flex", alignItems: "center", gap: "6px" }}>
              <span>🛡️</span> All data is encrypted end-to-end with AES-256
            </div>
          </div>
          {profileStatus ? <div style={{ marginTop: "12px", fontSize: "0.9rem", color: "#34d399", background: "rgba(52, 211, 153, 0.1)", padding: "8px", borderRadius: "8px" }}>{profileStatus}</div> : null}
          <div style={{ display: "flex", gap: "12px", marginTop: "24px" }}>
            {editProfile ? (
              <>
                <button onClick={handleProfileSave} className="btn" style={{ flex: 1, background: "#3b82f6", color: "white" }}>Save</button>
                <button onClick={() => { setEditProfile(false); setProfileStatus(""); }} className="btn" style={{ flex: 1, background: "rgba(255,255,255,0.1)", color: "white" }}>Cancel</button>
              </>
            ) : (
              <button onClick={() => setEditProfile(true)} className="btn" style={{ flex: 1, background: "rgba(255,255,255,0.1)", color: "white" }}>Edit Profile</button>
            )}
            <button onClick={onLogout} className="btn" style={{ flex: 1, background: "#ef4444", color: "white" }}>Logout</button>
          </div>
        </div>
        </>
      )}

      {/* Main Content Area */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", height: "100vh", overflow: "hidden" }}>
        
        {/* Top Header */}
        <header style={{ padding: "24px 40px", display: "flex", justifyContent: "space-between", alignItems: "center", background: "white", boxShadow: "0 2px 10px rgba(0,0,0,0.02)", zIndex: 10 }}>
          <div>
            <h2 style={{ margin: 0, fontSize: "1.8rem", color: "#0f4c81" }}>{navItems.find(i => i.view === currentView)?.label || "Dashboard"}</h2>
            <p style={{ margin: "4px 0 0 0", color: "#64748b" }}>Manage and analyze your household energy consumption</p>
          </div>
          
          <div style={{ display: "flex", alignItems: "center", gap: "24px" }}>
            {/* Live Weather Widget */}
            <div style={{ display: "flex", alignItems: "center", gap: "10px", background: "#f8fafc", padding: "10px 16px", borderRadius: "12px", border: "1px solid #e2e8f0" }}>
              <span style={{ fontSize: "1.2rem" }}>🌤️</span>
              <div>
                <div style={{ fontSize: "0.75rem", color: "#64748b", textTransform: "uppercase", fontWeight: 600 }}>Live Weather</div>
                <div style={{ fontWeight: 700, color: "#0f4c81" }}>{weather !== null ? `${weather}°C` : "Loading..."}</div>
              </div>
            </div>
            
            <button style={{ background: "white", border: "1px solid #e2e8f0", width: "44px", height: "44px", borderRadius: "50%", cursor: "pointer", display: "grid", placeItems: "center", transition: "all 0.2s" }}>
              <span style={{ fontSize: "1.2rem" }}>🔔</span>
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main style={{ flex: 1, overflowY: "auto", padding: "30px 40px" }}>
          <div style={{ maxWidth: "1400px", margin: "0 auto", animation: "fadeIn 0.5s ease-out" }}>
            {renderCurrentView()}
          </div>
        </main>
      </div>

      <Chatbot />
    </div>
  );
}

function App() {
  const [showSplash, setShowSplash] = useState(true);
  const [token, setToken] = useState(() => window.localStorage.getItem("smart-ai-token") || "");
  const [profile, setProfile] = useState(() => {
    const saved = window.localStorage.getItem("smart-ai-profile");
    return saved ? JSON.parse(saved) : null;
  });

  useEffect(() => {
    const timer = window.setTimeout(() => setShowSplash(false), 1500);
    return () => window.clearTimeout(timer);
  }, []);

  useEffect(() => {
    setAuthToken(token);
    if (!token) {
      return;
    }
    const restoreSession = async () => {
      const data = await getCurrentUser();
      if (data?.user) {
        setProfile(data.user);
        window.localStorage.setItem("smart-ai-profile", JSON.stringify(data.user));
        return;
      }
      // Token is missing, invalid, or expired (401). Drop the stale session so
      // the app returns to the login screen instead of showing a broken
      // dashboard whose data calls keep failing with 401.
      setProfile(null);
      setToken("");
      window.localStorage.removeItem("smart-ai-profile");
      window.localStorage.removeItem("smart-ai-token");
      setAuthToken("");
    };
    restoreSession();
  }, [token]);

  useEffect(() => {
    const handleSessionExpired = () => {
      setProfile(null);
      setToken("");
    };
    window.addEventListener("smartAiSessionExpired", handleSessionExpired);
    return () => window.removeEventListener("smartAiSessionExpired", handleSessionExpired);
  }, []);

  const handleLogin = (profileData, authToken) => {
    const savedProfile = {
      name: profileData.name || "",
      age: profileData.age || "",
      identifier: profileData.identifier.trim(),
    };
    setProfile(savedProfile);
    setToken(authToken || "");
    window.localStorage.setItem("smart-ai-profile", JSON.stringify(savedProfile));
    if (authToken) {
      window.localStorage.setItem("smart-ai-token", authToken);
      setAuthToken(authToken);
    }
  };

  const handleLogout = () => {
    setProfile(null);
    setToken("");
    window.localStorage.removeItem("smart-ai-profile");
    window.localStorage.removeItem("smart-ai-token");
    setAuthToken("");
  };

  const handleProfileUpdated = (nextProfile) => {
    setProfile(nextProfile);
    window.localStorage.setItem("smart-ai-profile", JSON.stringify(nextProfile));
  };

  return (
    <EnergyProvider authenticated={Boolean(token && profile)}>
      {showSplash ? <SplashScreen /> : profile ? <AppShell profile={profile} onLogout={handleLogout} onProfileUpdated={handleProfileUpdated} /> : <LoginScreen onLogin={handleLogin} />}
    </EnergyProvider>
  );
}

export default App;
