
import unittest

from atmosync.analytics.microclimate_analyzer import analyze_locations


class TestMicroclimateAnalyzer(unittest.TestCase):

    def setUp(self):
        self.readings = [
            {
                "timestamp": "2026-11-10T12:00:00+00:00",
                "sensor_id": "SENSOR_001",
                "location_id": "LOCATION_A",
                "temperature_c": "10",
                "humidity_pct": "60",
                "soil_moisture_pct": "40",
            },
            {
                "timestamp": "2026-11-10T12:05:00+00:00",
                "sensor_id": "SENSOR_002",
                "location_id": "LOCATION_B",
                "temperature_c": "20",
                "humidity_pct": "80",
                "soil_moisture_pct": "60",
            },
            {
                "timestamp": "2026-11-10T12:10:00+00:00",
                "sensor_id": "SENSOR_003",
                "location_id": "LOCATION_C",
                "temperature_c": "15",
                "humidity_pct": "70",
                "soil_moisture_pct": "50",
            },
        ]

    def test_location_count(self):
        results = analyze_locations(self.readings)
        self.assertEqual(len(results), 3)

    def test_average_temperature(self):
        results = analyze_locations(self.readings)

        location_a = next(
            item for item in results
            if item["location_id"] == "LOCATION_A"
        )

        self.assertEqual(location_a["avg_temperature_c"], 10.0)

    def test_highest_divergence_ranked_first(self):
        results = analyze_locations(self.readings)

        self.assertEqual(
            results[0]["location_id"],
            "LOCATION_A"
        )

    def test_divergence_score_is_non_negative(self):
        results = analyze_locations(self.readings)

        for result in results:
            self.assertGreaterEqual(
                result["divergence_score"], 0
            )

    def test_empty_readings(self):
        with self.assertRaises(ValueError):
            analyze_locations([])

    def test_identical_locations_have_zero_divergence(self):
        readings = [
            {
                "timestamp": "2026-11-10T12:00:00+00:00",
                "sensor_id": "SENSOR_001",
                "location_id": "LOCATION_A",
                "temperature_c": "10",
                "humidity_pct": "60",
                "soil_moisture_pct": "40",
            },
            {
                "timestamp": "2026-11-10T12:05:00+00:00",
                "sensor_id": "SENSOR_002",
                "location_id": "LOCATION_B",
                "temperature_c": "10",
                "humidity_pct": "60",
                "soil_moisture_pct": "40",
            },
        ]

        results = analyze_locations(readings)

        for result in results:
            self.assertEqual(result["divergence_score"], 0)


if __name__ == "__main__":
    unittest.main()
