"""
transform.py - Transformation layer

Reads the raw JSON produced by ingest.py, flattens the nested cart/product
structure, and writes a clean, tabular CSV ready for validation and loading.

Domain entities modeled:
  - order_id   : unique cart identifier
  - user_id    : customer identifier
  - product_id : product identifier
  - quantity   : units ordered
  - price      : unit price
  - total      : line-item total (quantity * price)
"""

import json
import logging
from typing import Any

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

RAW_INPUT = "raw_orders.json"
CLEAN_OUTPUT = "clean_orders.csv"


def flatten_carts(data: dict[str, Any]) -> list[dict]:
    rows = []
    for cart in data.get("carts", []):
        for product in cart.get("products", []):
            rows.append(
                {
                    "order_id": cart["id"],
                    "user_id": cart["userId"],
                    "product_id": product["id"],
                    "product_name": product.get("title", ""),
                    "quantity": product["quantity"],
                    "price": product["price"],
                    "total": product["total"],
                }
            )
    return rows


def run() -> pd.DataFrame:
    logger.info("Reading raw data from %s", RAW_INPUT)
    with open(RAW_INPUT) as f:
        data = json.load(f)

    rows = flatten_carts(data)
    df = pd.DataFrame(rows)

    logger.info("Transformed %d order-line records", len(df))
    df.to_csv(CLEAN_OUTPUT, index=False)
    logger.info("Clean data written to %s", CLEAN_OUTPUT)
    return df


if __name__ == "__main__":
    run()
