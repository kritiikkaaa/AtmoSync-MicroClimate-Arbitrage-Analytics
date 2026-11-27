from __future__ import annotations

import csv
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from atmosync.dashboard.server import create_dashboard_snapshot
from atmosync.streaming.kafka_producer import publish


ROOT = Path(__file__).resolve().parents[1]


class ProjectContractTests(unittest.TestCase):
    def test_week_two_price_seed_has_positive_prices(self) -> None:
        with (ROOT / "dbt_atmosync/seeds/commodity_prices.csv").open(newline="") as source:
            rows = list(csv.DictReader(source))
        self.assertGreaterEqual(len(rows), 12)
        self.assertTrue(all(float(row["market_price_inr_per_kg"]) > 0 for row in rows))
        self.assertTrue(all(row["currency"] == "INR" for row in rows))

    def test_dbt_models_reference_raw_data_and_the_price_join(self) -> None:
        staging = (ROOT / "dbt_atmosync/models/staging/stg_iot_telemetry.sql").read_text()
        enriched = (ROOT / "dbt_atmosync/models/intermediate/int_container_telemetry_enriched.sql").read_text()
        self.assertIn("source('raw', 'raw_iot_telemetry')", staging)
        self.assertIn("left join prices", enriched)
        self.assertIn("temperature_status", enriched)

    def test_dry_run_publishes_json_without_kafka_dependency(self) -> None:
        output = io.StringIO()
        event = {"event_id": "test-1", "container_id": "CONT-1"}
        with redirect_stdout(output):
            sent = publish([event], "not-used", "test-topic", dry_run=True)
        self.assertEqual(sent, 1)
        self.assertIn('"event_id":"test-1"', output.getvalue())

    def test_local_dashboard_snapshot_has_review_data(self) -> None:
        snapshot = create_dashboard_snapshot(event_count=45)
        containers = snapshot["containers"]
        self.assertEqual(snapshot["total_readings"], 45)
        self.assertEqual(snapshot["container_count"], 3)
        self.assertEqual(len(snapshot["raw_rows"]), 12)
        self.assertGreater(snapshot["at_risk_events"], 0)
        self.assertTrue(any(row["container_id"] == "CONT-A-AVO-001" for row in containers))


if __name__ == "__main__":
    unittest.main()
