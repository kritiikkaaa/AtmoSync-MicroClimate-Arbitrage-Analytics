
import unittest

from atmosync.processing.data_validator import validate_readings


class TestDataValidator(unittest.TestCase):

    def setUp(self):
        self.valid_reading = {
            "timestamp": "2026-11-10T12:00:00+00:00",
            "sensor_id": "SENSOR_001",
            "location_id": "LOCATION_A",
            "temperature_c": "10",
            "humidity_pct": "65",
            "soil_moisture_pct": "40",
        }

    def test_valid_reading(self):
        valid, rejected = validate_readings([self.valid_reading])

        self.assertEqual(len(valid), 1)
        self.assertEqual(len(rejected), 0)

    def test_invalid_humidity(self):
        reading = self.valid_reading.copy()
        reading["humidity_pct"] = "150"

        valid, rejected = validate_readings([reading])

        self.assertEqual(len(valid), 0)
        self.assertIn("Out of range: humidity_pct",
                      rejected[0]["validation_errors"])

    def test_unknown_sensor(self):
        reading = self.valid_reading.copy()
        reading["sensor_id"] = "SENSOR_999"

        valid, rejected = validate_readings([reading])

        self.assertEqual(len(rejected), 1)
        self.assertIn("Unknown sensor ID",
                      rejected[0]["validation_errors"])

    def test_missing_temperature(self):
        reading = self.valid_reading.copy()
        reading["temperature_c"] = ""

        valid, rejected = validate_readings([reading])

        self.assertEqual(len(rejected), 1)
        self.assertIn("Missing value: temperature_c",
                      rejected[0]["validation_errors"])

    def test_duplicate_reading(self):
        readings = [
            self.valid_reading,
            self.valid_reading.copy()
        ]

        valid, rejected = validate_readings(readings)

        self.assertEqual(len(valid), 1)
        self.assertEqual(len(rejected), 1)
        self.assertIn("Duplicate sensor reading",
                      rejected[0]["validation_errors"])

    def test_invalid_timestamp(self):
        reading = self.valid_reading.copy()
        reading["timestamp"] = "not-a-timestamp"

        valid, rejected = validate_readings([reading])

        self.assertEqual(len(rejected), 1)
        self.assertIn("Invalid timestamp",
                      rejected[0]["validation_errors"])


if __name__ == "__main__":
    unittest.main()
