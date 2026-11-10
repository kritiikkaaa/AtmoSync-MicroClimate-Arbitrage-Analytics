"""Generate synthetic microclimate sensor readings."""

import argparse
import csv
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path


def generate_readings(count: int = 100, seed: int = 42) -> list[dict]:
    """Generate reproducible synthetic sensor readings."""

    if count <= 0:
        raise ValueError("Number of readings must be positive.")

    rng = random.Random(seed)

    sensors = {
        "SENSOR_001": "LOCATION_A",
        "SENSOR_002": "LOCATION_B",
        "SENSOR_003": "LOCATION_C",
    }

    start_time = datetime.now(timezone.utc)
    readings = []

    for i in range(count):
        sensor_id = list(sensors.keys())[i % len(sensors)]
        location_id = sensors[sensor_id]

        readings.append({
            "timestamp": (
                start_time + timedelta(minutes=5 * i)
            ).isoformat(),
            "sensor_id": sensor_id,
            "location_id": location_id,
            "temperature_c": round(rng.uniform(2, 15), 2),
            "humidity_pct": round(rng.uniform(40, 95), 2),
            "soil_moisture_pct": round(rng.uniform(20, 80), 2),
        })

    return readings


def save_readings(readings: list[dict], output_path: Path) -> None:
    """Save sensor readings to a CSV file."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=readings[0].keys()
        )
        writer.writeheader()
        writer.writerows(readings)


def main():
    parser = argparse.ArgumentParser(
        description="AtmoSync Microclimate Sensor Simulator"
    )
    parser.add_argument("--readings", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[3]
    output_path = project_root / "data" / "raw" / "sensor_readings.csv"

    readings = generate_readings(args.readings, args.seed)
    save_readings(readings, output_path)

    print("AtmoSync Sensor Simulator")
    print("-------------------------")
    print(f"Readings generated: {len(readings)}")
    print(f"Sensors used: 3")
    print(f"Locations monitored: 3")
    print(f"Output file: {output_path}")


if __name__ == "__main__":
    main()
