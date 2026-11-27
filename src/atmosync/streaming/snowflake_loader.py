"""Consume Kafka telemetry and persist immutable raw payloads in Snowflake.

The loader commits Kafka offsets only after its current batch has been inserted.
It is intentionally a simple Week 1 reference implementation; durable retry
orchestration belongs to the Week 4 scope.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Any

DEFAULT_TOPIC = "atmosync.telemetry.v1"
RAW_INSERT = """
INSERT INTO RAW_IOT_TELEMETRY
    (EVENT_ID, EVENT_TS, CONTAINER_ID, KAFKA_TOPIC, KAFKA_PARTITION, KAFKA_OFFSET, PAYLOAD)
SELECT %s, %s, %s, %s, %s, %s, PARSE_JSON(%s)
"""


@dataclass(frozen=True)
class LoaderConfig:
    bootstrap_servers: str
    topic: str
    group_id: str
    batch_size: int
    account: str
    user: str
    password: str
    role: str
    warehouse: str
    database: str
    schema: str

    @classmethod
    def from_environment(cls, args: argparse.Namespace) -> "LoaderConfig":
        required = ("SNOWFLAKE_ACCOUNT", "SNOWFLAKE_USER", "SNOWFLAKE_PASSWORD")
        missing = [name for name in required if not os.getenv(name)]
        if missing:
            raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
        return cls(
            bootstrap_servers=args.bootstrap_servers,
            topic=args.topic,
            group_id=args.group_id,
            batch_size=args.batch_size,
            account=os.environ["SNOWFLAKE_ACCOUNT"],
            user=os.environ["SNOWFLAKE_USER"],
            password=os.environ["SNOWFLAKE_PASSWORD"],
            role=os.getenv("SNOWFLAKE_INGEST_ROLE", "ATMOSYNC_INGESTOR"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "ATMOSYNC_WH"),
            database=os.getenv("SNOWFLAKE_DATABASE", "ATMOSYNC"),
            schema=os.getenv("SNOWFLAKE_RAW_SCHEMA", "RAW"),
        )


def _load_clients():
    try:
        from kafka import KafkaConsumer  # type: ignore[import-not-found]
        import snowflake.connector  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError("Install requirements.txt before running the Snowflake loader.") from exc
    return KafkaConsumer, snowflake.connector


def _row_from_message(message: Any) -> tuple[object, ...]:
    payload = message.value
    if not isinstance(payload, dict):
        raise ValueError("Kafka value must decode to a JSON object")
    for field in ("event_id", "event_ts", "container_id"):
        if not payload.get(field):
            raise ValueError(f"Telemetry payload is missing {field}")
    return (
        payload["event_id"],
        payload["event_ts"],
        payload["container_id"],
        message.topic,
        message.partition,
        message.offset,
        json.dumps(payload, separators=(",", ":")),
    )


def load(config: LoaderConfig, max_messages: int | None = None) -> int:
    KafkaConsumer, snowflake = _load_clients()
    consumer = KafkaConsumer(
        config.topic,
        bootstrap_servers=config.bootstrap_servers,
        group_id=config.group_id,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        value_deserializer=lambda raw: json.loads(raw.decode("utf-8")),
    )
    connection = snowflake.connect(
        account=config.account,
        user=config.user,
        password=config.password,
        role=config.role,
        warehouse=config.warehouse,
        database=config.database,
        schema=config.schema,
    )
    loaded = 0
    batch: list[tuple[object, ...]] = []
    try:
        for message in consumer:
            batch.append(_row_from_message(message))
            if max_messages is not None and loaded + len(batch) >= max_messages:
                batch = batch[: max_messages - loaded]
            if len(batch) >= config.batch_size or (max_messages is not None and loaded + len(batch) >= max_messages):
                with connection.cursor() as cursor:
                    cursor.executemany(RAW_INSERT, batch)
                connection.commit()
                consumer.commit()
                loaded += len(batch)
                print(f"Loaded {loaded} message(s)", file=sys.stderr)
                batch = []
            if max_messages is not None and loaded >= max_messages:
                break
        return loaded
    finally:
        if batch:
            with connection.cursor() as cursor:
                cursor.executemany(RAW_INSERT, batch)
            connection.commit()
            consumer.commit()
            loaded += len(batch)
        connection.close()
        consumer.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Load AtmoSync Kafka telemetry into Snowflake raw storage.")
    parser.add_argument("--bootstrap-servers", default=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092"))
    parser.add_argument("--topic", default=os.getenv("KAFKA_TELEMETRY_TOPIC", DEFAULT_TOPIC))
    parser.add_argument("--group-id", default="atmosync-snowflake-loader-v1")
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--max-messages", type=int, help="Stop after this number of records.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.batch_size <= 0 or (args.max_messages is not None and args.max_messages <= 0):
        raise SystemExit("--batch-size and --max-messages must be positive")
    config = LoaderConfig.from_environment(args)
    loaded = load(config, args.max_messages)
    print(f"Loader finished after {loaded} message(s)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
