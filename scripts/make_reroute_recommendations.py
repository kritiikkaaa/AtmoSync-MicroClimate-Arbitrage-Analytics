import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA = PROJECT_ROOT / "data"
PROCESSED = DATA / "processed"

location_by_container = {}
with (PROCESSED / "validated_sensor_readings.csv").open(
    "r", newline="", encoding="utf-8"
) as file:
    for reading in csv.DictReader(file):
        location_by_container[reading["container_id"]] = reading["location_id"]

risk_by_location = {}
with (PROCESSED / "microclimate_analysis.csv").open(
    "r", newline="", encoding="utf-8"
) as file:
    for summary in csv.DictReader(file):
        risk_by_location[summary["location_id"]] = float(
            summary["avg_temperature_risk_pct"]
        )

recommendations = []
with (PROCESSED / "arbitrage_analysis.csv").open(
    "r", newline="", encoding="utf-8"
) as file:
    for shipment in csv.DictReader(file):
        container_id = shipment["container_id"]
        location_id = location_by_container.get(container_id, "")
        risk = risk_by_location.get(location_id, 0.0)
        uplift = float(shipment["net_reroute_uplift"])

        if risk >= 50 and uplift > 0:
            action = "Reroute candidate"
        elif risk >= 50:
            action = "High risk: expedite"
        elif uplift > 0:
            action = "Review alternate market"
        else:
            action = "Continue planned route"

        recommendations.append({
            "container_id": container_id,
            "commodity": shipment["commodity"],
            "location_id": location_id,
            "temperature_risk_pct": round(risk, 2),
            "alternate_market": shipment["alternate_market"],
            "net_reroute_uplift": round(uplift, 2),
            "recommendation": action,
        })

output_file = PROCESSED / "reroute_recommendations.csv"
fieldnames = [
    "container_id",
    "commodity",
    "location_id",
    "temperature_risk_pct",
    "alternate_market",
    "net_reroute_uplift",
    "recommendation",
]

with output_file.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(recommendations)

for item in recommendations:
    print(
        f"{item['container_id']} | Risk: "
        f"{item['temperature_risk_pct']}% | "
        f"Uplift: ₹{item['net_reroute_uplift']:,.0f} | "
        f"{item['recommendation']}"
    )

print(f"\nSaved: {output_file}")