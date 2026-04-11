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

const handleError = (error, endpoint) => {
  const message = error?.response?.data?.detail || error.message || "Request failed";
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

export async function sendChatMessage(message) {
  try {
    const response = await api.post("/chatbot/chat", null, {
      params: { message },
    });
    return response.data;
  } catch (error) {
    return handleError(error, "chatbot/chat");
  }
}
