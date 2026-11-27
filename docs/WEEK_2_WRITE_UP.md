# Week 2 Write-Up — ELT Pipeline and Baseline Analytics

**Project:** AtmoSync: Micro-Climate Arbitrage Analytics  
**Role:** Data Associate L1 Intern  
**Week focus:** dbt ELT models, mock price reference data, and initial dashboards

## Objective

The Week 2 goal was to convert raw Snowflake JSON events into reliable analytical fields, combine them with commodity-price data, and define baseline visuals for temperature and shipment routes. This creates the trusted data base needed before building the Week 3 spoilage-arbitrage calculation.

## Work completed

1. Configured a dbt Core project using a Snowflake profile template and explicit `RAW`, `REFERENCE`, and `ANALYTICS` schemas.
2. Added a versioned mock commodity-price seed for avocados and mangoes in the relevant destination markets.
3. Created `stg_iot_telemetry`, which decodes the raw `VARIANT` payload; types timestamps and measurements; removes duplicate event IDs; and filters invalid sensor ranges.
4. Created `stg_commodity_prices`, which cleans the reference seed and retains only positive prices.
5. Created `int_container_telemetry_enriched`, which joins valid telemetry to same-day, destination-market prices and supplies a baseline temperature status label.
6. Added dbt model tests for required identifiers, uniqueness, valid sensor ranges, permitted statuses, and price-join coverage on seeded dates.
7. Defined initial Superset datasets and chart specifications for raw-message integrity, temperature-over-time, and route/container health.

## Key implementation evidence

| Item | Location |
| --- | --- |
| dbt configuration | `dbt_atmosync/dbt_project.yml` |
| Raw source and staging models | `dbt_atmosync/models/staging/` |
| Enriched telemetry model | `dbt_atmosync/models/intermediate/int_container_telemetry_enriched.sql` |
| dbt schema/data tests | `dbt_atmosync/models/schema.yml`, `dbt_atmosync/tests/` |
| Versioned mock prices | `dbt_atmosync/seeds/commodity_prices.csv` |
| Superset chart specification | `superset/dataset_and_chart_specs.yml` |

## Initial dashboard design

The Week 2 dashboard is deliberately descriptive rather than prescriptive:

- **Raw telemetry integrity table:** proves that Superset can read Snowflake raw rows and exposes Kafka metadata.
- **Container temperature over time:** plots `temperature_c` by timestamp and container to make the Container A drift visible.
- **Route health summary:** aggregates reading count, latest temperature, and temperature-status counts by route and container.

No chart claims to compute financial arbitrage, spoilage probability, or a reroute recommendation. Those features require the Week 3 degradation/market-distance model.

## Verification performed

The repository’s standard-library tests can be executed without cloud access:

```bash
export PYTHONPATH=src
python3 -m unittest discover -s tests -v
```

When Snowflake credentials are available, the required ELT verification is:

```bash
cd dbt_atmosync
cp profiles.yml.example profiles.yml
dbt seed
dbt build
```

`dbt build` must complete with the staging, intermediate, and test nodes successful. The exact mid-review evidence to capture is listed in `MID_PROJECT_REVIEW.md`.

## Week 2 outcome

The project now has a documented raw-to-analytics path and first-pass visualizations. It is ready for the mid-project review, provided the connected-environment evidence is collected. Its deliberate next scope is the Week 3 spoilage-arbitrage model.
