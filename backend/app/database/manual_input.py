"""
Manual Data Input Module for Household Energy Management System

This module provides functionality to manually input home energy data
for software-only demos and testing purposes.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import random
import re

from app.database.db import db


class ManualDataInput:
    """Class for manual data input and simulation"""

    DEVICE_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_\-]+$")
    VALUE_RANGES = {
        "voltage": (0.0, 1000.0),
        "current": (0.0, 100.0),
        "power": (0.0, 100000.0),
        "energy_consumption": (0.0, 1000.0),
        "temperature": (-50.0, 120.0),
        "humidity": (0.0, 100.0),
    }
    APPLIANCE_WATTAGE = {
        "led_bulb": 9.0,
        "bulb": 60.0,
        "cfl_bulb": 20.0,
        "tube_light": 30.0,
        "ceiling_fan": 75.0,
        "exhaust_fan": 50.0,
        "table_fan": 45.0,
        "smart_light": 15.0,
        "night_lamp": 7.0,
        "emergency_torch": 10.0,
        "extension_board": 1.0,
        "refrigerator": 180.0,
        "deep_freezer": 300.0,
        "microwave_oven": 1000.0,
        "electric_kettle": 1500.0,
        "induction_cooktop": 1800.0,
        "rice_cooker": 500.0,
        "mixer_grinder": 500.0,
        "blender": 300.0,
        "toaster": 1200.0,
        "coffee_maker": 900.0,
        "washing_machine": 700.0,
        "clothes_dryer": 1800.0,
        "vacuum_cleaner": 1000.0,
        "robotic_vacuum": 40.0,
        "steam_cleaner": 1200.0,
        "carpet_cleaner": 1500.0,
        "iron": 1200.0,
        "water_heater": 2000.0,
        "pressure_washer": 2000.0,
        "shoe_polisher": 75.0,
        "led_tv_32_43": 60.0,
        "oled_4k_tv_55_65": 120.0,
        "projector": 220.0,
        "home_theater_system": 180.0,
        "set_top_box": 20.0,
        "laptop": 65.0,
        "desktop_pc": 220.0,
        "gaming_pc": 600.0,
        "gaming_console": 150.0,
        "wifi_router": 12.0,
        "hair_dryer": 1200.0,
        "hair_straightener": 50.0,
        "electric_shaver": 20.0,
        "electric_toothbrush": 3.0,
        "massager": 35.0,
        "heater": 1500.0,
        "room_heater": 1800.0,
        "air_conditioner_1_5_ton": 1800.0,
        "humidifier": 40.0,
        "dehumidifier": 300.0,
        "nebulizer": 80.0,
        "cctv_camera": 10.0,
        "smart_doorbell": 8.0,
        "smart_lock": 4.0,
        "smoke_detector": 3.0,
        "baby_monitor": 8.0,
        "motion_sensor_light": 10.0,
        "smart_thermostat": 6.0,
        "smart_plug": 2.0,
        "smart_curtains": 15.0,
        "smart_sprinkler_system": 35.0,
        "printer": 75.0,
        "scanner": 40.0,
        "digital_camera": 8.0,
        "portable_speaker": 20.0,
        "ebook_reader": 3.0,
        "smartwatch_charger": 3.0,
        "power_bank_charging": 8.0,
        "bluetooth_headphones": 3.0,
        "external_hard_drive": 8.0,
        "digital_weighing_scale": 7.0,
        "dishwasher": 1500.0,
        "water_purifier": 30.0,
        "chimney": 180.0,
        "food_processor": 600.0,
        "juicer": 350.0,
        "sandwich_maker": 800.0,
        "air_fryer": 1500.0,
        "electric_oven": 2000.0,
        "slow_cooker": 250.0,
        "dish_dryer": 900.0,
        "sewing_machine": 100.0,
        "inverter": 50.0,
        "water_pump": 750.0,
        "garage_door_motor": 350.0,
        "doorbell": 5.0,
        "aquarium_pump": 25.0,
        "aquarium_heater": 100.0,
        "electric_blanket": 120.0,
        "treadmill": 800.0,
        "exercise_bike": 100.0,
        "elliptical_trainer": 300.0,
        "cpap_machine": 60.0,
        "oxygen_concentrator": 350.0,
        "study_lamp": 12.0,
        "monitor": 30.0,
        "tablet_charger": 12.0,
        "phone_charger": 8.0,
        "speaker_system": 100.0,
        "modem": 10.0,
        "electric_drill": 600.0,
        "glue_gun": 40.0,
        "bread_maker": 500.0,
        "camera_charger": 10.0,
        "router_backup_ups": 20.0,
        "ceiling_light_panel": 36.0,
        "decorative_light_strip": 18.0,
    }

    def __init__(self):
        self.sample_data_file = Path(__file__).resolve().parents[2] / "data" / "manual_data_samples.json"
        self._ensure_sample_data()

    def _ensure_sample_data(self):
        """Ensure sample data file exists"""
        self.sample_data_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.sample_data_file.exists():
            sample_data = {
                "devices": [
                    {
                        "device_id": "living_room_fan",
                        "device_type": "appliance",
                        "name": "Living Room Fan",
                        "location": "living_room"
                    },
                    {
                        "device_id": "kitchen_light",
                        "device_type": "appliance",
                        "name": "Kitchen Light",
                        "location": "kitchen"
                    },
                    {
                        "device_id": "bedroom_heater",
                        "device_type": "appliance",
                        "name": "Bedroom Heater",
                        "location": "bedroom"
                    }
                ],
                "readings": [
                    {
                        "device_id": "living_room_fan",
                        "voltage": 220.5,
                        "current": 1.2,
                        "power": 264.6,
                        "energy_consumption": 0.2646,
                        "temperature": 25.3,
                        "humidity": 65.2
                    },
                    {
                        "device_id": "kitchen_light",
                        "voltage": 221.0,
                        "current": 2.1,
                        "power": 464.1,
                        "energy_consumption": 0.4641,
                        "temperature": 24.8,
                        "humidity": 62.1
                    },
                    {
                        "device_id": "bedroom_heater",
                        "voltage": 219.8,
                        "current": 0.8,
                        "power": 175.8,
                        "energy_consumption": 0.1758,
                        "temperature": 26.1,
                        "humidity": 68.5
                    }
                ]
            }

            with open(self.sample_data_file, 'w') as f:
                json.dump(sample_data, f, indent=2)

    def load_sample_data(self) -> Dict[str, Any]:
        """Load sample data from file"""
        try:
            with open(self.sample_data_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self._ensure_sample_data()
            return self.load_sample_data()

    def add_manual_reading(self, device_id: str, voltage: float = None, current: float = None,
                          power: float = None, energy_consumption: float = None,
                          temperature: float = None, humidity: float = None,
                          timestamp: str = None) -> Dict[str, Any]:
        """
        Manually add a single energy reading

        Args:
            device_id: Device identifier
            voltage: Voltage in volts
            current: Current in amperes
            power: Power in watts
            energy_consumption: Energy consumption in kWh
            temperature: Temperature in Celsius
            humidity: Humidity percentage
            timestamp: ISO format timestamp (optional, defaults to now)

        Returns:
            Dictionary with the inserted reading data
        """
        validation_error = self._validate_manual_reading(
            device_id=device_id,
            voltage=voltage,
            current=current,
            power=power,
            energy_consumption=energy_consumption,
            temperature=temperature,
            humidity=humidity,
            timestamp=timestamp,
        )
        if validation_error:
            return {"status": "error", "message": validation_error}

        if timestamp is None:
            timestamp = datetime.utcnow().isoformat()
        elif isinstance(timestamp, datetime):
            timestamp = timestamp.isoformat()

        # Calculate missing values if possible
        if power is None and voltage is not None and current is not None:
            power = voltage * current
        if energy_consumption is None and power is not None:
            # Convert power (watts) to energy consumption (kWh) for 1 hour
            energy_consumption = power / 1000  # kWh for 1 hour

        reading = {
            'timestamp': timestamp,
            'device_id': device_id,
            'device_type': 'appliance',
            'voltage': voltage,
            'current': current,
            'power': power,
            'energy_consumption': energy_consumption,
            'temperature': temperature,
            'humidity': humidity
        }

        # Remove None values
        reading = {k: v for k, v in reading.items() if v is not None}

        try:
            db.insert_reading(reading)
            db.register_device(
                {
                    "device_id": device_id,
                    "device_type": "appliance",
                    "name": device_id.replace("_", " ").title(),
                    "location": None,
                    "is_active": True,
                    "last_seen": timestamp,
                    "ip_address": None,
                }
            )
            return {"status": "success", "message": "Reading added successfully", "data": reading}
        except Exception as e:
            return {"status": "error", "message": f"Failed to add reading: {str(e)}"}

    def _validate_manual_reading(
        self,
        device_id: str,
        voltage: float = None,
        current: float = None,
        power: float = None,
        energy_consumption: float = None,
        temperature: float = None,
        humidity: float = None,
        timestamp: str = None,
    ) -> Optional[str]:
        if not device_id or not str(device_id).strip():
            return "device_id is required"

        if not self.DEVICE_ID_PATTERN.match(device_id):
            return "device_id may only contain letters, numbers, underscores, and hyphens"

        values = {
            "voltage": voltage,
            "current": current,
            "power": power,
            "energy_consumption": energy_consumption,
            "temperature": temperature,
            "humidity": humidity,
        }
        for field, value in values.items():
            if value is None:
                continue
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                return f"{field} must be numeric"
            lower, upper = self.VALUE_RANGES[field]
            if numeric < lower or numeric > upper:
                return f"{field} must be between {lower} and {upper}"

        if timestamp is not None and isinstance(timestamp, str):
            try:
                datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                return "timestamp must be ISO formatted"

        return None

    def add_bulk_readings(self, readings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Add multiple readings at once

        Args:
            readings: List of reading dictionaries

        Returns:
            Dictionary with success/error counts
        """
        success_count = 0
        error_count = 0
        errors = []

        for reading in readings:
            result = self.add_manual_reading(**reading)
            if result["status"] == "success":
                success_count += 1
            else:
                error_count += 1
                errors.append(result["message"])

        return {
            "status": "completed",
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors
        }

    def generate_realistic_reading(self, device_id: str, base_reading: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a realistic energy reading with some random variation

        Args:
            device_id: Device identifier
            base_reading: Base reading to vary from (optional)

        Returns:
            Dictionary with generated reading data
        """
        if base_reading is None:
            # Use default values based on device location
            sample_data = self.load_sample_data()
            device_readings = [r for r in sample_data["readings"] if r["device_id"] == device_id]
            if device_readings:
                base_reading = device_readings[0]
            else:
                # Default values
                base_reading = {
                    "voltage": 220.0,
                    "current": 1.0,
                    "power": 220.0,
                    "energy_consumption": 0.22,
                    "temperature": 25.0,
                    "humidity": 60.0
                }

        # Add realistic variation (±10%)
        variation = 0.1

        reading = {
            'device_id': device_id,
            'voltage': base_reading.get('voltage', 220.0) * (1 + random.uniform(-variation, variation)),
            'current': base_reading.get('current', 1.0) * (1 + random.uniform(-variation, variation)),
            'temperature': base_reading.get('temperature', 25.0) * (1 + random.uniform(-variation/2, variation/2)),
            'humidity': base_reading.get('humidity', 60.0) * (1 + random.uniform(-variation/2, variation/2))
        }

        # Recalculate power and energy
        reading['power'] = reading['voltage'] * reading['current']
        reading['energy_consumption'] = reading['power'] / 1000  # kWh for 1 hour

        return reading

    def simulate_continuous_data(self, device_ids: List[str], hours: int = 24,
                               interval_minutes: int = 60) -> Dict[str, Any]:
        """
        Simulate continuous data for multiple devices over a time period

        Args:
            device_ids: List of device IDs to simulate
            hours: Number of hours to simulate
            interval_minutes: Minutes between readings

        Returns:
            Dictionary with simulation results
        """
        sample_data = self.load_sample_data()
        readings_added = []

        start_time = datetime.utcnow() - timedelta(hours=hours)

        for device_id in device_ids:
            # Get base reading for this device
            device_readings = [r for r in sample_data["readings"] if r["device_id"] == device_id]
            base_reading = device_readings[0] if device_readings else None

            current_time = start_time
            while current_time <= datetime.utcnow():
                # Generate realistic reading
                reading = self.generate_realistic_reading(device_id, base_reading)
                reading['timestamp'] = current_time.isoformat()

                # Add the reading
                result = self.add_manual_reading(**reading)
                if result["status"] == "success":
                    readings_added.append(result["data"])

                current_time += timedelta(minutes=interval_minutes)

        return {
            "status": "completed",
            "readings_added": len(readings_added),
            "devices_simulated": len(device_ids),
            "time_period_hours": hours
        }

    def get_manual_input_template(self) -> Dict[str, Any]:
        """
        Get a template for manual data input

        Returns:
            Dictionary with input template and examples
        """
        return {
            "template": {
                "device_id": "living_room_fan",
                "voltage": 220.5,
                "current": 1.2,
                "power": 264.6,
                "energy_consumption": 0.2646,
                "temperature": 25.3,
                "humidity": 65.2,
                "timestamp": "2024-01-01T12:00:00"  # Optional
            },
            "required_fields": ["device_id"],
            "optional_fields": ["voltage", "current", "power", "energy_consumption", "temperature", "humidity", "timestamp"],
            "examples": [
                {
                    "description": "Basic reading with voltage and current",
                    "data": {
                        "device_id": "living_room_fan",
                        "voltage": 220.0,
                        "current": 1.5
                    }
                },
                {
                    "description": "Complete reading with all fields",
                    "data": {
                        "device_id": "kitchen_light",
                        "voltage": 221.5,
                        "current": 2.1,
                        "power": 464.0,
                        "energy_consumption": 0.464,
                        "temperature": 24.8,
                        "humidity": 62.1
                    }
                }
            ]
        }

    def export_data(self, device_id: str = None, hours: int = 24, format: str = "json") -> str:
        """
        Export manual data for backup or analysis

        Args:
            device_id: Specific device ID (optional)
            hours: Hours of data to export
            format: Export format ("json" or "csv")

        Returns:
            Exported data as string
        """
        # Get data from database
        readings = db.get_recent_readings(limit=hours*60, device_id=device_id)  # Assuming hourly readings

        if format.lower() == "json":
            return json.dumps(readings, indent=2)
        elif format.lower() == "csv":
            if not readings:
                return "No data available"

            # CSV header
            headers = list(readings[0].keys())
            csv_data = [",".join(headers)]

            # CSV rows
            for reading in readings:
                row = [str(reading.get(header, "")) for header in headers]
                csv_data.append(",".join(row))

            return "\n".join(csv_data)
        else:
            raise ValueError("Unsupported format. Use 'json' or 'csv'")

    def process_household_plan(
        self,
        appliances: List[Dict[str, Any]],
        date: str = None,
        rate_per_kwh: float = 6.26,
    ) -> Dict[str, Any]:
        if not appliances:
            return {"status": "error", "message": "At least one appliance entry is required"}

        target_date = datetime.utcnow()
        if date:
            try:
                target_date = datetime.fromisoformat(date)
            except ValueError:
                try:
                    target_date = datetime.fromisoformat(f"{date}T12:00:00")
                except ValueError:
                    return {"status": "error", "message": "date must be ISO formatted or YYYY-MM-DD"}

        readings = []
        breakdown = []
        total_energy = 0.0

        for item in appliances:
            appliance_name = str(item.get("appliance_name", "")).strip().lower().replace(" ", "_")
            if not appliance_name:
                return {"status": "error", "message": "Each appliance must include appliance_name"}

            try:
                quantity = int(item.get("quantity", 1))
                hours_per_day = float(item.get("hours_per_day", 0))
            except (TypeError, ValueError):
                return {"status": "error", "message": "quantity must be integer and hours_per_day must be numeric"}

            if quantity <= 0 or hours_per_day < 0:
                return {"status": "error", "message": "quantity must be positive and hours_per_day cannot be negative"}

            wattage = item.get("wattage")
            if wattage is None:
                wattage = self.APPLIANCE_WATTAGE.get(appliance_name)
            if wattage is None:
                return {"status": "error", "message": f"wattage is required for appliance '{appliance_name}'"}

            try:
                wattage = float(wattage)
            except (TypeError, ValueError):
                return {"status": "error", "message": f"wattage for '{appliance_name}' must be numeric"}

            total_power = wattage * quantity
            energy_kwh = (total_power * hours_per_day) / 1000.0
            total_energy += energy_kwh

            device_id = f"{appliance_name}_{quantity}unit"
            timestamp = target_date.replace(hour=12, minute=0, second=0, microsecond=0).isoformat()
            readings.append(
                {
                    "device_id": device_id,
                    "power": round(total_power, 3),
                    "energy_consumption": round(energy_kwh, 3),
                    "timestamp": timestamp,
                }
            )
            breakdown.append(
                {
                    "appliance_name": appliance_name.replace("_", " ").title(),
                    "quantity": quantity,
                    "hours_per_day": hours_per_day,
                    "wattage": wattage,
                    "power_watts": round(total_power, 3),
                    "energy_kwh": round(energy_kwh, 3),
                    "cost_inr": round(energy_kwh * rate_per_kwh, 2),
                }
            )

        save_result = self.add_bulk_readings(readings)
        total_cost = round(total_energy * rate_per_kwh, 2)

        return {
            "status": "success" if save_result["error_count"] == 0 else "partial_success",
            "date_used": target_date.date().isoformat(),
            "rate_per_kwh": rate_per_kwh,
            "total_energy_kwh": round(total_energy, 3),
            "total_cost_inr": total_cost,
            "breakdown": breakdown,
            "saved_readings": save_result["success_count"],
            "save_errors": save_result["errors"],
        }


# Global instance
manual_input = ManualDataInput()


def add_reading_interactive():
    """
    Interactive function to add a reading via command line
    """
    print("=== Manual Energy Reading Input ===")
    print()

    # Get device ID
    device_id = input("Enter device ID (e.g., living_room_fan): ").strip()
    if not device_id:
        print("Device ID is required!")
        return

    # Get optional values
    voltage = input("Enter voltage (V) or press Enter to skip: ").strip()
    voltage = float(voltage) if voltage else None

    current = input("Enter current (A) or press Enter to skip: ").strip()
    current = float(current) if current else None

    power = input("Enter power (W) or press Enter to skip: ").strip()
    power = float(power) if power else None

    energy = input("Enter energy consumption (kWh) or press Enter to skip: ").strip()
    energy = float(energy) if energy else None

    temp = input("Enter temperature (°C) or press Enter to skip: ").strip()
    temp = float(temp) if temp else None

    humidity = input("Enter humidity (%) or press Enter to skip: ").strip()
    humidity = float(humidity) if humidity else None

    # Add the reading
    result = manual_input.add_manual_reading(
        device_id=device_id,
        voltage=voltage,
        current=current,
        power=power,
        energy_consumption=energy,
        temperature=temp,
        humidity=humidity
    )

    print()
    if result["status"] == "success":
        print("✅ Reading added successfully!")
        print(f"Data: {result['data']}")
    else:
        print(f"❌ Error: {result['message']}")


if __name__ == "__main__":
    # Example usage
    print("Manual Data Input Module")
    print("Run: python -c \"from app.database.manual_input import add_reading_interactive; add_reading_interactive()\"")
    print("Or import and use the manual_input instance directly")
