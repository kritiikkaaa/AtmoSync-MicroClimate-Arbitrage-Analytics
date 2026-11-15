import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED = PROJECT_ROOT / "data" / "processed"

risk_by_container = {}

with (PROCESSED / "streaming_summary.csv").open(
    "r", newline="", encoding="utf-8"
) as file:
    for row in csv.DictReader(file):
        risk_by_container[row["container_id"]] = float(
            row["avg_temperature_risk_pct"]
        )

recommendations = []

with (PROCESSED / "arbitrage_analysis.csv").open(
    "r", newline="", encoding="utf-8"
) as file:
    for shipment in csv.DictReader(file):
        container_id = shipment["container_id"]
        risk = risk_by_container.get(container_id, 0.0)
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
            "temperature_risk_pct": round(risk, 2),
            "alternate_market": shipment["alternate_market"],
            "net_reroute_uplift": round(uplift, 2),
            "recommendation": action,
        })

output_file = PROCESSED / "reroute_recommendations.csv"
fieldnames = [
    "container_id",
    "commodity",
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
        f"{item['container_id']} | "
        f"Risk: {item['temperature_risk_pct']}% | "
        f"Uplift: ₹{item['net_reroute_uplift']:,.0f} | "
        f"{item['recommendation']}"
    )

print(f"\nSaved: {output_file}")