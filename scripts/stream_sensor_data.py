import argparse
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "sensor_readings.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "stream" / "sensor_events.jsonl"


def main():
    parser = argparse.ArgumentParser(
        description="Simulate a local stream of sensor events"
    )
    parser.add_argument(
        "--delay-ms",
        type=float,
        default=5,
        help="Pause between events in milliseconds",
    )
    args = parser.parse_args()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with INPUT_FILE.open("r", newline="", encoding="utf-8") as source:
        readings = csv.DictReader(source)

        with OUTPUT_FILE.open("w", encoding="utf-8") as stream:
            for event_id, reading in enumerate(readings, start=1):
                event = {
                    "event_id": event_id,
                    "topic": "sensor-readings",
                    "key": reading.get("container_id", reading.get("sensor_id", "unknown")),
                    "emitted_at": datetime.now(timezone.utc).isoformat(),
                    "payload": reading,
                }

                stream.write(json.dumps(event) + "\n")
                stream.flush()

                if event_id % 100 == 0:
                    print(f"Events emitted: {event_id}")

                if args.delay_ms > 0:
                    time.sleep(args.delay_ms / 1000)

    print(f"Stream saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()