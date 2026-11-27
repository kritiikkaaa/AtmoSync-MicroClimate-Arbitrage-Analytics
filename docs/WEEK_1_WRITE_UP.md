# Week 1 Write-Up — AtmoSync Ingestion and BI Foundations

**Project:** AtmoSync: Micro-Climate Arbitrage Analytics  
**Role:** Data Associate L1 Intern  
**Week focus:** Streaming ingestion architecture and business-intelligence foundations

## Objective

The Week 1 goal was to establish a dependable path for continuous mock IoT readings: generate container telemetry, publish it through Kafka, retain the original payload in Snowflake, and prepare the Superset environment that analysts will use to inspect the data.

## Work completed

1. Defined the telemetry contract for container ID, route, commodity, destination market, timestamp, temperature, humidity, vibration, and approximate location.
2. Built a deterministic Python simulator for three mock shipments. It emits newline-delimited JSON and deliberately introduces a warm/humid period for Container A so downstream monitoring can be tested.
3. Implemented a Kafka producer for the `atmosync.telemetry.v1` topic. It supports normal publishing, topic creation, and an offline `--dry-run` mode.
4. Created a local Docker Compose foundation containing a single-node Kafka broker and Apache Superset with its metadata services.
5. Designed the Snowflake database, warehouse, roles, schemas, and immutable `RAW_IOT_TELEMETRY` table. The table preserves the full JSON message in a `VARIANT` column alongside Kafka topic, partition, and offset metadata.
6. Implemented a consumer-loader design that inserts a batch into Snowflake before committing the associated Kafka offsets.
7. Prepared initial Superset connection/role instructions and a raw-telemetry table view specification.

## Key implementation evidence

| Item | Location |
| --- | --- |
| Simulator | `src/atmosync/simulation/sensor_simulator.py` |
| Kafka producer | `src/atmosync/streaming/kafka_producer.py` |
| Kafka → Snowflake loader | `src/atmosync/streaming/snowflake_loader.py` |
| Local services | `docker-compose.yml` |
| Snowflake bootstrap | `sql/snowflake/00_bootstrap.sql` |
| Superset setup | `docs/SUPERSET_SETUP.md` |

## Design decisions

Kafka was selected so sensor generation does not depend on the availability or throughput of the loader. Snowflake receives a raw, immutable JSON copy before transformations, which preserves traceability and allows the dbt layer to evolve without losing source context. The manual offset commit is important: a message is only acknowledged after the batch reaches Snowflake.

The project uses synthetic data only. No company, customer, route, or pricing data is embedded in the repository.

## Verification performed

Offline unit tests validate the event schema, seeded reproducibility, valid sensor ranges, controlled drift behavior, price-seed structure, and Kafka dry-run serialization. Execute:

```bash
export PYTHONPATH=src
python3 -m unittest discover -s tests -v
```

The full Kafka/Snowflake validation requires Docker, a Snowflake account, and credentials. It is intentionally not claimed as complete until the review commands in `MID_PROJECT_REVIEW.md` have been run and their evidence recorded.

## Week 1 outcome

The ingestion architecture and its executable local components are ready. The next step is to make the raw events analytically useful with dbt and to establish the first operational visualizations.
