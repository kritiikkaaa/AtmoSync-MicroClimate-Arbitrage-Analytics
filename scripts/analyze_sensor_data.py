from pathlib import Path
import csv
import html
import re
from collections import defaultdict


# Yeh script scripts folder mein hai; uska parent project folder hai.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FOLDER = PROJECT_ROOT / "data"
CHART_FOLDER = PROJECT_ROOT / "reports" / "charts"


def clean_name(name):
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def find_column(columns, possible_names):
    for name in possible_names:
        if name in columns:
            return columns[name]
    return None


temperature_names = {"temperature", "temperaturec", "temperaturecelsius", "tempc", "temp", "airtemperature"}
humidity_names = {"humidity", "humiditypct", "humiditypercent", "relativehumidity", "rh", "rhpercent"}
location_names = {"location", "locationid", "site", "station", "sensorid", "deviceid"}

csv_files = list(DATA_FOLDER.rglob("*.csv"))
csv_files.sort(
    key=lambda path: (
        "validated" not in path.name.lower(),
        "processed" not in str(path).lower(),
        str(path).lower(),
    )
)

records = []
source_file = None
temperature_column = None
humidity_column = None
location_column = None

for csv_file in csv_files:
    try:
        with csv_file.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            columns = {
                clean_name(name): name
                for name in (reader.fieldnames or [])
            }

            temp_col = find_column(columns, temperature_names)
            humidity_col = find_column(columns, humidity_names)

            if not temp_col or not humidity_col:
                continue

            location_col = find_column(columns, location_names)
            found_records = []

            for row in reader:
                try:
                    temperature = float(row[temp_col])
                    humidity = float(row[humidity_col])
                except (TypeError, ValueError):
                    continue

                location = row.get(location_col, "All sensors") if location_col else "All sensors"
                found_records.append({
                    "temperature": temperature,
                    "humidity": humidity,
                    "location": location or "Unknown",
                })

            if found_records:
                records = found_records
                source_file = csv_file
                temperature_column = temp_col
                humidity_column = humidity_col
                break
    except (OSError, csv.Error, UnicodeError):
        continue

if not records:
    raise SystemExit(
        "Data folder mein temperature aur humidity wala CSV nahi mila."
    )

CHART_FOLDER.mkdir(parents=True, exist_ok=True)


def save_line_chart(filename, title, values, y_label, color):
    width, height = 900, 500
    left, right, top, bottom = 80, 30, 65, 70
    plot_width = width - left - right
    plot_height = height - top - bottom

    low = min(values)
    high = max(values)
    if low == high:
        low -= 1
        high += 1

    points = []
    for index, value in enumerate(values):
        x = left + index * plot_width / max(len(values) - 1, 1)
        y = top + (high - value) * plot_height / (high - low)
        points.append(f"{x:.1f},{y:.1f}")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="white"/>
<text x="{width / 2}" y="35" text-anchor="middle" font-size="24" font-family="Arial">{html.escape(title)}</text>
<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="#555"/>
<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="#555"/>
<text x="20" y="{height / 2}" transform="rotate(-90 20 {height / 2})" text-anchor="middle" font-size="16" font-family="Arial">{html.escape(y_label)}</text>
<text x="{left}" y="{height-bottom+28}" font-size="13" font-family="Arial">First reading</text>
<text x="{width-right}" y="{height-bottom+28}" text-anchor="end" font-size="13" font-family="Arial">Last reading</text>
<text x="{left-10}" y="{top+5}" text-anchor="end" font-size="13" font-family="Arial">{high:.1f}</text>
<text x="{left-10}" y="{height-bottom}" text-anchor="end" font-size="13" font-family="Arial">{low:.1f}</text>
<polyline points="{' '.join(points)}" fill="none" stroke="{color}" stroke-width="3"/>
</svg>"""

    (CHART_FOLDER / filename).write_text(svg, encoding="utf-8")


temperatures = [record["temperature"] for record in records]
humidities = [record["humidity"] for record in records]

save_line_chart(
    "temperature.svg", "Temperature Readings",
    temperatures, temperature_column, "#e45757"
)
save_line_chart(
    "humidity.svg", "Humidity Readings",
    humidities, humidity_column, "#3977c3"
)

location_values = defaultdict(list)
for record in records:
    location_values[record["location"]].append(record["temperature"])

averages = {
    location: sum(values) / len(values)
    for location, values in location_values.items()
}
low = min(averages.values())
high = max(averages.values())
if low == high:
    low -= 1
    high += 1

width, height = 900, 500
left, right, top, bottom = 80, 30, 65, 100
plot_height = height - top - bottom
bar_width = min(70, 600 / max(len(averages), 1))
gap = 25
bars = []

for index, (location, value) in enumerate(sorted(averages.items())):
    x = left + index * (bar_width + gap)
    bar_height = (value - low) / (high - low) * plot_height
    y = top + plot_height - bar_height
    label = html.escape(str(location))
    bars.append(
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" '
        f'height="{bar_height:.1f}" fill="#3b9b72"/>'
        f'<text x="{x + bar_width/2:.1f}" y="{height-bottom+22}" '
        f'text-anchor="middle" font-size="12" font-family="Arial">{label}</text>'
        f'<text x="{x + bar_width/2:.1f}" y="{y-7:.1f}" '
        f'text-anchor="middle" font-size="12" font-family="Arial">{value:.1f}</text>'
    )

bar_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="white"/>
<text x="{width / 2}" y="35" text-anchor="middle" font-size="24" font-family="Arial">Average Temperature by Location</text>
<line x1="{left}" y1="{top}" x2="{left}" y2="{height-bottom}" stroke="#555"/>
<line x1="{left}" y1="{height-bottom}" x2="{width-right}" y2="{height-bottom}" stroke="#555"/>
<text x="20" y="{height / 2}" transform="rotate(-90 20 {height / 2})" text-anchor="middle" font-size="16" font-family="Arial">Average {html.escape(temperature_column)}</text>
{''.join(bars)}
</svg>"""

(CHART_FOLDER / "location_temperature.svg").write_text(bar_svg, encoding="utf-8")

print(f"Charts saved in: {CHART_FOLDER}")
print(f"CSV used: {source_file.name}")