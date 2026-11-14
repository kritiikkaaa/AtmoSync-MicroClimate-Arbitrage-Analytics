import csv
import html
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = (
    PROJECT_ROOT / "data" / "processed" / "reroute_recommendations.csv"
)
OUTPUT_FILE = (
    PROJECT_ROOT / "reports" / "charts" / "arbitrage_dashboard.html"
)

with INPUT_FILE.open("r", newline="", encoding="utf-8") as file:
    recommendations = list(csv.DictReader(file))

if not recommendations:
    raise SystemExit("No recommendation rows found.")

total_uplift = sum(
    float(row["net_reroute_uplift"]) for row in recommendations
)
high_risk_count = sum(
    float(row["temperature_risk_pct"]) >= 50
    for row in recommendations
)
max_uplift = max(
    float(row["net_reroute_uplift"]) for row in recommendations
)

table_rows = []

for row in recommendations:
    uplift = float(row["net_reroute_uplift"])
    risk = float(row["temperature_risk_pct"])
    bar_width = max(0, uplift / max(max_uplift, 1) * 100)

    table_rows.append(
        "<tr>"
        f"<td>{html.escape(row['container_id'])}</td>"
        f"<td>{html.escape(row['commodity'])}</td>"
        f"<td>{html.escape(row['alternate_market'])}</td>"
        f"<td>{risk:.2f}%</td>"
        f"<td>₹{uplift:,.0f}"
        f'<div class="bar"><span style="width:{bar_width:.1f}%"></span></div>'
        "</td>"
        f"<td>{html.escape(row['recommendation'])}</td>"
        "</tr>"
    )

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AtmoSync Arbitrage Dashboard</title>
<style>
body {{ margin:0; padding:32px; background:#101827; color:#eef4f8;
       font:16px Arial,sans-serif; }}
main {{ max-width:1050px; margin:auto; }}
h1 {{ color:#54d6b1; }}
.note {{ color:#b2c0cf; }}
.cards {{ display:flex; gap:16px; margin:24px 0; flex-wrap:wrap; }}
.card {{ background:#1b293a; padding:18px 22px; border-radius:12px;
         min-width:210px; }}
.card span {{ display:block; color:#b2c0cf; font-size:14px; }}
.card strong {{ display:block; margin-top:8px; font-size:24px; }}
table {{ width:100%; border-collapse:collapse; background:#1b293a; }}
th,td {{ padding:14px; border-bottom:1px solid #344458; text-align:left; }}
th {{ color:#54d6b1; }}
.bar {{ height:7px; background:#344458; margin-top:7px; border-radius:5px; }}
.bar span {{ display:block; height:100%; background:#54d6b1; border-radius:5px; }}
</style>
</head>
<body>
<main>
<h1>AtmoSync · Reroute Opportunities</h1>
<p class="note">Synthetic demonstration data and demo risk thresholds.</p>
<div class="cards">
  <div class="card"><span>Containers</span><strong>{len(recommendations)}</strong></div>
  <div class="card"><span>High demo-risk containers</span><strong>{high_risk_count}</strong></div>
  <div class="card"><span>Total estimated uplift</span><strong>₹{total_uplift:,.0f}</strong></div>
</div>
<table>
<thead><tr>
<th>Container</th><th>Commodity</th><th>Alternate market</th>
<th>Temp risk</th><th>Net uplift</th><th>Recommendation</th>
</tr></thead>
<tbody>{''.join(table_rows)}</tbody>
</table>
</main>
</body>
</html>
"""

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE.write_text(page, encoding="utf-8")
print(f"Dashboard saved: {OUTPUT_FILE}")