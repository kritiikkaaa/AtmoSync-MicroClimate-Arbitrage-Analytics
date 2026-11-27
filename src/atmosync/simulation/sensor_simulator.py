"""Generate realistic, schema-controlled container telemetry for AtmoSync.

The simulator has no cloud or Kafka dependency. It can be used as a standalone
newline-delimited JSON generator or as the source for the Kafka producer.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterator


@dataclass(frozen=True)
class ContainerProfile:
    """The planned operating envelope for one mock shipment."""

    container_id: str
    route_id: str
    commodity: str
    origin: str
    destination_market: str
    latitude: float
    longitude: float
    base_temperature_c: float
    base_humidity_pct: float
    base_vibration_g: float


CONTAINER_PROFILES: tuple[ContainerProfile, ...] = (
    ContainerProfile(
        "CONT-A-AVO-001",
        "MUM-BLR-01",
        "avocado",
        "Mumbai Port",
        "Bengaluru",
        18.5204,
        73.8567,
        4.3,
        82.0,
        0.18,
    ),
    ContainerProfile(
        "CONT-B-AVO-002",
        "CHE-HYD-02",
        "avocado",
        "Chennai Port",
        "Hyderabad",
        13.0827,
        80.2707,
        4.8,
        79.0,
        0.14,
    ),
    ContainerProfile(
        "CONT-C-MNG-003",
        "KOC-PUN-03",
        "mango",
        "Kochi Port",
        "Pune",
        9.9312,
        76.2673,
        11.0,
        73.0,
        0.21,
    ),
)


class TelemetrySimulator:
    """Produce deterministic events and inject a recoverable cold-chain drift.

    Container A becomes warmer for the last third of each 45-message cycle.
    This creates a visible temperature excursion for the Week 2 baseline chart
    without pretending that the Week 3 spoilage calculation already exists.
    """

    def __init__(self, seed: int = 42, start_time: datetime | None = None) -> None:
        self._random = random.Random(seed)
        self._start_time = start_time or datetime.now(timezone.utc)
        if self._start_time.tzinfo is None:
            raise ValueError("start_time must include a timezone")
        self._sequence = 0

    def next_event(self) -> dict[str, object]:
        profile = CONTAINER_PROFILES[self._sequence % len(CONTAINER_PROFILES)]
        event_time = self._start_time + timedelta(seconds=self._sequence * 15)
        cycle_position = self._sequence % 45
        temperature_drift = (
            3.8 if profile.container_id == "CONT-A-AVO-001" and cycle_position >= 30 else 0.0
        )
        humidity_drift = (
            8.5 if profile.container_id == "CONT-A-AVO-001" and cycle_position >= 30 else 0.0
        )
        event = {
            "schema_version": "1.0",
            "event_id": f"atm-{self._sequence:08d}-{self._random.getrandbits(32):08x}",
            "event_ts": event_time.isoformat().replace("+00:00", "Z"),
            "container_id": profile.container_id,
            "route_id": profile.route_id,
            "commodity": profile.commodity,
            "origin": profile.origin,
            "destination_market": profile.destination_market,
            "latitude": round(profile.latitude + self._random.uniform(-0.03, 0.03), 6),
            "longitude": round(profile.longitude + self._random.uniform(-0.03, 0.03), 6),
            "telemetry": {
                "temperature_c": round(
                    profile.base_temperature_c + temperature_drift + self._random.uniform(-0.45, 0.45),
                    2,
                ),
                "humidity_pct": round(
                    profile.base_humidity_pct + humidity_drift + self._random.uniform(-3.0, 3.0),
                    2,
                ),
                "vibration_g": round(
                    max(0.01, profile.base_vibration_g + self._random.uniform(-0.07, 0.12)), 3
                ),
            },
        }
        self._sequence += 1
        return event

    def events(self, count: int) -> Iterator[dict[str, object]]:
        if count < 0:
            raise ValueError("count must be zero or greater")
        for _ in range(count):
            yield self.next_event()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate mock AtmoSync container telemetry.")
    parser.add_argument("--count", type=int, default=10, help="Number of events to emit.")
    parser.add_argument(
        "--interval-seconds",
        type=float,
        default=1.0,
        help="Delay between events; use 0 for a burst.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for repeatable output.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.interval_seconds < 0:
        raise SystemExit("--interval-seconds must be zero or greater")
    simulator = TelemetrySimulator(seed=args.seed)
    for event in simulator.events(args.count):
        print(json.dumps(event, separators=(",", ":"), sort_keys=True))
        if args.interval_seconds:
            time.sleep(args.interval_seconds)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
