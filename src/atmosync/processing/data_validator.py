
"""Validate raw AtmoSync sensor readings and separate valid and rejected data."""

import argparse
import csv
import math
from datetime import datetime
from pathlib import Path


FIELDNAMES = [
    "timestamp",
    "sensor_id",
    "location_id",
    "temperature_c",
    "humidity_pct",
    "soil_moisture_pct",
]

SENSOR_LOCATIONS = {
    "SENSOR_001": "LOCATION_A",
    "SENSOR_002": "LOCATION_B",
    "SENSOR_003": "LOCATION_C",
}


def validate_readings(readings):
    """Return valid readings and rejected readings with error reasons."""

    valid = []
    rejected = []
    seen_records = set()

    for row in readings:
        errors = []

        # Check for missing fields
        for field in FIELDNAMES:
            if not row.get(field, "").strip():
                errors.append(f"Missing value: {field}")

        # Validate timestamp
        timestamp = row.get("timestamp", "").strip()
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            if timestamp:
                errors.append("Invalid timestamp")

        # Validate sensor and location
        sensor_id = row.get("sensor_id", "").strip()
        location_id = row.get("location_id", "").strip()

        if sensor_id and sensor_id not in SENSOR_LOCATIONS:
            errors.append("Unknown sensor ID")
        elif sensor_id in SENSOR_LOCATIONS and location_id:
            if SENSOR_LOCATIONS[sensor_id] != location_id:
                errors.append("Sensor-location mismatch")

        # Validate numeric readings
        numeric_fields = {
            "temperature_c": (-20, 60),
            "humidity_pct": (0, 100),
            "soil_moisture_pct": (0, 100),
        }

        for field, (minimum, maximum) in numeric_fields.items():
            value = row.get(field, "").strip()

            if value:
                try:
                    number = float(value)

                    if not math.isfinite(number):
                        errors.append(f"Invalid number: {field}")
                    elif not minimum <= number <= maximum:
                        errors.append(f"Out of range: {field}")

                except ValueError:
                    errors.append(f"Invalid number: {field}")

        # Check duplicate timestamp and sensor combinations
        if timestamp and sensor_id:
            record_key = (timestamp, sensor_id)

            if record_key in seen_records:
                errors.append("Duplicate sensor reading")
            else:
                seen_records.add(record_key)

        if errors:
            rejected.append({
                **row,
                "validation_errors": "; ".join(errors),
            })
        else:
            valid.append(row)

    return valid, rejected


def validate_file(input_path, valid_path, rejected_path):
    """Read raw CSV, validate it, and save both output files."""

    with input_path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        readings = list(reader)

    valid, rejected = validate_readings(readings)

    valid_path.parent.mkdir(parents=True, exist_ok=True)
    rejected_path.parent.mkdir(parents=True, exist_ok=True)

    with valid_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(valid)

    rejected_fields = FIELDNAMES + ["validation_errors"]

    with rejected_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rejected_fields)
        writer.writeheader()
        writer.writerows(rejected)

    print("AtmoSync Data Validation")
    print("------------------------")
    print(f"Total readings: {len(readings)}")
    print(f"Valid readings: {len(valid)}")
    print(f"Rejected readings: {len(rejected)}")
    print(f"Valid data saved: {valid_path}")
    print(f"Rejected data saved: {rejected_path}")


def main():
    project_root = Path(__file__).resolve().parents[3]

    parser = argparse.ArgumentParser(
        description="Validate AtmoSync sensor data"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=project_root / "data/raw/sensor_readings.csv",
    )
    args = parser.parse_args()

    validate_file(
        args.input,
        project_root / "data/processed/validated_sensor_readings.csv",
        project_root / "data/processed/rejected_sensor_readings.csv",
    )


if __name__ == "__main__":
    main()
