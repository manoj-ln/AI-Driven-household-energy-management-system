import React, { useEffect, useMemo, useState } from "react";
import Home from "./pages/Home";
import Analytics from "./pages/Analytics";
import Predictions from "./pages/Predictions";
import IntelligenceHub from "./pages/IntelligenceHub";
import EnergyStudio from "./pages/EnergyStudio";
import Explainability from "./pages/Explainability";
import DeviceControl from "./components/DeviceControl";
import Optimization from "./components/Optimization";
import Simulation from "./components/Simulation";
import EnergyIngestForm from "./components/EnergyIngestForm";
import Chatbot from "./components/Chatbot";
import { EnergyProvider } from "./context/EnergyContext";
import { getCurrentUser, loginUser, registerUser, setAuthToken, updateCurrentUser } from "./services/apiService";

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
          setMessage("Registration failed. Please try a different identifier.");
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
        setMessage("Login failed. Check identifier/password.");
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

  useEffect(() => {
    const hash = window.location.hash.replace("#", "");
    if (hash) {
      const viewMap = {
        dashboard: "dashboard",
        analytics: "analytics",
        predictions: "predictions",
        explainability: "explainability",
        intelligence: "intelligence",
        studio: "studio",
        "device-control": "device-control",
        optimization: "optimization",
        simulation: "simulation",
        "data-input": "data-input",
      };
      if (viewMap[hash]) {
        setCurrentView(viewMap[hash]);
      }
    }
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
      case "studio":
        return <EnergyStudio />;
      case "device-control":
        return <DeviceControl />;
      case "optimization":
        return <Optimization />;
      case "simulation":
        return <Simulation />;
      case "data-input":
        return <EnergyIngestForm />;
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

  return (
    <div style={{ fontFamily: "'Trebuchet MS', 'Segoe UI', sans-serif", background: "radial-gradient(circle at top, #eef5ff 0%, #dfeaf7 45%, #cfdcec 100%)", minHeight: "100vh", animation: "fadeIn 1s ease-in-out" }}>
      <style>
        {`
          @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
          }
          @keyframes slideIn {
            from { transform: translateX(-100%); }
            to { transform: translateX(0); }
          }
          @keyframes welcomePulse {
            from { transform: scale(0.98); opacity: 0.92; }
            to { transform: scale(1.02); opacity: 1; }
          }
          .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.3s ease, box-shadow 0.3s ease; }
          .card:hover { transform: translateY(-5px); box-shadow: 0 8px 15px rgba(0,0,0,0.2); }
          .btn { padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; transition: all 0.3s ease; font-weight: bold; }
          .btn:hover { transform: scale(1.05); }
          .btn-primary { background: #007bff; color: white; }
          .btn-success { background: #28a745; color: white; }
          .btn-danger { background: #dc3545; color: white; }
          .form-group { margin-bottom: 15px; }
          .form-label { display: block; margin-bottom: 5px; font-weight: bold; }
          .form-input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; transition: border-color 0.3s ease; box-sizing: border-box; }
          .form-input:focus { outline: none; border-color: #007bff; box-shadow: 0 0 5px rgba(0, 123, 255, 0.5); }
          .loading { display: inline-block; width: 20px; height: 20px; border: 3px solid #f3f3f3; border-top: 3px solid #3498db; border-radius: 50%; animation: spin 1s linear infinite; }
          @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        `}
      </style>

      <button
        onClick={() => setProfileOpen((prev) => !prev)}
        style={{ position: "fixed", top: "18px", left: "18px", zIndex: 1100, width: "56px", height: "56px", borderRadius: "18px", border: "none", background: "linear-gradient(135deg, #0b2b45 0%, #1a74b8 100%)", color: "white", fontWeight: 800, cursor: "pointer", boxShadow: "0 12px 30px rgba(15,76,129,0.28)" }}
        title="Profile"
      >
        AI
      </button>

      {profileOpen ? (
        <div style={{ position: "fixed", top: "84px", left: "18px", zIndex: 1100, width: "290px", borderRadius: "22px", padding: "18px", background: "linear-gradient(180deg, rgba(11,43,69,0.98) 0%, rgba(19,81,133,0.96) 100%)", color: "white", boxShadow: "0 20px 40px rgba(8,37,61,0.32)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "12px" }}>
            <div style={{ width: "52px", height: "52px", borderRadius: "16px", display: "grid", placeItems: "center", background: "rgba(255,255,255,0.18)", fontWeight: 800, fontSize: "1.1rem" }}>AI</div>
            <div>
              <div style={{ fontSize: "0.72rem", textTransform: "uppercase", letterSpacing: "0.16em", opacity: 0.72 }}>Profile</div>
              <div style={{ fontWeight: 700 }}>{profileLabel}</div>
            </div>
          </div>
          <div style={{ lineHeight: 1.8, fontSize: "0.95rem" }}>
            <div>
              Name: {editProfile ? (
                <input
                  className="form-input"
                  style={{ marginTop: "4px" }}
                  value={profileForm.name}
                  onChange={(event) => setProfileForm((prev) => ({ ...prev, name: event.target.value }))}
                />
              ) : (profile?.name || "Not set")}
            </div>
            <div>
              Age: {editProfile ? (
                <input
                  className="form-input"
                  style={{ marginTop: "4px" }}
                  value={profileForm.age}
                  onChange={(event) => setProfileForm((prev) => ({ ...prev, age: event.target.value }))}
                />
              ) : (profile?.age || "Not set")}
            </div>
            <div>Contact: {profile?.identifier || "Not set"}</div>
            <div>BESCOM Energy Rate: Rs. 6.26 / unit</div>
            <div>Fixed Charge Ref: Rs. 120 / kW</div>
          </div>
          {profileStatus ? <div style={{ marginTop: "8px", fontSize: "0.9rem", opacity: 0.9 }}>{profileStatus}</div> : null}
          <div style={{ display: "flex", gap: "8px", marginTop: "14px" }}>
            {editProfile ? (
              <>
                <button onClick={handleProfileSave} style={{ background: "rgba(255,255,255,0.24)", color: "white", border: "none", borderRadius: "10px", padding: "8px 12px", cursor: "pointer" }}>Save</button>
                <button onClick={() => { setEditProfile(false); setProfileStatus(""); }} style={{ background: "rgba(255,255,255,0.14)", color: "white", border: "none", borderRadius: "10px", padding: "8px 12px", cursor: "pointer" }}>Cancel</button>
              </>
            ) : (
              <button onClick={() => setEditProfile(true)} style={{ background: "rgba(255,255,255,0.18)", color: "white", border: "none", borderRadius: "10px", padding: "8px 12px", cursor: "pointer" }}>Edit Profile</button>
            )}
            <button onClick={onLogout} style={{ background: "rgba(255,255,255,0.18)", color: "white", border: "none", borderRadius: "10px", padding: "8px 12px", cursor: "pointer" }}>Logout</button>
          </div>
        </div>
      ) : null}

      <header style={{ padding: "24px 20px", background: "linear-gradient(135deg, #0b2b45 0%, #104a7d 52%, #1a74b8 100%)", color: "white", textAlign: "center", animation: "slideIn 1s ease-out" }}>
        <h1 style={{ margin: 0, fontSize: "2.5em" }}>AI-Driven Household Energy Management System</h1>
        <p style={{ margin: "10px 0 0 0", fontSize: "1.12em" }}>for Consumption Analysis and Cost Optimization</p>
      </header>

      <nav style={{ padding: "15px 20px", background: "linear-gradient(135deg, #143d63 0%, #205d94 100%)", color: "white", display: "flex", justifyContent: "center", gap: "20px", flexWrap: "wrap", animation: "fadeIn 1.5s ease-in-out" }}>
        {[
          { label: "Dashboard", view: "dashboard" },
          { label: "Analytics", view: "analytics" },
          { label: "Predictions", view: "predictions" },
          { label: "Explainability", view: "explainability" },
          { label: "AI Brief", view: "intelligence" },
          { label: "Studio", view: "studio" },
          { label: "Device Control", view: "device-control" },
          { label: "Optimization", view: "optimization" },
          { label: "Simulation", view: "simulation" },
          { label: "Data Input", view: "data-input" },
        ].map((item, index) => (
          <button
            key={item.view}
            onClick={() => handleNavigation(item.view)}
            style={{
              color: "white",
              background: currentView === item.view ? "rgba(255,255,255,0.3)" : "transparent",
              fontWeight: "bold",
              padding: "10px 15px",
              borderRadius: "5px",
              border: "none",
              cursor: "pointer",
              transition: "background 0.3s ease",
              animation: `fadeIn ${1.5 + index * 0.1}s ease-in-out`,
              fontSize: "0.9em",
            }}
          >
            {item.label}
          </button>
        ))}
      </nav>

      <main style={{ padding: "20px", maxWidth: "1200px", margin: "0 auto" }}>
        {renderCurrentView()}
      </main>
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
      }
    };
    restoreSession();
  }, [token]);

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
    <EnergyProvider>
      {showSplash ? <SplashScreen /> : profile ? <AppShell profile={profile} onLogout={handleLogout} onProfileUpdated={handleProfileUpdated} /> : <LoginScreen onLogin={handleLogin} />}
    </EnergyProvider>
  );
}

export default App;
