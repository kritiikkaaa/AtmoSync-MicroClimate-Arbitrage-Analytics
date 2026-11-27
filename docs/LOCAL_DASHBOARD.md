# Local Dashboard — What to Show in the Mid-Project Review

## Start it

From the project folder, run:

```bash
make dashboard
```

Then open **http://localhost:8000** in Chrome/Safari. Keep the terminal open while presenting; `Ctrl+C` stops the dashboard.

No `.env`, Docker, Kafka, Snowflake, or dbt installation is required for this view. It uses the same deterministic Python sensor simulator that powers the Kafka producer, so the interface is always ready to show.

## What appears in the interface

| Screen element | What to say in review |
| --- | --- |
| Telemetry readings and active containers | “The Python IoT simulator generates schema-controlled temperature, humidity, and vibration messages for three mock shipments.” |
| Temperature trend | “This is the Week 2 baseline chart. The dotted 7°C line is the monitoring threshold.” |
| Container A alert | “Container A is given a controlled temperature/humidity drift to test whether abnormal cold-chain conditions become visible.” |
| Route-health table | “The cleaned dataset groups container readings by route, commodity, destination, and status.” |
| Raw telemetry table | “These are the fields that are sent as Kafka JSON and stored in Snowflake’s raw `VARIANT` payload in the connected pipeline.” |
| Data-flow cards | “Week 1 builds simulator/Kafka/raw storage; Week 2 cleans/joins data and visualizes it. Spoilage arbitrage comes in Week 3.” |

## Honest scope statement

The page has a visible **Local simulated demo** label. It is a presentation interface for the completed Week 1–2 code and is not presented as a live Superset/Snowflake connection. The actual Kafka, Snowflake, dbt, and Superset implementation files remain in the repository and the connected review steps are in `MID_PROJECT_REVIEW.md`.

## Suggested two-minute demo

1. Open the local dashboard and point out the total readings and three containers.
2. Explain the Temperature Trend chart and the 7°C threshold.
3. Open/point to the Container A alert and explain that it is an intentionally simulated drift.
4. Show the Route Health table and Raw Telemetry Events table.
5. Finish: “Week 3 will convert this detection into spoilage-arbitrage and reroute recommendations; Week 4 will automate scheduled dbt runs and alerts.”

