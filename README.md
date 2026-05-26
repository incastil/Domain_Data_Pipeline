# Domain Data Pipeline

[![CI](https://github.com/incastil/Domain_Data_Pipeline/actions/workflows/pipeline.yml/badge.svg)](https://github.com/incastil/Domain_Data_Pipeline/actions/workflows/pipeline.yml)
[![Python](https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED?logo=docker&logoColor=white)](https://hub.docker.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Production-style containerized ETL pipeline with validation enforcement, idempotent loading, and structured logging. Ingests REST API data through a 4-stage pipeline — ingest, transform, validate, load — with fail-fast data quality gates before any data reaches storage.

---

## Production-Style Features

| Feature | Implementation |
|---|---|
| **Idempotent loading** | SQLite `if_exists="replace"` — safe to re-run anytime |
| **Fail-fast validation** | Pipeline aborts with exit code 1 on any quality failure |
| **Containerized execution** | Full Docker support with volume-mounted output |
| **Structured logging** | Timestamped log output at every pipeline stage |
| **Modular architecture** | Each stage is independently testable and replaceable |
| **Single-command orchestration** | `python main.py` or `docker run` runs the full pipeline |
| **Persistent storage** | SQLite output survives container restarts via volume mount |
| **Reproducible environments** | Pinned base image + requirements for consistent builds |

---

## Architecture

```
API (dummyjson.com/carts)
        │
        ▼
  [ ingest.py ]  →  raw_orders.json   (raw source preserved)
        │
        ▼
[ transform.py ] →  clean_orders.csv  (flattened, structured)
        │
        ▼
[ validate.py  ]                      (fail-fast quality gates)
        │
        ▼
  [ load.py    ]  →  orders.db        (idempotent SQLite load)
```

Orchestrated by `main.py` — each step is a named function registered in a `STEPS` list. Any step failure propagates an exit code and halts the pipeline cleanly.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.10+ | Runtime |
| pandas | Transformation and CSV I/O |
| requests | REST API ingestion |
| SQLite | Persistent storage |
| Docker | Containerized execution |
| GitHub Actions | CI — lint, pipeline smoke test, Docker build |

---

## Project Structure

```
Domain_Data_Pipeline/
├── main.py           # Orchestrator — runs all 4 stages in sequence
├── ingest.py         # Stage 1 — fetches and persists raw API response
├── transform.py      # Stage 2 — flattens nested JSON to tabular CSV
├── validate.py       # Stage 3 — enforces data quality rules (fail-fast)
├── load.py           # Stage 4 — idempotent load into SQLite
├── requirements.txt
├── Dockerfile
└── .github/
    └── workflows/
        └── pipeline.yml   # CI: lint + smoke test + Docker build
```

---

## Validation Rules

`validate.py` collects **all** failures before aborting — not just the first one:

- `order_id` — no null values
- `quantity` — must be a positive integer (> 0)
- `price` — must be non-negative (≥ 0)
- `(order_id, product_id)` — no duplicate pairs
- `total` — must equal `quantity × price` within ±0.02 tolerance (handles floating-point artifacts)

If any check fails, the pipeline exits with code 1 and nothing reaches the database.

---

## Running the Pipeline

### Local

```bash
# Install dependencies
pip install -r requirements.txt

# Run full pipeline
python main.py
```

### Docker (Recommended)

```bash
# Build image
docker build -t domain-data-pipeline .

# Run — output written to /app inside the container (ephemeral)
docker run --rm domain-data-pipeline

# Run with volume mount — the pipeline writes all output files to its
# working directory (/app inside the container), so mounting a host
# directory there causes raw_orders.json, clean_orders.csv, and
# orders.db to be written directly to ./output/ on the host.
mkdir -p output
docker run --rm -v $(pwd)/output:/app domain-data-pipeline
```

After the container exits, `./output/` contains `raw_orders.json`, `clean_orders.csv`, and `orders.db`.

---

## Example Output

```
2024-01-15 10:23:01 INFO     [ingest]    Fetching orders from https://dummyjson.com/carts
2024-01-15 10:23:01 INFO     [ingest]    Saved 30 carts to raw_orders.json
2024-01-15 10:23:01 INFO     [transform] Flattened 30 carts → 123 order lines
2024-01-15 10:23:01 INFO     [transform] Saved clean_orders.csv
2024-01-15 10:23:01 INFO     [validate]  Running 5 data quality checks...
2024-01-15 10:23:01 INFO     [validate]  All checks passed
2024-01-15 10:23:01 INFO     [load]      Loading 123 rows into orders.db
2024-01-15 10:23:01 INFO     [load]      Load complete — 123 rows in table 'orders'
```

**Sample rows from `clean_orders.csv`:**

```
order_id,user_id,product_id,product_name,quantity,price,total
1,97,144,Cricket Helmet,1,49.99,49.99
1,97,98,Dimple Golf Ball,3,7.99,23.97
2,44,26,Handmade Cotton Shirt,2,31.49,62.98
```

---

## Domain Model

| Column | Type | Description |
|---|---|---|
| `order_id` | int | Unique cart/order identifier |
| `user_id` | int | Customer identifier |
| `product_id` | int | Product identifier |
| `product_name` | str | Human-readable product name |
| `quantity` | int | Units ordered |
| `price` | float | Unit price (USD) |
| `total` | float | Line-item total (quantity × price) |

---

## CI / CD

GitHub Actions runs on every push and pull request:

1. **Lint** — `flake8` syntax and style check
2. **Smoke test** — runs `python main.py` end-to-end against live API
3. **Docker build** — verifies container builds successfully

See [`.github/workflows/pipeline.yml`](.github/workflows/pipeline.yml).

---

## Future Improvements

- **PostgreSQL support** — swap SQLite adapter for production-grade storage
- **Prometheus metrics** — expose pipeline run duration and row counts
- **Apache Airflow orchestration** — replace `main.py` with a DAG for scheduling
- **Kubernetes deployment** — containerized pipeline job via CronJob resource
- **Terraform provisioning** — infrastructure-as-code for cloud deployment
- **dbt transformation layer** — SQL-based transforms with lineage tracking
- **Unit test suite** — pytest coverage for `flatten_carts` and `run_checks`
