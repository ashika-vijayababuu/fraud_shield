from __future__ import annotations

import json
import os
import random
import time

from kafka import KafkaProducer


TOPIC = os.getenv("KAFKA_TOPIC", "transactions")
BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


def build_transaction() -> dict[str, int | float | bool]:
    return {
        "transaction_amount": round(random.uniform(10, 2500), 2),
        "customer_age": random.randint(18, 75),
        "merchant_risk_score": round(random.uniform(0, 1), 3),
        "transaction_velocity_1h": random.randint(0, 20),
        "card_present": random.choice([True, False]),
        "international": random.choice([True, False]),
    }


def main() -> None:
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=lambda payload: json.dumps(payload).encode("utf-8"),
    )

    while True:
        event = build_transaction()
        producer.send(TOPIC, event)
        print(f"Sent: {event}")
        time.sleep(1)


if __name__ == "__main__":
    main()
