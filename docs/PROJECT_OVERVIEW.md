# AtmoSync: Micro-Climate Arbitrage Analytics

**Internship role:** Data Associate L1 Intern (Data Analytics)  
**Organisation:** Infotact Solutions  
**Assigned project:** AtmoSync: Micro-Climate Arbitrage Analytics  
**Project window stated in the assignment letter:** 10 November 2026–10 December 2026

## What the project is

AtmoSync is a data-engineering and analytics system for perishable commodity shipments. Conventional supply-chain reporting works from scheduled transit times and broad weather forecasts. It can miss a dangerous local condition inside one refrigerated container, such as a sudden humidity or temperature increase. That gap matters because avocados, mangoes, and similar products can lose quality before a trader sees the problem.

The intended operational story is a commodities trader monitoring a container. When its internal temperature drifts and spoilage risk rises, the system should eventually calculate whether rerouting to a nearer market protects more value than continuing to the original destination.

## Why it is needed

| Need | AtmoSync response |
| --- | --- |
| Perishable quality can change between checkpoints. | Frequent container telemetry captures temperature, humidity, and vibration as events. |
| Raw sensor messages are semi-structured and high-volume. | Kafka separates event production from consumption; Snowflake keeps an immutable JSON landing layer. |
| Analysts need trustworthy, reusable fields instead of JSON fragments. | dbt types, validates, deduplicates, and enriches telemetry with price reference data. |
| Operations users need to notice abnormal conditions quickly. | Superset baseline time-series, route, and raw-data views make the stream visible. |
| Rerouting requires a financial decision, not only a sensor alert. | The later Week 3 arbitrage model will compare degradation and market/distance trade-offs. |

## Required technology modules

The project brief calls for Apache Kafka for streaming ingestion, Snowflake for raw streams and commodity-price history, dbt for SQL ELT models, and Apache Superset for live business intelligence. This repository implements the first two weeks of that plan:

| Delivery period | Included work |
| --- | --- |
| Week 1 | Python sensor simulator; Kafka topic/producer; Snowflake `RAW_IOT_TELEMETRY` design and loader; Superset local deployment foundations and role guidance. |
| Week 2 | Mock commodity-price seed; dbt source and staging models; validation tests; telemetry-to-price join; baseline Superset datasets/charts for routes and temperature. |
| Week 3 — not implemented | Spoilage degradation curve, time-to-spoilage, distance-to-market, arbitrage metric, and reroute recommendation UI. |
| Week 4 — not implemented | Scheduled dbt orchestration, Snowflake optimization, and Slack/email alerts. |

## Data contract

Every simulated Kafka message has the following important fields:

```json
{
  "schema_version": "1.0",
  "event_id": "atm-00000030-…",
  "event_ts": "2026-11-27T09:07:30Z",
  "container_id": "CONT-A-AVO-001",
  "route_id": "MUM-BLR-01",
  "commodity": "avocado",
  "destination_market": "Bengaluru",
  "telemetry": {
    "temperature_c": 8.1,
    "humidity_pct": 90.3,
    "vibration_g": 0.22
  }
}
```

Container A has a controlled simulated temperature/humidity drift. It is intentional test data for proving that the baseline dashboard can visibly distinguish abnormal readings; it is not yet a spoilage or trading recommendation.

## Deliverables required by the assignment

The assignment letter requires source code where applicable, project documentation/report, a presentation, model evaluation results where applicable, and a final demonstration where applicable. This Week 1–2 repository supplies the source, documentation, test evidence structure, and review material. A final presentation/demonstration can be prepared after the Week 3–4 features and a connected Snowflake/Superset environment are complete.
