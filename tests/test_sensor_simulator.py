from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone

from atmosync.simulation.sensor_simulator import CONTAINER_PROFILES, TelemetrySimulator


class TelemetrySimulatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.start = datetime(2026, 11, 27, 9, 0, tzinfo=timezone.utc)

    def test_event_conforms_to_week_one_contract(self) -> None:
        event = TelemetrySimulator(seed=7, start_time=self.start).next_event()

        self.assertEqual(event["schema_version"], "1.0")
        self.assertEqual(event["event_ts"], "2026-11-27T09:00:00Z")
        self.assertEqual(event["container_id"], CONTAINER_PROFILES[0].container_id)
        self.assertSetEqual(
            set(event["telemetry"]), {"temperature_c", "humidity_pct", "vibration_g"}
        )
        self.assertTrue(-30 <= event["telemetry"]["temperature_c"] <= 30)
        self.assertTrue(0 <= event["telemetry"]["humidity_pct"] <= 100)
        self.assertTrue(0 <= event["telemetry"]["vibration_g"] <= 5)
        self.assertIsInstance(json.dumps(event), str)

    def test_seed_makes_a_reproducible_stream(self) -> None:
        first = list(TelemetrySimulator(seed=99, start_time=self.start).events(6))
        second = list(TelemetrySimulator(seed=99, start_time=self.start).events(6))
        self.assertEqual(first, second)
        self.assertEqual(len({row["event_id"] for row in first}), 6)

    def test_container_a_has_a_visible_controlled_drift(self) -> None:
        events = list(TelemetrySimulator(seed=11, start_time=self.start).events(45))
        baseline = events[0]["telemetry"]["temperature_c"]
        drifted = events[30]["telemetry"]["temperature_c"]
        self.assertEqual(events[30]["container_id"], "CONT-A-AVO-001")
        self.assertGreater(drifted - baseline, 2.5)


if __name__ == "__main__":
    unittest.main()
