
"""Compare environmental conditions across AtmoSync locations."""

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean


METRICS = [
    "temperature_c",
    "humidity_pct",
    "soil_moisture_pct",
]
DEMO_TEMP_LIMIT_C = {
    "Mango": 13.0,
    "Grapes": 4.0,
    "Avocado": 7.0,
}


def temperature_risk_score(reading):
    """Return a demo risk score based on one reading's temperature."""
    commodity = reading.get("commodity", "").strip()
    limit = DEMO_TEMP_LIMIT_C.get(commodity)

    if limit is None:
        return 0.0

    excess = max(0.0, float(reading["temperature_c"]) - limit)
    return round(min(excess * 20, 100), 2)

def load_readings(input_path):
    """Load validated sensor readings from CSV."""

    with input_path.open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def analyze_locations(readings):
    """Calculate location averages and microclimate divergence scores."""

    if not readings:
        raise ValueError("No validated readings available for analysis.")

    locations = defaultdict(list)

    for reading in readings:
        locations[reading["location_id"]].append(reading)

    summaries = {}
    for location_id, location_readings in locations.items():
        summaries[location_id] = {
            "location_id": location_id,
            "readings_count": len(location_readings),
        }

        for metric in METRICS:
            values = [float(row[metric]) for row in location_readings]
            summaries[location_id][f"avg_{metric}"] = round(mean(values), 2)

        risk_scores = [
            temperature_risk_score(reading)
            for reading in location_readings
            if reading.get("commodity")
        ]

        summaries[location_id]["avg_temperature_risk_pct"] = (
            round(mean(risk_scores), 2) if risk_scores else 0.0
        )


     # Calculate network-wide averages
    network_averages = {}

    for metric in METRICS:
        network_averages[metric] = mean(
            summary[f"avg_{metric}"]
            for summary in summaries.values()
        )

    # Calculate the observed range between location averages
    metric_ranges = {}

    for metric in METRICS:
        values = [
            summary[f"avg_{metric}"]
            for summary in summaries.values()
        ]
        metric_ranges[metric] = max(values) - min(values)

    # Calculate divergence relative to network averages
    results = []

    for location_id, summary in summaries.items():
        deviations = []

        for metric in METRICS:
            location_average = summary[f"avg_{metric}"]
            network_average = network_averages[metric]
            observed_range = metric_ranges[metric]

            if observed_range == 0:
                deviation = 0
            else:
                deviation = (
                    abs(location_average - network_average)
                    / observed_range
                )

            deviations.append(deviation)

        score = mean(deviations) * 100

        results.append({
            **summary,
            "divergence_score": round(score, 2),
        })

    results.sort(
        key=lambda item: item["divergence_score"],
        reverse=True,
    )

    return results


def save_analysis(results, output_path):
    """Save location analysis to CSV."""

    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "location_id",
        "readings_count",
        "avg_temperature_c",
        "avg_temperature_risk_pct",
        "avg_humidity_pct",
        "avg_soil_moisture_pct",
        "divergence_score",
    ]

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def main():
    project_root = Path(__file__).resolve().parents[3]

    parser = argparse.ArgumentParser(
        description="AtmoSync Microclimate Analytics Engine"
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=(
            project_root
            / "data/processed/validated_sensor_readings.csv"
        ),
    )

    args = parser.parse_args()

    readings = load_readings(args.input)
    results = analyze_locations(readings)

    output_path = (
        project_root / "data/processed/microclimate_analysis.csv"
    )

    save_analysis(results, output_path)

    print("AtmoSync Microclimate Analytics")
    print("--------------------------------")
    print(f"Locations analyzed: {len(results)}")

    for rank, result in enumerate(results, start=1):
        print(
            f"{rank}. {result['location_id']} | "
            f"Temperature risk: {result['avg_temperature_risk_pct']}% | "
            f"Divergence score: {result['divergence_score']}"
        )
    print(f"\nAnalysis saved: {output_path}")


if __name__ == "__main__":
    main()
