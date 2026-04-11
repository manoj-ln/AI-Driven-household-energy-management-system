import React, { useEffect, useMemo, useState } from "react";
import { createHouseholdPlan, formatINR, getForecast, getHistoricalData } from "../services/apiService";
import { sanitizeText } from "../utils/helpers";
import Chart from "./Dashboard/Chart";

const APPLIANCE_GROUPS = [
  {
    label: "Lighting & Small Appliances",
    options: [
      { value: "led_bulb", label: "LED bulb", wattage: 9 },
      { value: "bulb", label: "Bulb", wattage: 60 },
      { value: "cfl_bulb", label: "CFL bulb", wattage: 20 },
      { value: "tube_light", label: "Tube light", wattage: 30 },
      { value: "ceiling_fan", label: "Ceiling fan", wattage: 75 },
      { value: "exhaust_fan", label: "Exhaust fan", wattage: 50 },
      { value: "table_fan", label: "Table fan", wattage: 45 },
      { value: "smart_light", label: "Smart light", wattage: 15 },
      { value: "night_lamp", label: "Night lamp", wattage: 7 },
      { value: "emergency_torch", label: "Emergency torch", wattage: 10 },
      { value: "extension_board", label: "Extension board", wattage: 1 },
    ],
  },
  {
    label: "Kitchen & Cooking",
    options: [
      { value: "refrigerator", label: "Refrigerator", wattage: 180 },
      { value: "deep_freezer", label: "Deep freezer", wattage: 300 },
      { value: "microwave_oven", label: "Microwave oven", wattage: 1000 },
      { value: "electric_kettle", label: "Electric kettle", wattage: 1500 },
      { value: "induction_cooktop", label: "Induction cooktop", wattage: 1800 },
      { value: "rice_cooker", label: "Rice cooker", wattage: 500 },
      { value: "mixer_grinder", label: "Mixer grinder", wattage: 500 },
      { value: "blender", label: "Blender", wattage: 300 },
      { value: "toaster", label: "Toaster", wattage: 1200 },
      { value: "coffee_maker", label: "Coffee maker", wattage: 900 },
      { value: "dishwasher", label: "Dishwasher", wattage: 1500 },
      { value: "water_purifier", label: "Water purifier", wattage: 30 },
      { value: "chimney", label: "Kitchen chimney", wattage: 180 },
      { value: "food_processor", label: "Food processor", wattage: 600 },
      { value: "juicer", label: "Juicer", wattage: 350 },
      { value: "sandwich_maker", label: "Sandwich maker", wattage: 800 },
      { value: "air_fryer", label: "Air fryer", wattage: 1500 },
      { value: "electric_oven", label: "Electric oven", wattage: 2000 },
      { value: "slow_cooker", label: "Slow cooker", wattage: 250 },
      { value: "dish_dryer", label: "Dish dryer", wattage: 900 },
    ],
  },
  {
    label: "Cleaning & Utility",
    options: [
      { value: "washing_machine", label: "Washing machine", wattage: 700 },
      { value: "clothes_dryer", label: "Clothes dryer", wattage: 1800 },
      { value: "vacuum_cleaner", label: "Vacuum cleaner", wattage: 1000 },
      { value: "robotic_vacuum", label: "Robotic vacuum", wattage: 40 },
      { value: "steam_cleaner", label: "Steam cleaner", wattage: 1200 },
      { value: "carpet_cleaner", label: "Carpet cleaner", wattage: 1500 },
      { value: "iron", label: "Iron", wattage: 1200 },
      { value: "water_heater", label: "Water heater", wattage: 2000 },
      { value: "pressure_washer", label: "Pressure washer", wattage: 2000 },
      { value: "shoe_polisher", label: "Shoe polisher", wattage: 75 },
      { value: "sewing_machine", label: "Sewing machine", wattage: 100 },
      { value: "inverter", label: "Inverter", wattage: 50 },
      { value: "water_pump", label: "Water pump", wattage: 750 },
      { value: "garage_door_motor", label: "Garage door motor", wattage: 350 },
      { value: "doorbell", label: "Doorbell", wattage: 5 },
    ],
  },
  {
    label: "Entertainment & Work",
    options: [
      { value: "led_tv_32_43", label: "LED TV (32-43 in)", wattage: 60 },
      { value: "oled_4k_tv_55_65", label: "OLED/4K TV (55-65 in)", wattage: 120 },
      { value: "projector", label: "Projector", wattage: 220 },
      { value: "home_theater_system", label: "Home theater system", wattage: 180 },
      { value: "set_top_box", label: "Set-top box", wattage: 20 },
      { value: "laptop", label: "Laptop", wattage: 65 },
      { value: "desktop_pc", label: "Desktop PC", wattage: 220 },
      { value: "gaming_pc", label: "Gaming PC", wattage: 600 },
      { value: "gaming_console", label: "Gaming console", wattage: 150 },
      { value: "wifi_router", label: "Wi-Fi router", wattage: 12 },
      { value: "printer", label: "Printer", wattage: 75 },
      { value: "scanner", label: "Scanner", wattage: 40 },
      { value: "portable_speaker", label: "Portable speaker", wattage: 20 },
      { value: "ebook_reader", label: "E-book reader", wattage: 3 },
      { value: "external_hard_drive", label: "External hard drive", wattage: 8 },
      { value: "monitor", label: "Monitor", wattage: 30 },
      { value: "tablet_charger", label: "Tablet charger", wattage: 12 },
      { value: "phone_charger", label: "Phone charger", wattage: 8 },
      { value: "speaker_system", label: "Speaker system", wattage: 100 },
      { value: "modem", label: "Modem", wattage: 10 },
    ],
  },
  {
    label: "Personal Care & Health",
    options: [
      { value: "hair_dryer", label: "Hair dryer", wattage: 1200 },
      { value: "hair_straightener", label: "Hair straightener", wattage: 50 },
      { value: "electric_shaver", label: "Electric shaver", wattage: 20 },
      { value: "electric_toothbrush", label: "Electric toothbrush", wattage: 3 },
      { value: "massager", label: "Massager", wattage: 35 },
      { value: "heater", label: "Heater", wattage: 1500 },
      { value: "room_heater", label: "Room heater", wattage: 1800 },
      { value: "air_conditioner_1_5_ton", label: "Air conditioner (1.5 ton)", wattage: 1800 },
      { value: "humidifier", label: "Humidifier", wattage: 40 },
      { value: "dehumidifier", label: "Dehumidifier", wattage: 300 },
      { value: "nebulizer", label: "Nebulizer", wattage: 80 },
      { value: "electric_blanket", label: "Electric blanket", wattage: 120 },
      { value: "treadmill", label: "Treadmill", wattage: 800 },
      { value: "exercise_bike", label: "Exercise bike", wattage: 100 },
      { value: "elliptical_trainer", label: "Elliptical trainer", wattage: 300 },
      { value: "cpap_machine", label: "CPAP machine", wattage: 60 },
      { value: "oxygen_concentrator", label: "Oxygen concentrator", wattage: 350 },
    ],
  },
  {
    label: "Smart Home & Security",
    options: [
      { value: "cctv_camera", label: "CCTV camera", wattage: 10 },
      { value: "smart_doorbell", label: "Smart doorbell", wattage: 8 },
      { value: "smart_lock", label: "Smart lock", wattage: 4 },
      { value: "smoke_detector", label: "Smoke detector", wattage: 3 },
      { value: "baby_monitor", label: "Baby monitor", wattage: 8 },
      { value: "motion_sensor_light", label: "Motion light", wattage: 10 },
      { value: "smart_thermostat", label: "Smart thermostat", wattage: 6 },
      { value: "smart_plug", label: "Smart plug", wattage: 2 },
      { value: "smart_curtains", label: "Smart curtains", wattage: 15 },
      { value: "smart_sprinkler_system", label: "Smart sprinkler system", wattage: 35 },
    ],
  },
  {
    label: "Miscellaneous & Essentials",
    options: [
      { value: "digital_camera", label: "Digital camera", wattage: 8 },
      { value: "smartwatch_charger", label: "Smartwatch charger", wattage: 3 },
      { value: "power_bank_charging", label: "Power bank charging", wattage: 8 },
      { value: "bluetooth_headphones", label: "Bluetooth headphones", wattage: 3 },
      { value: "digital_weighing_scale", label: "Digital weighing scale", wattage: 7 },
      { value: "aquarium_pump", label: "Aquarium pump", wattage: 25 },
      { value: "aquarium_heater", label: "Aquarium heater", wattage: 100 },
      { value: "study_lamp", label: "Study lamp", wattage: 12 },
      { value: "electric_drill", label: "Electric drill", wattage: 600 },
      { value: "glue_gun", label: "Glue gun", wattage: 40 },
      { value: "bread_maker", label: "Bread maker", wattage: 500 },
      { value: "camera_charger", label: "Camera charger", wattage: 10 },
      { value: "router_backup_ups", label: "Router backup UPS", wattage: 20 },
      { value: "ceiling_light_panel", label: "Ceiling light panel", wattage: 36 },
      { value: "decorative_light_strip", label: "Decorative light strip", wattage: 18 },
    ],
  },
];

const APPLIANCE_OPTIONS = APPLIANCE_GROUPS.flatMap((group) => group.options);
const DATASET_OPTIONS = [
  { value: "energy_last_24_hours.csv", label: "Energy Last 24 Hours CSV" },
  { value: "energy_peak_window.csv", label: "Energy Peak Window CSV" },
  { value: "energy_night_window.csv", label: "Energy Night Window CSV" },
  { value: "energy_warm_day_profile.csv", label: "Energy Warm Day Profile CSV" },
];
const CSV_DEVICE_MAP = {
  led_bulb: ["Lighting_LED"],
  bulb: ["Lighting_Tube", "Lighting_LED"],
  cfl_bulb: ["Lighting_Tube"],
  tube_light: ["Lighting_Tube"],
  ceiling_fan: ["Cooling_Fan_Ceiling"],
  table_fan: ["Cooling_Fan_Table"],
  exhaust_fan: ["Others_Exhaust"],
  smart_light: ["Lighting_LED"],
  night_lamp: ["Lighting_LED"],
  refrigerator: ["Others_Refrigerator"],
  microwave_oven: ["Kitchen_Microwave"],
  induction_cooktop: ["Kitchen_Induction"],
  electric_kettle: ["Kitchen_Kettle"],
  mixer_grinder: ["Kitchen_Mixer"],
  toaster: ["Kitchen_Toaster"],
  coffee_maker: ["Kitchen_Coffee"],
  washing_machine: ["Utility_Washing"],
  dishwasher: ["Utility_Dishwasher"],
  vacuum_cleaner: ["Utility_Vacuum"],
  iron: ["Utility_Iron"],
  water_heater: ["Heating_Water"],
  heater: ["Heating_Room"],
  room_heater: ["Heating_Room"],
  smart_speaker: ["Smart_Speaker"],
  cctv_camera: ["Smart_CCTV"],
  air_conditioner_1_5_ton: ["Cooling_AC"],
  laptop: ["Electronics_Laptop"],
  desktop_pc: ["Electronics_Desktop"],
  phone_charger: ["Electronics_Charger"],
  wifi_router: ["Electronics_WiFi"],
  water_purifier: ["Others_Purifier", "Smart_Purifier"],
};

function createEntry(appliance = "ceiling_fan", quantity = "1", hours = "") {
  return {
    appliance_name: appliance,
    quantity,
    hours_per_day: hours,
  };
}

function safeNumber(value) {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : 0;
}

function parseCsvText(csvText) {
  const lines = String(csvText || "").trim().split(/\r?\n/);
  if (lines.length <= 1) {
    return [];
  }
  const headers = lines[0].split(",").map((item) => item.replace(/^"|"$/g, ""));
  return lines.slice(1).map((line) => {
    const values = line.split(",");
    const row = {};
    headers.forEach((header, index) => {
      row[header] = (values[index] || "").replace(/^"|"$/g, "");
    });
    return row;
  });
}

function EnergyIngestForm() {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().slice(0, 10));
  const [ratePerKwh, setRatePerKwh] = useState("6.26");
  const [entries, setEntries] = useState([
    createEntry("ceiling_fan", "2", "5"),
    createEntry("led_bulb", "1", "5"),
    createEntry("bulb", "3", "1"),
    createEntry("heater", "1", "3"),
  ]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [message, setMessage] = useState("");
  const [datasetWindow, setDatasetWindow] = useState(7);
  const [datasetSource, setDatasetSource] = useState(DATASET_OPTIONS[0].value);
  const [predictionMode, setPredictionMode] = useState("blend");
  const [forecastWindow, setForecastWindow] = useState("24");
  const [historicalData, setHistoricalData] = useState([]);
  const [forecastData, setForecastData] = useState([]);
  const [csvDatasetRows, setCsvDatasetRows] = useState([]);

  useEffect(() => {
    async function loadPredictionContext() {
      const history = await getHistoricalData(datasetWindow);
      let forecast = [];
      if (forecastWindow !== "60_seconds_csv") {
        forecast = await getForecast(Number(forecastWindow));
      }
      setHistoricalData(history || []);
      setForecastData(forecast || []);
    }
    loadPredictionContext();
  }, [datasetWindow, forecastWindow]);

  useEffect(() => {
    async function loadCsvDataset() {
      try {
        const response = await fetch(`/datasets/${datasetSource}`);
        const text = await response.text();
        setCsvDatasetRows(parseCsvText(text));
      } catch (error) {
        console.error("CSV dataset load error:", error);
        setCsvDatasetRows([]);
      }
    }
    loadCsvDataset();
  }, [datasetSource]);

  const preview = useMemo(() => {
    const rate = safeNumber(ratePerKwh);
    const breakdown = entries.map((entry) => {
      const appliance = APPLIANCE_OPTIONS.find((option) => option.value === entry.appliance_name);
      const quantity = safeNumber(entry.quantity);
      const hours = safeNumber(entry.hours_per_day);
      const wattage = safeNumber(appliance?.wattage);
      const energy = (quantity * wattage * hours) / 1000;
      return {
        label: appliance?.label || entry.appliance_name,
        quantity,
        hours,
        wattage,
        energy,
        cost: energy * rate,
      };
    });
    const totalEnergy = breakdown.reduce((sum, item) => sum + item.energy, 0);
    return {
      breakdown,
      totalEnergy,
      totalCost: totalEnergy * rate,
    };
  }, [entries, ratePerKwh]);

  const predictionPreview = useMemo(() => {
    const rate = safeNumber(ratePerKwh);
    const historyAverageDaily = historicalData.length
      ? historicalData.reduce((sum, item) => sum + safeNumber(item.total_consumption), 0) / historicalData.length
      : 0;
    const forecastAverageHourly = forecastData.length
      ? forecastData.reduce((sum, item) => sum + safeNumber(item.energy_kwh), 0) / forecastData.length
      : 0;
    const forecastDailyEquivalent = forecastAverageHourly * 24;

    const csvRows = csvDatasetRows;
    const secondWiseRows = Array.from({ length: 60 }, (_, second) => {
      let secondTotal = 0;
      entries.forEach((entry) => {
        const matchedColumns = CSV_DEVICE_MAP[entry.appliance_name] || [];
        const averagePerMinute = matchedColumns.reduce((sum, column) => {
          if (!csvRows.length) {
            return sum;
          }
          const columnAverage = csvRows.reduce((acc, row) => acc + safeNumber(row[column]), 0) / csvRows.length;
          return sum + columnAverage;
        }, 0);
        const quantity = safeNumber(entry.quantity);
        const pulse = 1 + ((((second + quantity) % 10) - 5) * 0.015);
        const perSecondValue = Math.max(0, (averagePerMinute * quantity * pulse) / 60);
        secondTotal += perSecondValue;
      });
      return {
        second: second + 1,
        total_kwh: secondTotal,
      };
    });
    const csvSecondTotal = secondWiseRows.reduce((sum, row) => sum + row.total_kwh, 0);
    const csvAverageDaily = csvRows.length
      ? (csvRows.reduce((sum, row) => sum + safeNumber(row.Total_Consumption), 0) / csvRows.length) * 1440
      : 0;

    let predictedDailyKwh = preview.totalEnergy;
    let methodText = "This prediction uses only the appliance plan you entered.";

    if (predictionMode === "dataset") {
      predictedDailyKwh = csvAverageDaily || historyAverageDaily || preview.totalEnergy;
      methodText = `This prediction follows the selected CSV dataset "${DATASET_OPTIONS.find((item) => item.value === datasetSource)?.label || datasetSource}" as the main daily usage reference.`;
    } else if (predictionMode === "blend") {
      predictedDailyKwh = (preview.totalEnergy * 0.45) + (historyAverageDaily * 0.2) + (forecastDailyEquivalent * 0.15) + (csvAverageDaily * 0.2);
      methodText = `This prediction blends your manual plan, recent project history, the selected forecast window, and the CSV dataset "${DATASET_OPTIONS.find((item) => item.value === datasetSource)?.label || datasetSource}".`;
    } else if (predictionMode === "forecast") {
      predictedDailyKwh = forecastWindow === "60_seconds_csv" ? (csvSecondTotal * 1440) : (forecastDailyEquivalent || preview.totalEnergy);
      methodText = forecastWindow === "60_seconds_csv"
        ? `This prediction uses second-wise device information from "${DATASET_OPTIONS.find((item) => item.value === datasetSource)?.label || datasetSource}" and scales that pulse into a daily estimate.`
        : `This prediction follows the current ${forecastWindow}-hour forecast pattern and scales it into a one-day equivalent.`;
    }

    const predictedWeeklyKwh = predictedDailyKwh * 7;
    const predictedMonthlyKwh = predictedDailyKwh * 30;
    const deviation = predictedDailyKwh - preview.totalEnergy;

    return {
      historyAverageDaily,
      csvAverageDaily,
      forecastDailyEquivalent,
      predictedDailyKwh,
      predictedWeeklyKwh,
      predictedMonthlyKwh,
      dailyCost: predictedDailyKwh * rate,
      weeklyCost: predictedWeeklyKwh * rate,
      monthlyCost: predictedMonthlyKwh * rate,
      deviation,
      methodText,
      secondWiseRows,
      csvSecondTotal,
    };
  }, [csvDatasetRows, datasetSource, entries, forecastData, forecastWindow, historicalData, predictionMode, preview.totalEnergy, ratePerKwh]);

  const handleEntryChange = (index, field, value) => {
    setEntries((prev) =>
      prev.map((entry, entryIndex) =>
        entryIndex === index ? { ...entry, [field]: sanitizeText(value) } : entry
      )
    );
  };

  const addEntry = () => {
    setEntries((prev) => [...prev, createEntry()]);
  };

  const removeEntry = (index) => {
    setEntries((prev) => prev.filter((_, entryIndex) => entryIndex !== index));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setMessage("");
    setResult(null);

    const appliances = entries.map((entry) => ({
      appliance_name: entry.appliance_name,
      quantity: safeNumber(entry.quantity),
      hours_per_day: safeNumber(entry.hours_per_day),
    }));

    try {
      const response = await createHouseholdPlan({
        appliances,
        date: selectedDate || undefined,
        rate_per_kwh: safeNumber(ratePerKwh || 6.26),
      });

      if (response?.status === "success" || response?.status === "partial_success") {
        setResult(response);
        setMessage("Household usage calculated and saved successfully.");
      } else {
        setMessage(response?.message || "Unable to calculate household usage.");
      }
    } catch (error) {
      console.error("Household plan error:", error);
      setMessage("Failed to calculate the household usage plan.");
    } finally {
      setLoading(false);
    }
  };

  const success = message.toLowerCase().includes("success");

  return (
    <section style={{ marginBottom: "38px", animation: "fadeIn 1s ease-in-out" }}>
      <h2 style={{ color: "#0f4c81", marginBottom: "20px" }}>Manual Home Usage Input</h2>
      <div className="card" style={{ maxWidth: "980px", margin: "0 auto" }}>
        <h3 style={{ color: "#0f4c81", marginBottom: "12px" }}>Add Daily Appliance Usage</h3>
        <p style={{ marginTop: 0, color: "#5d6778", lineHeight: 1.55 }}>
          Select from a large household device list, enter quantity and hours used per day, choose a date if needed,
          and the system will calculate total energy and total amount in rupees. You can also choose how the project dataset should influence a forward-looking estimate.
        </p>
        <div style={{ marginBottom: "18px", padding: "14px", borderRadius: "14px", background: "#f6fbff", color: "#456077", border: "1px solid #d8e8f7" }}>
          <strong>BESCOM 2025 residential tariff:</strong> Fixed charge Rs. 120 per kW and energy charge Rs. 5.90 per unit with a Rs. 0.36 surcharge from April 2025.
          The default rate here uses <strong>Rs. 6.26 per unit</strong> for energy calculation. Fixed charge is shown as a note and is not added to each single-day usage preview.
        </div>

        {message && (
          <div
            style={{
              padding: "10px",
              marginBottom: "20px",
              borderRadius: "5px",
              backgroundColor: success ? "#d4edda" : "#f8d7da",
              color: success ? "#155724" : "#721c24",
              border: `1px solid ${success ? "#c3e6cb" : "#f5c6cb"}`,
            }}
          >
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "18px" }}>
            <div className="form-group">
              <label className="form-label">Date:</label>
              <input
                type="date"
                value={selectedDate}
                onChange={(event) => setSelectedDate(event.target.value)}
                className="form-input"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Rate Per kWh (INR):</label>
              <input
                type="number"
                step="0.1"
                min="0"
                value={ratePerKwh}
                onChange={(event) => setRatePerKwh(event.target.value)}
                className="form-input"
              />
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px", marginBottom: "18px" }}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Dataset Window</label>
              <select value={datasetWindow} onChange={(event) => setDatasetWindow(Number(event.target.value))} className="form-input">
                <option value={1}>Last 24 Hours</option>
                <option value={7}>Last 7 Days</option>
                <option value={14}>Last 14 Days</option>
                <option value={30}>Last 30 Days</option>
                <option value={60}>Last 60 Days</option>
                <option value={90}>Last 90 Days</option>
              </select>
            </div>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">CSV Dataset Source</label>
              <select value={datasetSource} onChange={(event) => setDatasetSource(event.target.value)} className="form-input">
                {DATASET_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Prediction Mode</label>
              <select value={predictionMode} onChange={(event) => setPredictionMode(event.target.value)} className="form-input">
                <option value="blend">Manual + Dataset Blend</option>
                <option value="dataset">Dataset-Led Prediction</option>
                <option value="forecast">Forecast-Led Prediction</option>
                <option value="manual">Manual Plan Only</option>
              </select>
            </div>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label className="form-label">Forecast Horizon</label>
              <select value={forecastWindow} onChange={(event) => setForecastWindow(event.target.value)} className="form-input">
                <option value="60_seconds_csv">60 Seconds CSV Device Pulse</option>
                <option value={6}>6 Hours</option>
                <option value={12}>12 Hours</option>
                <option value={24}>24 Hours</option>
                <option value={48}>48 Hours</option>
                <option value={72}>72 Hours</option>
                <option value={168}>168 Hours</option>
              </select>
            </div>
          </div>

          <div style={{ display: "grid", gap: "14px" }}>
            {entries.map((entry, index) => {
              const applianceMeta = APPLIANCE_OPTIONS.find((option) => option.value === entry.appliance_name);
              return (
                <div
                  key={`${entry.appliance_name}-${index}`}
                  style={{
                    display: "grid",
                    gridTemplateColumns: "2.2fr 0.8fr 0.8fr auto",
                    gap: "12px",
                    alignItems: "end",
                    padding: "14px",
                    borderRadius: "14px",
                    background: "#f8fbff",
                    border: "1px solid #dbe7f3",
                  }}
                >
                  <div className="form-group" style={{ marginBottom: 0 }}>
                    <label className="form-label">Appliance</label>
                    <select
                      value={entry.appliance_name}
                      onChange={(event) => handleEntryChange(index, "appliance_name", event.target.value)}
                      className="form-input"
                    >
                      {APPLIANCE_GROUPS.map((group) => (
                        <optgroup key={group.label} label={group.label}>
                          {group.options.map((option) => (
                            <option key={option.value} value={option.value}>
                              {option.label} ({option.wattage} W)
                            </option>
                          ))}
                        </optgroup>
                      ))}
                    </select>
                  </div>
                  <div className="form-group" style={{ marginBottom: 0 }}>
                    <label className="form-label">Quantity</label>
                    <input
                      type="number"
                      min="1"
                      value={entry.quantity}
                      onChange={(event) => handleEntryChange(index, "quantity", event.target.value)}
                      className="form-input"
                    />
                  </div>
                  <div className="form-group" style={{ marginBottom: 0 }}>
                    <label className="form-label">Hours/Day</label>
                    <input
                      type="number"
                      step="0.5"
                      min="0"
                      value={entry.hours_per_day}
                      onChange={(event) => handleEntryChange(index, "hours_per_day", event.target.value)}
                      className="form-input"
                    />
                  </div>
                  <button
                    type="button"
                    onClick={() => removeEntry(index)}
                    className="btn"
                    style={{
                      background: index === 0 ? "#d5e3f1" : "#fce2e2",
                      color: index === 0 ? "#5d6778" : "#9f1239",
                      cursor: entries.length === 1 ? "not-allowed" : "pointer",
                    }}
                    disabled={entries.length === 1}
                  >
                    Remove
                  </button>
                  <div style={{ gridColumn: "1 / -1", color: "#5d6778", fontSize: "0.92rem" }}>
                    Typical wattage for {applianceMeta?.label}: <strong>{applianceMeta?.wattage} W</strong>
                  </div>
                </div>
              );
            })}
          </div>

          <div style={{ display: "flex", gap: "12px", marginTop: "16px", flexWrap: "wrap" }}>
            <button type="button" onClick={addEntry} className="btn btn-success">
              Add Appliance
            </button>
            <button type="submit" disabled={loading} className="btn btn-primary">
              {loading ? "Calculating..." : "Calculate Total Amount"}
            </button>
          </div>
        </form>

        <div style={{ marginTop: "24px", padding: "18px", background: "#f4f9ff", borderRadius: "16px" }}>
          <h4 style={{ marginTop: 0, color: "#0f4c81" }}>Live Preview</h4>
          <p style={{ marginTop: 0, color: "#5d6778" }}>
            If you do not choose a date, the current date is used automatically.
          </p>
          <div style={{ display: "grid", gap: "10px" }}>
            {preview.breakdown.map((item, index) => (
              <div key={`${item.label}-${index}`} style={{ display: "flex", justifyContent: "space-between", gap: "12px", flexWrap: "wrap" }}>
                <span>{item.quantity} {item.label}{item.quantity > 1 ? "s" : ""} x {item.hours} hrs</span>
                <span>{item.energy.toFixed(3)} kWh | {formatINR(item.cost)}</span>
              </div>
            ))}
          </div>
          <hr style={{ margin: "14px 0", border: 0, borderTop: "1px solid #d7e6f4" }} />
          <div style={{ display: "flex", justifyContent: "space-between", gap: "12px", fontWeight: 700 }}>
            <span>Total Energy</span>
            <span>{preview.totalEnergy.toFixed(3)} kWh</span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", gap: "12px", fontWeight: 700, color: "#0f4c81", marginTop: "6px" }}>
            <span>Total Amount</span>
            <span>{formatINR(preview.totalCost)}</span>
          </div>
        </div>

        <div style={{ marginTop: "24px", padding: "18px", background: "linear-gradient(180deg, #ffffff 0%, #eef6ff 100%)", borderRadius: "16px", border: "1px solid #d9e8f7" }}>
          <h4 style={{ marginTop: 0, color: "#0f4c81" }}>Dataset-Aware Prediction</h4>
          <p style={{ marginTop: 0, color: "#5d6778", lineHeight: 1.6 }}>
            {predictionPreview.methodText}
          </p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))", gap: "14px", marginBottom: "14px" }}>
            <div style={{ padding: "14px", borderRadius: "14px", background: "white" }}>
              <div style={{ color: "#5d6778", marginBottom: "6px" }}>Dataset Avg/Day</div>
              <strong>{predictionPreview.historyAverageDaily.toFixed(2)} kWh</strong>
            </div>
            <div style={{ padding: "14px", borderRadius: "14px", background: "white" }}>
              <div style={{ color: "#5d6778", marginBottom: "6px" }}>CSV Avg/Day</div>
              <strong>{predictionPreview.csvAverageDaily.toFixed(2)} kWh</strong>
            </div>
            <div style={{ padding: "14px", borderRadius: "14px", background: "white" }}>
              <div style={{ color: "#5d6778", marginBottom: "6px" }}>Forecast Daily Eq.</div>
              <strong>{predictionPreview.forecastDailyEquivalent.toFixed(2)} kWh</strong>
            </div>
            <div style={{ padding: "14px", borderRadius: "14px", background: "white" }}>
              <div style={{ color: "#5d6778", marginBottom: "6px" }}>Predicted Daily</div>
              <strong>{predictionPreview.predictedDailyKwh.toFixed(2)} kWh</strong>
            </div>
            <div style={{ padding: "14px", borderRadius: "14px", background: "white" }}>
              <div style={{ color: "#5d6778", marginBottom: "6px" }}>Daily Amount</div>
              <strong>{formatINR(predictionPreview.dailyCost)}</strong>
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "14px" }}>
            <div style={{ padding: "14px", borderRadius: "14px", background: "#f9fcff" }}>
              <div style={{ color: "#5d6778", marginBottom: "6px" }}>Weekly Projection</div>
              <strong>{predictionPreview.predictedWeeklyKwh.toFixed(2)} kWh</strong>
              <div style={{ marginTop: "6px", color: "#0f4c81" }}>{formatINR(predictionPreview.weeklyCost)}</div>
            </div>
            <div style={{ padding: "14px", borderRadius: "14px", background: "#f9fcff" }}>
              <div style={{ color: "#5d6778", marginBottom: "6px" }}>Monthly Projection</div>
              <strong>{predictionPreview.predictedMonthlyKwh.toFixed(2)} kWh</strong>
              <div style={{ marginTop: "6px", color: "#0f4c81" }}>{formatINR(predictionPreview.monthlyCost)}</div>
            </div>
            <div style={{ padding: "14px", borderRadius: "14px", background: "#f9fcff" }}>
              <div style={{ color: "#5d6778", marginBottom: "6px" }}>Deviation From Manual Plan</div>
              <strong style={{ color: predictionPreview.deviation >= 0 ? "#b45309" : "#166534" }}>
                {predictionPreview.deviation >= 0 ? "+" : ""}{predictionPreview.deviation.toFixed(2)} kWh/day
              </strong>
              <div style={{ marginTop: "6px", color: "#5d6778" }}>
                Based on selected dataset and forecast context.
              </div>
            </div>
          </div>
          {forecastWindow === "60_seconds_csv" ? (
            <div style={{ marginTop: "18px", padding: "16px", borderRadius: "16px", background: "#ffffff", border: "1px solid #dbe8f6" }}>
              <h5 style={{ marginTop: 0, color: "#0f4c81" }}>Second-Wise Device Pulse From energy_consumption.csv</h5>
              <p style={{ marginTop: 0, color: "#5d6778", lineHeight: 1.6 }}>
                This view uses the selected CSV dataset and converts matching device columns into a 60-second appliance pulse for your selected entries.
              </p>
              <Chart
                labels={predictionPreview.secondWiseRows.map((row) => `${row.second}s`)}
                values={predictionPreview.secondWiseRows.map((row) => Number(row.total_kwh.toFixed(4)))}
                datasetLabel="Second-wise total energy pulse"
                borderColor="#9f1239"
                backgroundColor="rgba(159, 18, 57, 0.16)"
                chartType="line"
                yAxisLabel="Energy (kWh per second slice)"
              />
              <div style={{ marginTop: "12px", color: "#5d6778" }}>
                60-second accumulated energy from selected CSV: <strong>{predictionPreview.csvSecondTotal.toFixed(4)} kWh</strong>
              </div>
            </div>
          ) : null}
        </div>

        {result && (
          <div style={{ marginTop: "24px", padding: "18px", background: "linear-gradient(180deg, #ffffff 0%, #eef8ef 100%)", borderRadius: "16px", border: "1px solid #d3ebd4" }}>
            <h4 style={{ marginTop: 0, color: "#166534" }}>Calculated Output</h4>
            <p><strong>Date used:</strong> {result.date_used}</p>
            <p><strong>Total energy:</strong> {result.total_energy_kwh} kWh</p>
            <p><strong>Total amount:</strong> {formatINR(result.total_cost_inr)}</p>
            <p><strong>Saved readings:</strong> {result.saved_readings}</p>
            <div style={{ display: "grid", gap: "8px" }}>
              {result.breakdown.map((item, index) => (
                <div key={`${item.appliance_name}-${index}`} style={{ display: "flex", justifyContent: "space-between", gap: "12px", flexWrap: "wrap" }}>
                  <span>{item.appliance_name}: {item.quantity} units for {item.hours_per_day} hours</span>
                  <span>{item.energy_kwh} kWh | {formatINR(item.cost_inr)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}

export default EnergyIngestForm;
