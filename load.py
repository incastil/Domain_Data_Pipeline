"""
load.py - Storage layer

Reads the validated CSV and loads it into a SQLite database, replacing any
existing data so the pipeline is idempotent (safe to re-run).
"""

import logging
import sqlite3

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

CLEAN_INPUT = "clean_orders.csv"
DB_PATH = "orders.db"
TABLE_NAME = "orders"


def run() -> None:
    logger.info("Loading data from %s into %s", CLEAN_INPUT, DB_PATH)
    df = pd.read_csv(CLEAN_INPUT)

    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
        row_count = conn.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]

    logger.info(
        "Loaded %d rows into table '%s' in %s", row_count, TABLE_NAME, DB_PATH
    )


if __name__ == "__main__":
    run()
