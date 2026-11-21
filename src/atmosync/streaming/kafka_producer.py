
"""Publish AtmoSync sensor readings to Apache Kafka."""

import argparse
import json

from kafka import KafkaProducer
from kafka.errors import KafkaError

from atmosync.simulation.sensor_simulator import (
    generate_readings,
    save_readings,
)

from pathlib import Path


def create_producer(broker):
    """Create a Kafka producer connection."""

    return KafkaProducer(
        bootstrap_servers=broker,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        key_serializer=lambda key: key.encode("utf-8"),
        acks="all",
        retries=5,
    )


def publish_readings(producer, readings, topic):
    """Publish sensor readings to a Kafka topic."""

    successful = 0

    for reading in readings:
        try:
            future = producer.send(
                topic,
                key=reading["sensor_id"],
                value=reading,
            )
            future.get(timeout=10)
            successful += 1

            print(
                f"Published: {reading['sensor_id']} | "
                f"{reading['commodity']} | "
                f"{reading['temperature_c']}°C"
            )

        except KafkaError as error:
            print(f"Failed to publish reading: {error}")
            raise

    producer.flush()
    return successful


def main():
    parser = argparse.ArgumentParser(
        description="AtmoSync Kafka Sensor Producer"
    )
    parser.add_argument("--readings", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--broker", default="localhost:9092")
    parser.add_argument(
        "--topic",
        default="atmosync-sensor-readings",
    )

    args = parser.parse_args()

    readings = generate_readings(args.readings, args.seed)

    project_root = Path(__file__).resolve().parents[3]
    csv_path = project_root / "data/raw/sensor_readings.csv"
    save_readings(readings, csv_path)

    producer = create_producer(args.broker)

    try:
        successful = publish_readings(
            producer,
            readings,
            args.topic,
        )

        print("\nAtmoSync Kafka Producer Summary")
        print("--------------------------------")
        print(f"Generated readings: {len(readings)}")
        print(f"Published readings: {successful}")
        print(f"CSV saved: {csv_path}")
        print(f"Kafka topic: {args.topic}")

    finally:
        producer.close()


if __name__ == "__main__":
    main()
