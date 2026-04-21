from __future__ import annotations

import json
import os
from typing import Any

import requests
from kafka import KafkaConsumer


TOPIC = os.getenv("KAFKA_TOPIC", "transactions")
BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
API_URL = os.getenv("FRAUD_API_INGEST_URL", "http://127.0.0.1:8000/api/ingest-transaction")


def consume_messages() -> None:
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id="fraud-dashboard-consumers",
        value_deserializer=lambda payload: json.loads(payload.decode("utf-8")),
    )

    print(f"Listening to Kafka topic '{TOPIC}' on {BOOTSTRAP_SERVERS}")
    print(f"Forwarding events to {API_URL}")

    for message in consumer:
        event: dict[str, Any] = message.value
        response = requests.post(API_URL, json=event, timeout=10)
        response.raise_for_status()
        print(f"Scored streamed transaction: {response.json()}")


if __name__ == "__main__":
    consume_messages()
