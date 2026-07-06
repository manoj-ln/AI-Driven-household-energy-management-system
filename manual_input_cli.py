#!/usr/bin/env python3
"""
Interactive command-line tool for manual data input.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT / "backend"))

from app.database.manual_input import add_reading_interactive, manual_input


def _print_header() -> None:
    print("=" * 64)
    print("Household Energy Management - Manual Data Input")
    print("=" * 64)
    print("Software-only mode: use this tool to verify and save readings.")
    print()


def _confirm(prompt: str) -> bool:
    return input(f"{prompt} (y/n): ").strip().lower().startswith("y")


def _print_reading_preview(reading: dict) -> None:
    print("\nPreview of reading to be saved:")
    print(json.dumps(reading, indent=2, default=str))


def main() -> None:
    _print_header()

    while True:
        print("\nOptions:")
        print("1. Add single reading interactively")
        print("2. Add bulk readings from file")
        print("3. Generate realistic reading for device")
        print("4. Simulate continuous data")
        print("5. Export data")
        print("6. Show input template")
        print("7. Exit")
        print()

        choice = input("Enter your choice (1-7): ").strip()

        if choice == "1":
            add_reading_interactive()

        elif choice == "2":
            print("\nBulk Reading Input")
            print("-" * 20)
            file_path = input("Enter path to JSON file with readings array: ").strip()
            if not os.path.exists(file_path):
                print("File not found")
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    readings = json.load(f)
                if not isinstance(readings, list):
                    print("File must contain an array of readings")
                    continue

                result = manual_input.add_bulk_readings(readings)
                print(f"Added {result['success_count']} readings successfully")
                if result["error_count"] > 0:
                    print(f"{result['error_count']} errors:")
                    for error in result["errors"][:5]:
                        print(f"  - {error}")
            except json.JSONDecodeError:
                print("Invalid JSON file")
            except Exception as exc:
                print(f"Error: {exc}")

        elif choice == "3":
            print("\nGenerate Realistic Reading")
            print("-" * 30)
            device_id = input("Enter device ID: ").strip()
            if not device_id:
                print("Device ID is required")
                continue

            reading = manual_input.generate_realistic_reading(device_id)
            _print_reading_preview(reading)

            if _confirm("Save this reading to the database?"):
                result = manual_input.add_manual_reading(**reading)
                if result["status"] == "success":
                    print("Reading added successfully.")
                else:
                    print(f"Error: {result['message']}")

        elif choice == "4":
            print("\nSimulate Continuous Data")
            print("-" * 25)
            devices_input = input("Enter device IDs (comma-separated): ").strip()
            if not devices_input:
                print("At least one device ID is required")
                continue

            device_ids = [device.strip() for device in devices_input.split(",") if device.strip()]
            hours_text = input("Enter hours to simulate (default 24): ").strip()
            hours = int(hours_text) if hours_text.isdigit() else 24

            print(f"Simulating {hours} hours of data for {len(device_ids)} devices...")
            result = manual_input.simulate_continuous_data(device_ids, hours)
            print(f"Added {result['readings_added']} readings across {result['devices_simulated']} devices")

        elif choice == "5":
            print("\nExport Data")
            print("-" * 12)
            device_id = input("Enter device ID (optional): ").strip() or None
            hours_text = input("Enter hours to export (default 24): ").strip()
            hours = int(hours_text) if hours_text.isdigit() else 24
            format_type = input("Enter format (json/csv, default json): ").strip().lower()
            format_type = format_type if format_type in {"json", "csv"} else "json"

            try:
                data = manual_input.export_data(device_id, hours, format_type)
                filename = f"export_{device_id or 'all'}_{hours}h.{format_type}"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(data)
                print(f"Data exported to {filename}")
            except Exception as exc:
                print(f"Export failed: {exc}")

        elif choice == "6":
            print("\nManual Input Template")
            print("-" * 22)
            template = manual_input.get_manual_input_template()
            print("Template structure:")
            print(json.dumps(template["template"], indent=2))
            print(f"\nRequired fields: {template['required_fields']}")
            print(f"Optional fields: {template['optional_fields']}")
            print("\nExamples:")
            for index, example in enumerate(template["examples"], 1):
                print(f"{index}. {example['description']}:")
                print(json.dumps(example["data"], indent=4))

        elif choice == "7":
            print("Goodbye.")
            break

        else:
            print("Invalid choice. Please enter 1-7.")

        print("\n" + "=" * 64)


if __name__ == "__main__":
    try:
        import json  # noqa: F401 - kept for the interactive preview helper

        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Goodbye.")
    except Exception as exc:
        print(f"\nError: {exc}")
        sys.exit(1)
