
"""Generate synthetic IoT telemetry for AtmoSync shipping containers."""

import argparse
import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


CONTAINERS = [
    {
        "sensor_id": "SENSOR_001",
        "container_id": "CONT_001",
        "location_id": "LOCATION_A",
        "commodity": "Mango",
        "origin": "Mumbai",
        "destination": "Delhi",
    },
    {
        "sensor_id": "SENSOR_002",
        "container_id": "CONT_002",
        "location_id": "LOCATION_B",
        "commodity": "Grapes",
        "origin": "Nashik",
        "destination": "Bengaluru",
    },
    {
        "sensor_id": "SENSOR_003",
        "container_id": "CONT_003",
        "location_id": "LOCATION_C",
        "commodity": "Avocado",
        "origin": "Pune",
        "destination": "Mumbai",
    },
]

FIELDNAMES = [
    "timestamp",
    "sensor_id",
    "container_id",
    "commodity",
    "origin",
    "destination",
    "location_id",
    "temperature_c",
    "humidity_pct",
    "vibration_level",
    "soil_moisture_pct",
]


def generate_readings(count: int = 100, seed: int = 42) -> list[dict]:
    """Generate reproducible synthetic container sensor readings."""

    if count <= 0:
        raise ValueError("Number of readings must be positive.")

    rng = random.Random(seed)
    start_time = datetime.now(timezone.utc)
    readings = []

    for i in range(count):
        container = CONTAINERS[i % len(CONTAINERS)]

        reading = {
            "timestamp": (
                start_time + timedelta(minutes=5 * i)
            ).isoformat(),
            "sensor_id": container["sensor_id"],
            "container_id": container["container_id"],
            "commodity": container["commodity"],
            "origin": container["origin"],
            "destination": container["destination"],
            "location_id": container["location_id"],
            "temperature_c": round(rng.uniform(2, 15), 2),
            "humidity_pct": round(rng.uniform(40, 95), 2),
            "vibration_level": round(rng.uniform(0.05, 1.20), 2),
            "soil_moisture_pct": round(rng.uniform(20, 80), 2),
        }

        readings.append(reading)

    return readings


def save_readings(readings: list[dict], output_path: Path) -> None:
    """Save simulated readings to a CSV file."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(readings)


def main():
    parser = argparse.ArgumentParser(
        description="AtmoSync Container Sensor Simulator"
    )
    parser.add_argument("--readings", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[3]
    output_path = project_root / "data" / "raw" / "sensor_readings.csv"

    readings = generate_readings(args.readings, args.seed)
    save_readings(readings, output_path)

    print("AtmoSync Container Sensor Simulator")
    print("-----------------------------------")
    print(f"Readings generated: {len(readings)}")
    print(f"Sensors used: {len(CONTAINERS)}")
    print(f"Containers monitored: {len(CONTAINERS)}")
    print(f"Commodities monitored: Mango, Grapes, Avocado")
    print(f"Output file: {output_path}")


if __name__ == "__main__":
    main()
