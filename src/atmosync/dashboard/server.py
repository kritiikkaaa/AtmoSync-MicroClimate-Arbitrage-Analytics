"""Serve the self-contained AtmoSync mid-review dashboard on localhost.

This browser view uses the project's deterministic simulator so it is useful in
a classroom/demo setting without Kafka, Snowflake, or Superset credentials. It
does not replace the documented Superset integration; it is an honest local
presentation layer for the implemented Week 1–2 data contract.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from atmosync.simulation.sensor_simulator import CONTAINER_PROFILES, TelemetrySimulator

WEB_DIRECTORY = Path(__file__).with_name("web")
DEFAULT_EVENT_COUNT = 135


def _temperature_status(temperature_c: float) -> str:
    if temperature_c > 7:
        return "At risk"
    if temperature_c < 2:
        return "Cold alert"
    return "Stable"


def create_dashboard_snapshot(event_count: int = DEFAULT_EVENT_COUNT) -> dict[str, object]:
    """Create browser-ready Week 1–2 telemetry, health, and raw-event data."""

    if event_count < len(CONTAINER_PROFILES):
        raise ValueError("event_count must include at least one reading per container")

    start_time = datetime.now(timezone.utc) - timedelta(seconds=(event_count - 1) * 15)
    events = list(TelemetrySimulator(seed=42, start_time=start_time).events(event_count))
    readings_by_container: dict[str, list[dict[str, object]]] = defaultdict(list)
    latest_by_container: dict[str, dict[str, object]] = {}
    raw_rows: list[dict[str, object]] = []

    for event in events:
        telemetry = event["telemetry"]
        assert isinstance(telemetry, dict)
        temperature_c = float(telemetry["temperature_c"])
        reading = {
            "event_id": event["event_id"],
            "event_ts": event["event_ts"],
            "temperature_c": temperature_c,
            "humidity_pct": float(telemetry["humidity_pct"]),
            "vibration_g": float(telemetry["vibration_g"]),
            "status": _temperature_status(temperature_c),
        }
        container_id = str(event["container_id"])
        readings_by_container[container_id].append(reading)
        latest_by_container[container_id] = {**event, **reading}
        raw_rows.append(
            {
                "event_id": event["event_id"],
                "event_ts": event["event_ts"],
                "container_id": event["container_id"],
                "route_id": event["route_id"],
                "commodity": event["commodity"],
                "destination_market": event["destination_market"],
                "temperature_c": temperature_c,
                "humidity_pct": float(telemetry["humidity_pct"]),
                "vibration_g": float(telemetry["vibration_g"]),
                "status": _temperature_status(temperature_c),
            }
        )

    containers = []
    for profile in CONTAINER_PROFILES:
        latest = latest_by_container[profile.container_id]
        telemetry = latest["telemetry"]
        assert isinstance(telemetry, dict)
        containers.append(
            {
                "container_id": profile.container_id,
                "route_id": profile.route_id,
                "commodity": profile.commodity,
                "origin": profile.origin,
                "destination_market": profile.destination_market,
                "temperature_c": latest["temperature_c"],
                "humidity_pct": latest["humidity_pct"],
                "vibration_g": latest["vibration_g"],
                "status": latest["status"],
                "last_seen": latest["event_ts"],
            }
        )

    at_risk_events = [row for row in raw_rows if row["status"] == "At risk"]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "mode": "Local review demo — simulated Week 1–2 telemetry",
        "total_readings": len(events),
        "container_count": len(CONTAINER_PROFILES),
        "at_risk_events": len(at_risk_events),
        "at_risk_containers": sum(1 for row in containers if row["status"] == "At risk"),
        "containers": containers,
        "readings_by_container": dict(readings_by_container),
        "recent_alerts": list(reversed(at_risk_events[-6:])),
        "raw_rows": list(reversed(raw_rows[-12:])),
    }


class AtmoSyncDashboardHandler(SimpleHTTPRequestHandler):
    """Serve dashboard assets and a fresh synthetic telemetry snapshot endpoint."""

    def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
        super().__init__(*args, directory=str(WEB_DIRECTORY), **kwargs)

    def do_GET(self) -> None:  # noqa: N802
        request_path = urlparse(self.path).path
        if request_path == "/api/dashboard":
            payload = json.dumps(create_dashboard_snapshot(), separators=(",", ":")).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if request_path == "/":
            self.path = "/index.html"
        else:
            self.path = request_path
        super().do_GET()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the AtmoSync Week 1–2 local review dashboard.")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind (default: 127.0.0.1).")
    parser.add_argument("--port", type=int, default=8000, help="Local port to use (default: 8000).")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not 1 <= args.port <= 65535:
        raise SystemExit("--port must be between 1 and 65535")
    server = ThreadingHTTPServer((args.host, args.port), AtmoSyncDashboardHandler)
    print(f"AtmoSync dashboard is running at http://{args.host}:{args.port}")
    print("Press Ctrl+C in this terminal to stop the dashboard.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nAtmoSync dashboard stopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

