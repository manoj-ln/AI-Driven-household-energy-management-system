# Manual Data Input Module

This module provides software-only manual input, validation, simulation, and export for the energy management system.

## Features

- Manual reading input with validation
- Bulk data import from JSON files
- Realistic reading generation
- Continuous simulation for multiple devices
- Export to JSON or CSV
- REST API endpoints
- Interactive command-line interface

## Validation

The manual input pipeline now checks:

- `device_id` format
- numeric value ranges for voltage, current, power, energy, temperature, and humidity
- ISO timestamp formatting

Invalid entries are rejected before they reach the database.

## API Endpoints

### Add Single Reading

```http
POST /manual/manual-reading
Content-Type: application/json

{
  "device_id": "device_001",
  "voltage": 220.5,
  "current": 1.2,
  "temperature": 25.3
}
```

### Add Bulk Readings

```http
POST /manual/manual-readings/bulk
Content-Type: application/json

[
  {
    "device_id": "device_001",
    "voltage": 220.0,
    "current": 1.5
  },
  {
    "device_id": "device_002",
    "voltage": 221.0,
    "current": 2.1,
    "temperature": 24.8
  }
]
```

### Generate Realistic Reading

```http
POST /manual/simulate/device_001?base_voltage=220.0&base_current=1.0
```

### Simulate Continuous Data

```http
POST /manual/simulate-continuous
Content-Type: application/json

{
  "device_ids": ["device_001", "device_002"],
  "hours": 24,
  "interval_minutes": 60
}
```

### Get Input Template

```http
GET /manual/manual-input-template
```

### Export Data

```http
GET /manual/export-data?device_id=device_001&hours=24&format=json
```

## CLI

Run the interactive CLI:

```bash
python manual_input_cli.py
```

The CLI now previews generated readings before saving them.

## Data Flow

- Input is validated in the service layer
- Valid data is saved to SQLite
- Analytics and prediction services can read the stored history
- The frontend and chatbot can use the same data source for software-only demos
