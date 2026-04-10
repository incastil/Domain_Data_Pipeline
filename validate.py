"""
validate.py - Data quality layer

Runs a suite of checks on the transformed dataset to catch data integrity
issues before the data is loaded into the storage layer.

Checks performed:
  - No null order IDs
  - All quantities are positive integers
  - All prices are non-negative
  - No duplicate (order_id, product_id) combinations
  - Total matches quantity * price within floating-point tolerance
"""

import logging
import sys

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

CLEAN_INPUT = "clean_orders.csv"


def run_checks(df: pd.DataFrame) -> bool:
    failures = []

    if df["order_id"].isnull().any():
        failures.append("Null values found in 'order_id'")

    if not (df["quantity"] > 0).all():
        bad = df[df["quantity"] <= 0]
        failures.append(f"Non-positive quantity in {len(bad)} row(s)")

    if not (df["price"] >= 0).all():
        bad = df[df["price"] < 0]
        failures.append(f"Negative price in {len(bad)} row(s)")

    duplicates = df.duplicated(subset=["order_id", "product_id"])
    if duplicates.any():
        failures.append(f"{duplicates.sum()} duplicate (order_id, product_id) pair(s)")

    expected_total = (df["quantity"] * df["price"]).round(2)
    mismatch = ~((df["total"].round(2) - expected_total).abs() < 0.02)
    if mismatch.any():
        failures.append(f"Total/price mismatch in {mismatch.sum()} row(s)")

    if failures:
        for msg in failures:
            logger.error("VALIDATION FAILED: %s", msg)
        return False

    logger.info("All data quality checks passed (%d rows)", len(df))
    return True


def run() -> None:
    logger.info("Loading data from %s", CLEAN_INPUT)
    df = pd.read_csv(CLEAN_INPUT)
    passed = run_checks(df)
    if not passed:
        sys.exit(1)


if __name__ == "__main__":
    run()
