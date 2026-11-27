# Superset Setup — Week 1–2 Baseline Monitoring

## Purpose

This guide deploys the local Superset service and connects it to Snowflake with least-privilege, read-only access. The goal is to render raw telemetry for the mid-project integrity check and then render the Week 2 enriched baseline dataset.

## Start the local service

1. Copy `.env.example` to `.env` and change `SUPERSET_SECRET_KEY` and the admin password.
2. Build and start the service:

   ```bash
   docker compose up -d --build superset
   docker compose logs -f superset
   ```

3. When initialization completes, visit `http://localhost:8088` and sign in with the local `SUPERSET_ADMIN_*` values.

The supplied Dockerfile includes the Snowflake SQLAlchemy driver. This local stack is for development and review; use managed secrets, HTTPS, and production deployment controls outside the prototype.

## Configure Snowflake access

1. Run `sql/snowflake/00_bootstrap.sql` as an appropriate Snowflake administrator.
2. Run dbt `seed` and `build`, then run `sql/snowflake/01_grants.sql`.
3. In Superset, open **Settings → Database Connections → + Database** and choose **Snowflake**.
4. Use a URI with the `ATMOSYNC_ANALYST` role (the `.env` template calls this `SNOWFLAKE_SUPERSET_ROLE`). URL-encode special characters in the password:

   ```text
   snowflake://<user>:<url-encoded-password>@<account>/ATMOSYNC/RAW?warehouse=ATMOSYNC_WH&role=ATMOSYNC_ANALYST
   ```

5. Press **Test Connection**, then save. Do not use the ingestion role or an account-admin role in Superset.

## Register the baseline datasets

Create these datasets through **Data → Datasets → + Dataset**:

| Dataset name | Snowflake object | Use |
| --- | --- | --- |
| Raw telemetry integrity | `ATMOSYNC.RAW.RAW_IOT_TELEMETRY` | Mid-review data-integrity table |
| Container telemetry enriched | `ATMOSYNC.ANALYTICS.INT_CONTAINER_TELEMETRY_ENRICHED` | Temperature and route charts |

Mark `EVENT_TS` as the temporal field on both datasets. In the enriched dataset, ensure `TEMPERATURE_C`, `HUMIDITY_PCT`, `VIBRATION_G`, and `MARKET_PRICE_INR_PER_KG` are numeric columns.

## Build the three Week 2 charts

Use `superset/dataset_and_chart_specs.yml` as the versioned specification.

1. **Raw telemetry integrity table:** select event/time/container and Kafka coordinate columns; sort by `INGESTED_AT` descending.
2. **Container temperature over time:** choose a time-series line chart, `EVENT_TS` as time, average `TEMPERATURE_C` as metric, and `CONTAINER_ID` as group by.
3. **Route health summary:** choose a table grouped by `ROUTE_ID`, `CONTAINER_ID`, and `TEMPERATURE_STATUS`; show reading count, latest timestamp, and average temperature.

Save them to a dashboard called **AtmoSync — Week 2 Baseline Monitoring**.

## Mid-review integrity query

Run this in Snowflake and compare the count with the raw table in Superset:

```sql
select count(*) as raw_rows
from ATMOSYNC.RAW.RAW_IOT_TELEMETRY;
```

The identity and timestamps of several visible Superset rows should match the raw Snowflake table. This is the required review proof; it is stronger than merely showing that a dashboard page loads.
