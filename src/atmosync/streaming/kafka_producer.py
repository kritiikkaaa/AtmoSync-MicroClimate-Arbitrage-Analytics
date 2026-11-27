"""Publish simulated AtmoSync readings to a Kafka topic.

Use --dry-run to validate payload production without Kafka. Kafka imports are
kept inside the adapter functions so the simulator remains easy to test offline.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections.abc import Iterable

from atmosync.simulation.sensor_simulator import TelemetrySimulator

DEFAULT_TOPIC = "atmosync.telemetry.v1"
DEFAULT_BOOTSTRAP = "localhost:29092"


def _load_kafka():
    try:
        from kafka import KafkaProducer  # type: ignore[import-not-found]
        from kafka.admin import KafkaAdminClient, NewTopic  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError(
            "Kafka support is not installed. Activate the project virtual environment and run "
            "pip install -r requirements.txt. For an offline check, pass --dry-run."
        ) from exc
    return KafkaProducer, KafkaAdminClient, NewTopic


def create_topic(bootstrap_servers: str, topic: str) -> None:
    _, KafkaAdminClient, NewTopic = _load_kafka()
    admin = KafkaAdminClient(bootstrap_servers=bootstrap_servers, client_id="atmosync-topic-setup")
    try:
        existing = set(admin.list_topics())
        if topic not in existing:
            admin.create_topics([NewTopic(name=topic, num_partitions=3, replication_factor=1)])
            print(f"Created topic {topic}", file=sys.stderr)
        else:
            print(f"Topic {topic} already exists", file=sys.stderr)
    finally:
        admin.close()


def publish(
    events: Iterable[dict[str, object]], bootstrap_servers: str, topic: str, dry_run: bool
) -> int:
    if dry_run:
        sent = 0
        for event in events:
            print(json.dumps(event, separators=(",", ":"), sort_keys=True))
            sent += 1
        return sent

    KafkaProducer, _, _ = _load_kafka()
    producer = KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda value: json.dumps(value, separators=(",", ":")).encode("utf-8"),
        key_serializer=lambda value: value.encode("utf-8"),
        acks="all",
        retries=3,
    )
    sent = 0
    try:
        for event in events:
            producer.send(topic, key=str(event["container_id"]), value=event)
            sent += 1
        producer.flush(timeout=30)
        return sent
    finally:
        producer.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Send mock AtmoSync readings to Kafka.")
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--interval-seconds", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--dry-run", action="store_true", help="Print newline-delimited JSON instead of Kafka publishing.")
    parser.add_argument("--create-topic", action="store_true", help="Create the telemetry topic before publishing.")
    parser.add_argument("--topic", default=os.getenv("KAFKA_TELEMETRY_TOPIC", DEFAULT_TOPIC))
    parser.add_argument("--bootstrap-servers", default=os.getenv("KAFKA_BOOTSTRAP_SERVERS", DEFAULT_BOOTSTRAP))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.count < 0 or args.interval_seconds < 0:
        raise SystemExit("--count and --interval-seconds must be zero or greater")
    if args.create_topic:
        create_topic(args.bootstrap_servers, args.topic)

    simulator = TelemetrySimulator(seed=args.seed)

    def paced_events():
        for event in simulator.events(args.count):
            yield event
            if args.interval_seconds:
                time.sleep(args.interval_seconds)

    sent = publish(paced_events(), args.bootstrap_servers, args.topic, args.dry_run)
    print(f"Published {sent} event(s) to {args.topic}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
