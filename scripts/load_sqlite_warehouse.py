import csv
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA = PROJECT_ROOT / "data"
PROCESSED = DATA / "processed"

SENSOR_FILE = PROCESSED / "validated_sensor_readings.csv"
QUOTE_FILE = DATA / "raw" / "market_quotes.csv"
DATABASE_FILE = DATA / "atmosync_warehouse.db"

SENSOR_FIELDS = [
    "timestamp",
    "sensor_id",
    "container_id",
    "commodity",
    "origin",
    "destination",
    "location_id",
    "temperature_c",
    "humidity_pct",
    "vibration_level",
    "soil_moisture_pct",
]

QUOTE_FIELDS = [
    "container_id",
    "commodity",
    "quantity_kg",
    "origin_market_price_per_kg",
    "alternate_market",
    "alternate_market_price_per_kg",
    "extra_freight_cost",
]

with SENSOR_FILE.open("r", newline="", encoding="utf-8") as file:
    sensor_rows = list(csv.DictReader(file))

with QUOTE_FILE.open("r", newline="", encoding="utf-8") as file:
    quote_rows = list(csv.DictReader(file))

with sqlite3.connect(DATABASE_FILE) as connection:
    connection.execute("""
        CREATE TABLE IF NOT EXISTS raw_sensor_readings (
            timestamp TEXT,
            sensor_id TEXT,
            container_id TEXT,
            commodity TEXT,
            origin TEXT,
            destination TEXT,
            location_id TEXT,
            temperature_c REAL,
            humidity_pct REAL,
            vibration_level REAL,
            soil_moisture_pct REAL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS raw_market_quotes (
            container_id TEXT,
            commodity TEXT,
            quantity_kg INTEGER,
            origin_market_price_per_kg REAL,
            alternate_market TEXT,
            alternate_market_price_per_kg REAL,
            extra_freight_cost REAL
        )
    """)

    connection.execute("DELETE FROM raw_sensor_readings")
    connection.execute("DELETE FROM raw_market_quotes")

    sensor_sql = (
        "INSERT INTO raw_sensor_readings VALUES "
        "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    )
    quote_sql = (
        "INSERT INTO raw_market_quotes VALUES "
        "(?, ?, ?, ?, ?, ?, ?)"
    )

    connection.executemany(
        sensor_sql,
        [tuple(row[field] for field in SENSOR_FIELDS) for row in sensor_rows],
    )
    connection.executemany(
        quote_sql,
        [tuple(row[field] for field in QUOTE_FIELDS) for row in quote_rows],
    )

    sensor_count = connection.execute(
        "SELECT COUNT(*) FROM raw_sensor_readings"
    ).fetchone()[0]
    quote_count = connection.execute(
        "SELECT COUNT(*) FROM raw_market_quotes"
    ).fetchone()[0]

print(f"Sensor rows loaded: {sensor_count}")
print(f"Market quote rows loaded: {quote_count}")
print(f"SQLite warehouse: {DATABASE_FILE}")