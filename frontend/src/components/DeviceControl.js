import React, { useEffect, useState } from "react";
import {
  createControlDevice,
  deleteControlDevice,
  getControlDevices,
  toggleDevice,
  updateControlDevice,
} from "../services/apiService";

function DeviceControl() {
  const quickDevices = [
    { name: "Bedroom Fan", device_type: "fan", location: "Bedroom" },
    { name: "Kitchen Light", device_type: "light", location: "Kitchen" },
    { name: "Hall Heater", device_type: "heater", location: "Hall" },
    { name: "Living Room TV", device_type: "entertainment", location: "Living Room" },
    { name: "Study Lamp", device_type: "light", location: "Study Room" },
    { name: "Refrigerator", device_type: "cooling", location: "Kitchen" },
  ];
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [editingDeviceId, setEditingDeviceId] = useState("");
  const [form, setForm] = useState({
    name: "",
    device_type: "fan",
    location: "Living Room",
    quantity: 1,
  });
  const [message, setMessage] = useState("");

  useEffect(() => {
    async function loadDevices() {
      const data = await getControlDevices();
      setDevices(data || []);
      setLoading(false);
    }
    loadDevices();
  }, []);

  const refreshDevices = async () => {
    const data = await getControlDevices();
    setDevices(data || []);
  };

  const resetForm = () => {
    setForm({
      name: "",
      device_type: "fan",
      location: "Living Room",
      quantity: 1,
    });
    setEditingDeviceId("");
  };

  const handleToggle = async (deviceName) => {
    const result = await toggleDevice(deviceName);
    if (!result) {
      return;
    }
    setDevices((prev) =>
      prev.map((device) =>
        device.name === result.name ? { ...device, is_on: result.is_on } : device
      )
    );
  };

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({
      ...prev,
      [name]: name === "quantity" ? Number(value) : value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSaving(true);
    setMessage("");

    const payload = {
      name: form.name.trim(),
      device_type: form.device_type,
      location: form.location.trim() || "Home",
      quantity: Number(form.quantity || 1),
    };

    const result = editingDeviceId
      ? await updateControlDevice(editingDeviceId, payload)
      : await createControlDevice(payload);

    if (result && !result.error) {
      setMessage(editingDeviceId ? `${result.name} updated successfully.` : `${result.name} added to Device Control.`);
      resetForm();
      await refreshDevices();
    } else {
      setMessage(result?.error || "Unable to save the device right now. Please restart the backend and try again.");
    }

    setSaving(false);
  };

  const handleQuickAdd = async (preset) => {
    setSaving(true);
    setMessage("");
    const result = await createControlDevice({ ...preset, quantity: 1 });
    if (result && !result.error) {
      setMessage(`${result.name} added to Device Control.`);
      await refreshDevices();
    } else {
      setMessage(result?.error || "Unable to add the device right now. Please restart the backend and try again.");
    }
    setSaving(false);
  };

  const handleEdit = (device) => {
    setEditingDeviceId(device.device_id);
    setForm({
      name: device.name,
      device_type: device.device_type || "fan",
      location: device.location || "Home",
      quantity: 1,
    });
    setMessage("");
  };

  const handleDelete = async (deviceId) => {
    setSaving(true);
    const result = await deleteControlDevice(deviceId);
    if (result && !result.error) {
      setDevices((prev) => prev.filter((device) => device.device_id !== deviceId));
      setMessage("Device deleted successfully.");
      if (editingDeviceId === deviceId) {
        resetForm();
      }
    } else {
      setMessage(result?.error || "Unable to delete the device right now.");
    }
    setSaving(false);
  };

  return (
    <section style={{ marginBottom: "38px", animation: "fadeIn 1s ease-in-out" }}>
      <h2 style={{ color: "#0f4c81", marginBottom: "20px" }}>Device Control</h2>
      <div
        className="card"
        style={{
          marginBottom: "20px",
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
          gap: "20px",
        }}
      >
        <div>
          <h3 style={{ color: "#0f4c81", marginTop: 0 }}>{editingDeviceId ? "Edit Device" : "Add Device"}</h3>
          <p style={{ marginTop: 0, color: "#4f6173" }}>
            Create, edit, and remove software-only home appliance profiles here.
          </p>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label" htmlFor="device-name">Device Name</label>
              <input
                id="device-name"
                name="name"
                className="form-input"
                placeholder="Example: Bedroom Fan"
                value={form.name}
                onChange={handleChange}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="device-type">Device Type</label>
              <select
                id="device-type"
                name="device_type"
                className="form-input"
                value={form.device_type}
                onChange={handleChange}
              >
                <option value="fan">Fan</option>
                <option value="light">Light</option>
                <option value="heater">Heater</option>
                <option value="kitchen">Kitchen Appliance</option>
                <option value="cooling">Cooling Appliance</option>
                <option value="entertainment">Entertainment Device</option>
                <option value="security">Security Device</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="device-location">Location</label>
              <input
                id="device-location"
                name="location"
                className="form-input"
                placeholder="Example: Living Room"
                value={form.location}
                onChange={handleChange}
              />
            </div>
            {!editingDeviceId ? (
              <div className="form-group">
                <label className="form-label" htmlFor="device-quantity">Quantity</label>
                <input
                  id="device-quantity"
                  name="quantity"
                  type="number"
                  min="1"
                  max="25"
                  className="form-input"
                  value={form.quantity}
                  onChange={handleChange}
                />
              </div>
            ) : null}
            <div style={{ display: "flex", gap: "10px", flexWrap: "wrap" }}>
              <button type="submit" className="btn btn-primary" disabled={saving}>
                {saving ? "Saving..." : editingDeviceId ? "Update Device" : "Add Device"}
              </button>
              {editingDeviceId ? (
                <button type="button" className="btn" style={{ background: "#e8eef5", color: "#0f4c81" }} onClick={resetForm}>
                  Cancel Edit
                </button>
              ) : null}
            </div>
          </form>
          {message ? (
            <p style={{ marginTop: "12px", color: message.toLowerCase().includes("unable") ? "#b42318" : "#12723b" }}>
              {message}
            </p>
          ) : null}
        </div>
        <div>
          <h3 style={{ color: "#0f4c81", marginTop: 0 }}>Quick Add</h3>
          <p style={{ marginTop: 0, color: "#4f6173" }}>
            Use presets to populate your home quickly and then edit the names or rooms if needed.
          </p>
          <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginTop: "10px" }}>
            {quickDevices.map((preset) => (
              <button
                key={preset.name}
                type="button"
                className="btn"
                style={{ background: "#e8f1fb", color: "#0f4c81", padding: "8px 12px" }}
                onClick={() => handleQuickAdd(preset)}
                disabled={saving}
              >
                {preset.name}
              </button>
            ))}
          </div>
        </div>
      </div>
      <div className="card" style={{ marginBottom: "20px" }}>
        <strong>Software-only status:</strong> {(devices || []).length} registered device profiles loaded.
        {" "}
        {(devices || []).length > 0 && (devices || []).every((device) => device.is_on)
          ? "All devices are running."
          : "Some devices are switched off."}
      </div>
      {loading ? (
        <div style={{ textAlign: "center", padding: "40px" }}>
          <span className="loading" style={{ marginRight: "10px" }}></span>
          Loading device controls...
        </div>
      ) : devices.length === 0 ? (
        <div className="card" style={{ textAlign: "center", padding: "32px" }}>
          <h3 style={{ color: "#0f4c81", marginTop: 0 }}>No devices added yet</h3>
          <p style={{ color: "#4f6173", marginBottom: 0 }}>
            Add your first software-only appliance above and it will appear here for control.
          </p>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "20px" }}>
          {devices.map((device, index) => (
            <div
              key={device.device_id || device.name}
              className="card"
              style={{
                animation: `fadeIn ${1 + index * 0.1}s ease-in-out`,
                position: "relative",
                overflow: "hidden"
              }}
            >
              <div style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: "100%",
                height: "4px",
                background: device.is_on ? "#28a745" : "#dc3545",
                transition: "background 0.3s ease"
              }}></div>
              <h3 style={{ color: "#0f4c81", marginBottom: "10px" }}>{String(device.name).replace(/_/g, " ")}</h3>
              <div style={{ marginBottom: "15px" }}>
                <p style={{ margin: "5px 0" }}>
                  <strong>Type:</strong> {device.device_type || "appliance"}
                </p>
                <p style={{ margin: "5px 0" }}>
                  <strong>Location:</strong> {device.location || "Home"}
                </p>
                <p style={{ margin: "5px 0" }}>
                  <strong>Average Usage:</strong> {device.average_usage} kWh
                </p>
                <p style={{ margin: "5px 0" }}>
                  <strong>Share:</strong> {device.share}%
                </p>
                <p style={{ margin: "5px 0" }}>
                  <strong>Status:</strong>
                  <span style={{
                    color: device.is_on ? "#28a745" : "#dc3545",
                    fontWeight: "bold",
                    marginLeft: "5px"
                  }}>
                    {device.is_on ? "ON" : "OFF"}
                  </span>
                </p>
              </div>
              <div style={{ display: "grid", gap: "8px" }}>
                <button
                  onClick={() => handleToggle(device.name)}
                  className={`btn ${device.is_on ? "btn-danger" : "btn-success"}`}
                  style={{ width: "100%" }}
                >
                  {device.is_on ? "Turn Off" : "Turn On"}
                </button>
                <div style={{ display: "flex", gap: "8px" }}>
                  <button
                    type="button"
                    className="btn"
                    style={{ background: "#e8f1fb", color: "#0f4c81", flex: 1 }}
                    onClick={() => handleEdit(device)}
                  >
                    Edit
                  </button>
                  <button
                    type="button"
                    className="btn"
                    style={{ background: "#fce2e2", color: "#9f1239", flex: 1 }}
                    onClick={() => handleDelete(device.device_id)}
                    disabled={saving}
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}

export default DeviceControl;
