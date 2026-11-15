import csv
import json
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_ROOT / "data" / "stream" / "sensor_events.jsonl"
OUTPUT_FILE = (
    PROJECT_ROOT / "data" / "processed" / "streaming_summary.csv"
)

DEMO_TEMP_LIMIT_C = {
    "Mango": 13.0,
    "Grapes": 4.0,
    "Avocado": 7.0,
}

totals = defaultdict(
    lambda: {
        "commodity": "",
        "event_count": 0,
        "temperature_sum": 0.0,
        "humidity_sum": 0.0,
        "vibration_sum": 0.0,
        "risk_sum": 0.0,
    }
)

events_processed = 0

with INPUT_FILE.open("r", encoding="utf-8") as stream:
    for line in stream:
        event = json.loads(line)
        reading = event["payload"]
        container_id = reading["container_id"]
        commodity = reading["commodity"]

        temperature = float(reading["temperature_c"])
        humidity = float(reading["humidity_pct"])
        vibration = float(reading["vibration_level"])

        limit = DEMO_TEMP_LIMIT_C.get(commodity)
        risk = 0.0

        if limit is not None:
            risk = min(max(temperature - limit, 0.0) * 20, 100)

        result = totals[container_id]
        result["commodity"] = commodity
        result["event_count"] += 1
        result["temperature_sum"] += temperature
        result["humidity_sum"] += humidity
        result["vibration_sum"] += vibration
        result["risk_sum"] += risk

        events_processed += 1

results = []

for container_id, values in totals.items():
    count = values["event_count"]
    average_risk = values["risk_sum"] / count

    results.append({
        "container_id": container_id,
        "commodity": values["commodity"],
        "event_count": count,
        "avg_temperature_c": round(values["temperature_sum"] / count, 2),
        "avg_humidity_pct": round(values["humidity_sum"] / count, 2),
        "avg_vibration_level": round(values["vibration_sum"] / count, 3),
        "avg_temperature_risk_pct": round(average_risk, 2),
    })

fieldnames = [
    "container_id",
    "commodity",
    "event_count",
    "avg_temperature_c",
    "avg_humidity_pct",
    "avg_vibration_level",
    "avg_temperature_risk_pct",
]

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print(f"Events consumed: {events_processed}")
print(f"Containers summarized: {len(results)}")
print(f"Summary saved: {OUTPUT_FILE}")