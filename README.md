# AtmoSync: MicroClimate Arbitrage Analytics



\# AtmoSync: MicroClimate Arbitrage Analytics



A local demonstration project for validating container sensor readings, analyzing microclimate differences, estimating temperature risk, and comparing mock market reroute economics.



\## Quick start



Run these commands from the repository folder in PowerShell. The project uses Python's standard library; it does not need `requirements.txt` or package installation.



```powershell

py -3.14 -m venv .venv

```



Then run the pipeline steps:



```powershell

.\\.venv\\Scripts\\python.exe src\\atmosync\\simulation\\sensor\_simulator.py --readings 1000 --seed 7

.\\.venv\\Scripts\\python.exe src\\atmosync\\processing\\data\_validator.py

.\\.venv\\Scripts\\python.exe src\\atmosync\\analytics\\microclimate\_analyzer.py

.\\.venv\\Scripts\\python.exe scripts\\analyze\_sensor\_data.py

.\\.venv\\Scripts\\python.exe scripts\\calculate\_arbitrage.py

.\\.venv\\Scripts\\python.exe scripts\\make\_reroute\_recommendations.py

.\\.venv\\Scripts\\python.exe scripts\\build\_arbitrage\_dashboard.py

```



Open the generated dashboard:



```powershell

start .\\reports\\charts\\arbitrage\_dashboard.html

```



\## Pipeline



1\. \*\*Simulate:\*\* Generate synthetic IoT readings for three containers.

2\. \*\*Validate:\*\* Separate valid sensor rows from rejected rows.

3\. \*\*Analyze:\*\* Calculate per-location averages, temperature-risk scores, and microclimate divergence scores.

4\. \*\*Visualize:\*\* Create SVG charts and an HTML dashboard.

5\. \*\*Compare markets:\*\* Calculate estimated reroute uplift from mock prices and freight costs.

6\. \*\*Recommend:\*\* Combine temperature risk and uplift into a demo recommendation.



\## Metric definitions



\- \*\*Temperature risk score:\*\* For this demo, the score is based on how far a reading exceeds the configured commodity temperature limit. The score is capped at 100 and averaged by location.

\- \*\*Divergence score:\*\* Measures how different each location's average temperature, humidity, and soil moisture are from the network averages. A high divergence score does not necessarily mean high temperature risk.

\- \*\*Net reroute uplift:\*\* `(alternate market price − origin market price) × quantity − extra freight cost`.

\- \*\*Reroute candidate:\*\* The demo labels a container this way when its average temperature-risk score is at least 50 and its estimated reroute uplift is positive.



\## Important assumptions



All sensor readings, market prices, quantities, temperature limits, and recommendation thresholds are synthetic demo values. The risk score is an educational heuristic, not a food-safety assessment. Do not use these results to make real shipment decisions.



This repository currently runs locally from CSV files. A live Kafka stream, Snowflake warehouse, dbt deployment, and Superset service are not configured.



\## Project structure



\- `src/atmosync/simulation/`: sensor data generator

\- `src/atmosync/processing/`: input validation

\- `src/atmosync/analytics/`: location and temperature-risk analysis

\- `scripts/`: chart, market-uplift, recommendation, and dashboard scripts

\- `data/raw/`: synthetic sensor readings and market quotes

\- `data/processed/`: validation and analysis outputs

\- `reports/charts/`: SVG charts and HTML dashboards

