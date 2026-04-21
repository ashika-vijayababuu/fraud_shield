from __future__ import annotations

import os

import requests

from streaming.producer.simulate_transactions import build_transaction


API_URL = os.getenv("FRAUD_API_INGEST_URL", "http://127.0.0.1:8000/api/ingest-transaction")


def main() -> None:
    event = build_transaction()
    response = requests.post(API_URL, json=event, timeout=10)
    response.raise_for_status()
    print(f"Sent live transaction to API: {event}")
    print(f"Scoring result: {response.json()}")


if __name__ == "__main__":
    main()
