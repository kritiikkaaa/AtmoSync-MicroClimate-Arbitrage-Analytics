# Mid-Project Review — Week 1–2 Evidence Pack

## Review purpose

The project brief defines three review gates after Week 2:

1. **Pipeline validation:** demonstrate that Kafka handles high-frequency event streams without lag.
2. **ELT validation:** demonstrate that the dbt staging models compile successfully.
3. **Data-integrity check:** demonstrate that Superset renders raw Snowflake tables correctly.

The review is not a final arbitrage demonstration. The advanced spoilage-arbitrage metric, at-risk rerouting interface, scheduling, and alerts belong to Weeks 3–4.

## What to prepare before the review

- A Docker-capable machine with the local Kafka/Superset services running.
- A Snowflake account with the `00_bootstrap.sql` objects created and `.env` credentials set locally.
- A copy of `dbt_atmosync/profiles.yml.example` saved as `profiles.yml` with valid account access.
- An assigned Superset analyst/service user with only the required role grants.
- Screen recording or screenshots of each command/result below.

## Demonstration runbook

### 1. Show high-frequency Kafka ingestion and no consumer lag

Start the local services, create the topic, and send a burst of messages:

```bash
docker compose up -d kafka
export PYTHONPATH=src
python3 -m atmosync.streaming.kafka_producer --create-topic --count 0
python3 -m atmosync.streaming.kafka_producer --count 1000 --interval-seconds 0
```

Run the loader in another terminal until it reports 1,000 loaded messages:

```bash
python3 -m atmosync.streaming.snowflake_loader --max-messages 1000
```

Then inspect the consumer group from the Kafka container:

```bash
docker compose exec kafka /opt/kafka/bin/kafka-consumer-groups.sh \
  --bootstrap-server kafka:9092 \
  --describe --group atmosync-snowflake-loader-v1
```

**Pass condition:** each topic partition shows `LAG` of `0` after the loader finishes, and Snowflake has 1,000 newly ingested rows for the test run. Capture the producer result, loader total, consumer-group output, and Snowflake count.

```sql
select count(*) as raw_rows, min(ingested_at) as first_ingested_at, max(ingested_at) as last_ingested_at
from ATMOSYNC.RAW.RAW_IOT_TELEMETRY;
```

### 2. Show that dbt staging models compile and tests run

```bash
cd dbt_atmosync
dbt debug
dbt seed
dbt compile
dbt build
```

**Pass condition:** `dbt compile` exits successfully, and `dbt build` reports successful `stg_iot_telemetry`, `stg_commodity_prices`, `int_container_telemetry_enriched`, and their tests. Capture the terminal summary and `target/manifest.json` timestamp.

### 3. Show raw data integrity in Superset

1. Sign in at `http://localhost:8088`.
2. Add the Snowflake database connection using the analyst role, as documented in `docs/SUPERSET_SETUP.md`.
3. Register `ATMOSYNC.RAW.RAW_IOT_TELEMETRY` as the **Raw telemetry integrity** dataset.
4. Create the table using `EVENT_ID`, `EVENT_TS`, `CONTAINER_ID`, `KAFKA_TOPIC`, `KAFKA_PARTITION`, `KAFKA_OFFSET`, and `INGESTED_AT`.
5. Compare the dashboard row count to the Snowflake count query above and inspect several `PAYLOAD` values against the producer output.

**Pass condition:** the dashboard displays the raw Snowflake rows with the expected IDs/timestamps and its count agrees with Snowflake. Capture the database connection test, table chart, and count comparison.

## Evidence record

| Gate | Evidence to attach | Result |
| --- | --- | --- |
| Kafka throughput | Producer total, loader total, consumer-group lag screen, Snowflake count | To be recorded after connected run |
| dbt compile/build | `dbt debug`, `dbt compile`, `dbt build` terminal output | To be recorded after connected run |
| Superset raw integrity | Raw-table screenshot and matching Snowflake count | To be recorded after connected run |
| Offline code checks | `python3 -m unittest discover -s tests -v` output | Run locally before review |

## Review talking points

- The sensor simulator purposely introduces an observable drift into Container A. It validates the monitoring path without fabricating a trading result.
- The raw Snowflake table retains the original JSON payload and Kafka coordinates, allowing analysts to trace every cleaned field back to its source event.
- dbt is responsible for validation, typing, and the price reference join. The join creates a reliable starting dataset but does not yet calculate arbitrage.
- The baseline dashboard verifies visibility and data integrity. A financial decision dashboard follows only after the Week 3 model is validated.
