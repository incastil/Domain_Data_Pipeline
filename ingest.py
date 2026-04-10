"""
ingest.py - Ingestion layer

Fetches raw cart/order data from the DummyJSON public API and persists it
as a JSON file so the original source data is preserved before any
transformation takes place.
"""

import json
import logging
import sys

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

API_URL = "https://dummyjson.com/carts"
RAW_OUTPUT = "raw_orders.json"


def fetch_orders(url: str = API_URL) -> dict:
    logger.info("Fetching data from %s", url)
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    logger.info("Received %d carts from API", len(data.get("carts", [])))
    return data


def save_raw(data: dict, path: str = RAW_OUTPUT) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    logger.info("Raw data saved to %s", path)


def run() -> None:
    data = fetch_orders()
    save_raw(data)


if __name__ == "__main__":
    try:
        run()
    except requests.RequestException as exc:
        logger.error("Network error during ingestion: %s", exc)
        sys.exit(1)
