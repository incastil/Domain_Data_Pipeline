"""
main.py - Pipeline orchestrator

Runs the full domain data pipeline in order:
  1. Ingest  - fetch raw data from API
  2. Transform - flatten and clean the data
  3. Validate - run data quality checks
  4. Load    - persist to SQLite

Usage:
  python main.py
"""

import logging
import sys

import ingest
import load
import transform
import validate

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

STEPS = [
    ("Ingest", ingest.run),
    ("Transform", transform.run),
    ("Validate", validate.run),
    ("Load", load.run),
]


def main() -> None:
    logger.info("=== Domain Data Pipeline starting ===")
    for name, step in STEPS:
        logger.info("--- Step: %s ---", name)
        try:
            step()
        except SystemExit as exc:
            logger.error("Pipeline aborted at step '%s' (exit code %s)", name, exc.code)
            sys.exit(exc.code)
        except Exception as exc:
            logger.error("Unexpected error at step '%s': %s", name, exc)
            sys.exit(1)
    logger.info("=== Pipeline completed successfully ===")


if __name__ == "__main__":
    main()
