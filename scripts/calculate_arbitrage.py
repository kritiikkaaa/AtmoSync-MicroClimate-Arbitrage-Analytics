import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "market_quotes.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "arbitrage_analysis.csv"

with INPUT_FILE.open("r", newline="", encoding="utf-8") as file:
    quotes = list(csv.DictReader(file))

results = []

for quote in quotes:
    quantity = float(quote["quantity_kg"])
    origin_price = float(quote["origin_market_price_per_kg"])
    alternate_price = float(quote["alternate_market_price_per_kg"])
    freight = float(quote["extra_freight_cost"])

    uplift = (alternate_price - origin_price) * quantity - freight

    results.append({
        "container_id": quote["container_id"],
        "commodity": quote["commodity"],
        "alternate_market": quote["alternate_market"],
        "net_reroute_uplift": round(uplift, 2),
        "recommendation": (
            "Positive uplift" if uplift > 0 else "No positive uplift"
        ),
    })

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

fieldnames = [
    "container_id",
    "commodity",
    "alternate_market",
    "net_reroute_uplift",
    "recommendation",
]

with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

for result in results:
    print(
        f"{result['container_id']} | "
        f"Net uplift: ₹{result['net_reroute_uplift']:,.0f} | "
        f"{result['recommendation']}"
    )

print(f"\nSaved: {OUTPUT_FILE}")