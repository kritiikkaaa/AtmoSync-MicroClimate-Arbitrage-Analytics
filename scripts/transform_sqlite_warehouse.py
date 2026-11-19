import csv
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_FILE = PROJECT_ROOT / "data" / "atmosync_warehouse.db"
OUTPUT_FILE = (
    PROJECT_ROOT / "data" / "processed" / "sqlite_mart.csv"
)

SQL = """
DROP VIEW IF EXISTS stg_sensor_readings;

CREATE VIEW stg_sensor_readings AS
SELECT
    TRIM(container_id) AS container_id,
    TRIM(commodity) AS commodity,
    TRIM(origin) AS origin,
    TRIM(destination) AS destination,
    TRIM(location_id) AS location_id,
    CAST(temperature_c AS REAL) AS temperature_c,
    CAST(humidity_pct AS REAL) AS humidity_pct,
    CAST(vibration_level AS REAL) AS vibration_level
FROM raw_sensor_readings
WHERE container_id IS NOT NULL
  AND TRIM(container_id) <> '';

DROP VIEW IF EXISTS stg_market_quotes;

CREATE VIEW stg_market_quotes AS
SELECT
    TRIM(container_id) AS container_id,
    TRIM(commodity) AS commodity,
    CAST(quantity_kg AS REAL) AS quantity_kg,
    CAST(origin_market_price_per_kg AS REAL) AS origin_price,
    TRIM(alternate_market) AS alternate_market,
    CAST(alternate_market_price_per_kg AS REAL) AS alternate_price,
    CAST(extra_freight_cost AS REAL) AS extra_freight_cost
FROM raw_market_quotes;

DROP TABLE IF EXISTS mart_container_analytics;

CREATE TABLE mart_container_analytics AS
WITH container_metrics AS (
    SELECT
        container_id,
        MAX(commodity) AS commodity,
        MAX(origin) AS origin,
        MAX(destination) AS destination,
        COUNT(*) AS event_count,
        ROUND(AVG(temperature_c), 2) AS avg_temperature_c,
        ROUND(AVG(humidity_pct), 2) AS avg_humidity_pct,
        ROUND(AVG(vibration_level), 3) AS avg_vibration_level,
        ROUND(AVG(
            CASE
                WHEN commodity = 'Mango'
                    THEN MIN(MAX(temperature_c - 13.0, 0.0) * 20.0, 100.0)
                WHEN commodity = 'Grapes'
                    THEN MIN(MAX(temperature_c - 4.0, 0.0) * 20.0, 100.0)
                WHEN commodity = 'Avocado'
                    THEN MIN(MAX(temperature_c - 7.0, 0.0) * 20.0, 100.0)
                ELSE 0.0
            END
        ), 2) AS avg_temperature_risk_pct
    FROM stg_sensor_readings
    GROUP BY container_id
),
economics AS (
    SELECT
        container_id,
        alternate_market,
        quantity_kg,
        origin_price,
        alternate_price,
        extra_freight_cost
    FROM stg_market_quotes
),
decision_base AS (
    SELECT
        m.*,
        e.alternate_market,
        ROUND(
            (e.alternate_price - e.origin_price) * e.quantity_kg
            - e.extra_freight_cost,
            2
        ) AS net_reroute_uplift
    FROM container_metrics AS m
    JOIN economics AS e USING (container_id)
)
SELECT
    container_id,
    commodity,
    origin,
    destination,
    alternate_market,
    event_count,
    avg_temperature_c,
    avg_humidity_pct,
    avg_vibration_level,
    avg_temperature_risk_pct,
    net_reroute_uplift,
    CASE
        WHEN avg_temperature_risk_pct >= 50
             AND net_reroute_uplift > 0
            THEN 'Reroute candidate'
        WHEN avg_temperature_risk_pct >= 50
            THEN 'High risk: expedite'
        WHEN net_reroute_uplift > 0
            THEN 'Review alternate market'
        ELSE 'Continue planned route'
    END AS recommendation
FROM decision_base;
"""

with sqlite3.connect(DATABASE_FILE) as connection:
    connection.executescript(SQL)
    cursor = connection.execute("""
        SELECT
            container_id,
            commodity,
            alternate_market,
            event_count,
            avg_temperature_risk_pct,
            net_reroute_uplift,
            recommendation
        FROM mart_container_analytics
        ORDER BY container_id
    """)
    columns = [item[0] for item in cursor.description]
    rows = cursor.fetchall()

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(columns)
    writer.writerows(rows)

print(f"Containers in SQL mart: {len(rows)}")
for row in rows:
    print(
        f"{row[0]} | Risk: {row[4]}% | "
        f"Uplift: ₹{row[5]:,.0f} | {row[6]}"
    )
print(f"Mart exported: {OUTPUT_FILE}")