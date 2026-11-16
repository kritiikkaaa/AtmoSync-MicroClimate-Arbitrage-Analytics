import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

steps = [
    (
        "Generate sensor readings",
        "src/atmosync/simulation/sensor_simulator.py",
        ["--readings", "1000", "--seed", "7"],
    ),
    (
        "Validate sensor readings",
        "src/atmosync/processing/data_validator.py",
        [],
    ),
    (
        "Analyze microclimate",
        "src/atmosync/analytics/microclimate_analyzer.py",
        [],
    ),
    (
        "Build sensor charts",
        "scripts/analyze_sensor_data.py",
        [],
    ),
    (
        "Stream sensor events",
        "scripts/stream_sensor_data.py",
        [],
    ),
    (
        "Consume event stream",
        "scripts/consume_sensor_stream.py",
        [],
    ),
    (
        "Calculate market uplift",
        "scripts/calculate_arbitrage.py",
        [],
    ),
    (
        "Create streaming recommendations",
        "scripts/make_streaming_recommendations.py",
        [],
    ),
    (
        "Load SQLite warehouse",
        "scripts/load_sqlite_warehouse.py",
        [],
    ),
    (
        "Transform SQLite warehouse",
        "scripts/transform_sqlite_warehouse.py",
        [],
    ),
    (
        "Build arbitrage dashboard",
        "scripts/build_arbitrage_dashboard.py",
        [],
    ),
   ]

for name, script, arguments in steps:
    print(f"\n=== {name} ===", flush=True)
    subprocess.run(
        [sys.executable, str(PROJECT_ROOT / script), *arguments],
        cwd=PROJECT_ROOT,
        check=True,
    )

dashboard = PROJECT_ROOT / "reports" / "charts" / "arbitrage_dashboard.html"
print(f"\nPipeline complete. Dashboard: {dashboard}")