import axios from "axios";

const API_BASE = (process.env.REACT_APP_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
  headers: {
    "Content-Type": "application/json",
    "X-Client-App": "energy-management-frontend",
  },
});

function toReadableErrorMessage(rawDetail, fallbackMessage = "Request failed") {
  if (!rawDetail) {
    return fallbackMessage;
  }
  if (typeof rawDetail === "string") {
    return rawDetail;
  }
  if (Array.isArray(rawDetail)) {
    const parts = rawDetail
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }
        if (item && typeof item === "object" && typeof item.msg === "string") {
          return item.msg;
        }
        return "";
      })
      .filter(Boolean);
    return parts.length ? parts.join("; ") : fallbackMessage;
  }
  if (typeof rawDetail === "object") {
    if (typeof rawDetail.msg === "string") {
      return rawDetail.msg;
    }
    try {
      return JSON.stringify(rawDetail);
    } catch (_error) {
      return fallbackMessage;
    }
  }
  return String(rawDetail);
}

export function setAuthToken(token) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
    return;
  }
  delete api.defaults.headers.common.Authorization;
}

const handleError = (error, endpoint) => {
  const message = toReadableErrorMessage(
    error?.response?.data?.detail,
    error?.message || "Request failed"
  );
  console.error(`API Error [${endpoint}]:`, message);
  return null;
};

export function formatINR(value) {
  const numeric = Number(value || 0);
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
  }).format(numeric);
}

export async function registerUser(payload) {
  try {
    const response = await api.post("/users/register", payload);
    return response.data;
  } catch (error) {
    const message = toReadableErrorMessage(
      error?.response?.data?.detail,
      error?.message || "Registration failed"
    );
    console.error(`API Error [users/register]:`, message);
    return { error: message };
  }
}

export async function loginUser(payload) {
  try {
    const response = await api.post("/users/login", payload);
    return response.data;
  } catch (error) {
    const message = toReadableErrorMessage(
      error?.response?.data?.detail,
      error?.message || "Login failed"
    );
    console.error(`API Error [users/login]:`, message);
    return { error: message };
  }
}

export async function getCurrentUser() {
  try {
    const response = await api.get("/users/me");
    return response.data;
  } catch (error) {
    return handleError(error, "users/me");
  }
}

export async function updateCurrentUser(payload) {
  try {
    const response = await api.put("/users/me", payload);
    return response.data;
  } catch (error) {
    return handleError(error, "users/me");
  }
}

export async function getNextHourPrediction() {
  try {
    const response = await api.get("/predictions/next-hour");
    return response.data;
  } catch (error) {
    return handleError(error, "predictions/next-hour");
  }
}

export async function getAvailableModels() {
  try {
    const response = await api.get("/predictions/models");
    return response.data;
  } catch (error) {
    return handleError(error, "predictions/models");
  }
}

export async function getForecast(hours = 24) {
  try {
    const response = await api.get(`/predictions/forecast/${hours}`);
    return response.data || [];
  } catch (error) {
    return handleError(error, "predictions/forecast/{hours}") || [];
  }
}

export async function getPredictionAnomalies(method = "zscore") {
  try {
    const response = await api.get(`/predictions/anomalies/${encodeURIComponent(method)}`);
    return response.data || [];
  } catch (error) {
    return handleError(error, "predictions/anomalies/{method}") || [];
  }
}

export async function getPredictionExplainability() {
  try {
    const response = await api.get("/predictions/explain-next");
    return response.data;
  } catch (error) {
    return handleError(error, "predictions/explain-next");
  }
}

export async function setModel(modelName) {
  try {
    const response = await api.post(`/predictions/models/${encodeURIComponent(modelName)}`);
    return response.data;
  } catch (error) {
    return handleError(error, "predictions/models/{modelName}");
  }
}

export async function getAnalyticsSummary() {
  try {
    const response = await api.get("/analytics/summary");
    return response.data;
  } catch (error) {
    return handleError(error, "analytics/summary");
  }
}

export async function getRecentUsage() {
  try {
    const response = await api.get("/analytics/recent");
    return response.data;
  } catch (error) {
    return handleError(error, "analytics/recent");
  }
}

export async function getDeviceBreakdown() {
  try {
    const response = await api.get("/analytics/device-breakdown");
    return response.data || [];
  } catch (error) {
    return handleError(error, "analytics/device-breakdown") || [];
  }
}

export async function getDeviceCatalog() {
  try {
    const response = await api.get("/analytics/catalog");
    return response.data;
  } catch (error) {
    return handleError(error, "analytics/catalog");
  }
}

export async function getHistoricalData(days = 7) {
  try {
    const response = await api.get(`/analytics/historical/${days}`);
    return response.data;
  } catch (error) {
    return handleError(error, "analytics/historical/{days}");
  }
}

export async function getDeviceTimeSeries(hours = 24) {
  try {
    const response = await api.get(`/analytics/device-series/${hours}`);
    return response.data || [];
  } catch (error) {
    return handleError(error, "analytics/device-series/{hours}") || [];
  }
}

export async function getDeviceTimeSeriesWindow(minutes = 1440) {
  try {
    const response = await api.get("/analytics/device-series", {
      params: { minutes },
    });
    return response.data || [];
  } catch (error) {
    return handleError(error, "analytics/device-series") || [];
  }
}

export async function getAnomalies() {
  try {
    const response = await api.get("/analytics/anomalies");
    return response.data || [];
  } catch (error) {
    return handleError(error, "analytics/anomalies") || [];
  }
}

export async function getEfficiencyScore() {
  try {
    const response = await api.get("/analytics/efficiency-score");
    return response.data;
  } catch (error) {
    return handleError(error, "analytics/efficiency-score");
  }
}

export async function getPatternInsights() {
  try {
    const response = await api.get("/analytics/pattern-insights");
    return response.data;
  } catch (error) {
    return handleError(error, "analytics/pattern-insights");
  }
}

export async function getDatasetMode() {
  try {
    const response = await api.get("/analytics/dataset-mode");
    return response.data;
  } catch (error) {
    return handleError(error, "analytics/dataset-mode");
  }
}

export async function setDatasetMode(mode) {
  try {
    const response = await api.post("/analytics/dataset-mode", { mode });
    return response.data;
  } catch (error) {
    return handleError(error, "analytics/dataset-mode");
  }
}

export async function getDatasets() {
  try {
    const response = await api.get("/analytics/datasets");
    return response.data;
  } catch (error) {
    return handleError(error, "analytics/datasets");
  }
}

export async function selectDataset(datasetName) {
  try {
    const response = await api.post("/analytics/datasets/select", {
      dataset_name: datasetName,
    });
    return response.data;
  } catch (error) {
    return handleError(error, "analytics/datasets/select");
  }
}

export async function getControlDevices() {
  try {
    const response = await api.get("/control/devices");
    return response.data || [];
  } catch (error) {
    return handleError(error, "control/devices") || [];
  }
}

export async function createControlDevice(payload) {
  try {
    const response = await api.post("/control/devices", payload);
    return response.data;
  } catch (error) {
    const message = error?.response?.data?.detail || error.message || "Request failed";
    console.error(`API Error [control/devices]:`, message);
    return { error: message };
  }
}

export async function updateControlDevice(deviceId, payload) {
  try {
    const response = await api.put(`/control/devices/${encodeURIComponent(deviceId)}`, payload);
    return response.data;
  } catch (error) {
    const message = error?.response?.data?.detail || error.message || "Request failed";
    console.error(`API Error [control/devices/{deviceId}]:`, message);
    return { error: message };
  }
}

export async function deleteControlDevice(deviceId) {
  try {
    const response = await api.delete(`/control/devices/${encodeURIComponent(deviceId)}`);
    return response.data;
  } catch (error) {
    const message = error?.response?.data?.detail || error.message || "Request failed";
    console.error(`API Error [control/devices/{deviceId}]:`, message);
    return { error: message };
  }
}

export async function toggleDevice(deviceName) {
  try {
    const response = await api.post(`/control/devices/${encodeURIComponent(deviceName)}/toggle`);
    return response.data;
  } catch (error) {
    return handleError(error, "control/devices/{deviceName}/toggle");
  }
}

export async function getOptimizationReport() {
  try {
    const response = await api.get("/optimization/report");
    return response.data;
  } catch (error) {
    return handleError(error, "optimization/report");
  }
}

export async function runSimulation(payload) {
  try {
    const response = await api.post("/simulation/run", payload);
    return response.data;
  } catch (error) {
    return handleError(error, "simulation/run");
  }
}

export async function ingestEnergyReading(reading) {
  try {
    const response = await api.post("/energy/ingest", reading);
    return response.data;
  } catch (error) {
    return handleError(error, "energy/ingest");
  }
}

export async function addManualReading(reading) {
  try {
    const response = await api.post("/manual/manual-reading", reading);
    return response.data;
  } catch (error) {
    return handleError(error, "manual/manual-reading");
  }
}

export async function createHouseholdPlan(payload) {
  try {
    const response = await api.post("/manual/household-plan", payload);
    return response.data;
  } catch (error) {
    return handleError(error, "manual/household-plan");
  }
}

export async function sendChatMessage(message, options = {}) {
  try {
    const params = { message };
    if (options.sessionId) {
      params.session_id = options.sessionId;
    }
    if (options.userName) {
      params.user_name = options.userName;
    }
    const response = await api.post("/chatbot/chat", null, {
      params,
    });
    return response.data;
  } catch (error) {
    return handleError(error, "chatbot/chat");
  }
}

export async function getCurrentWeather() {
  try {
    const lat = 12.9716;
    const lon = 77.5946;
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true`;
    const response = await fetch(url);
    if (response.ok) {
      const data = await response.json();
      return { status: "success", temperature: data.current_weather?.temperature || 25.0 };
    }
    return { status: "success", temperature: 25.0 };
  } catch (error) {
    console.error("Weather fetch failed:", error);
    return { status: "success", temperature: 25.0 };
  }
}
