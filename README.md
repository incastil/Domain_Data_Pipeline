# Domain Data Pipeline

A modular data pipeline that ingests, transforms, validates, and stores e-commerce order data — demonstrating domain modeling, data quality, and structured data engineering practices.

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
[ validate.py  ]                      (data quality checks)
        │
        ▼
  [ load.py    ]  →  orders.db        (SQLite storage)
```

Run all steps with one command:

```bash
python main.py
```

---

## Project Structure

```
Domain_Data_Pipeline/
├── main.py           # Orchestrator — runs the full pipeline
├── ingest.py         # Ingestion layer
├── transform.py      # Transformation layer
├── validate.py       # Data quality layer
├── load.py           # Storage layer
├── requirements.txt
├── Dockerfile
├── raw_orders.json   # Generated — raw API response
├── clean_orders.csv  # Generated — transformed data
└── orders.db         # Generated — SQLite database
```

---

## Domain Model

| Column        | Type   | Description                     |
|---------------|--------|---------------------------------|
| `order_id`    | int    | Unique cart/order identifier    |
| `user_id`     | int    | Customer identifier             |
| `product_id`  | int    | Product identifier              |
| `product_name`| str    | Human-readable product name     |
| `quantity`    | int    | Units ordered                   |
| `price`       | float  | Unit price (USD)                |
| `total`       | float  | Line-item total (quantity×price)|

---

## Setup & Usage

### Local

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the full pipeline
python main.py
```

### Docker

**Prerequisites:** Docker must be installed and running.

```bash
# 1. Build the image
docker build -t domain-data-pipeline .

# 2. Run (output stays inside the container)
docker run --rm domain-data-pipeline
```

To persist the generated files (`raw_orders.json`, `clean_orders.csv`, `orders.db`) to your local machine, mount a volume:

```bash
# Create output directory
mkdir -p output

# Run with volume mount
docker run --rm -v $(pwd)/output:/app domain-data-pipeline
```

Output files will appear in `./output/` after the container exits.

**Useful Docker commands:**

```bash
# View logs from a named container
docker run --name pipeline domain-data-pipeline
docker logs pipeline

# Remove the image when done
docker rmi domain-data-pipeline
```

---

## Data Quality Checks

`validate.py` enforces the following rules before data reaches storage:

- `order_id` has no null values
- `quantity` is a positive integer
- `price` is non-negative
- No duplicate `(order_id, product_id)` pairs
- `total` matches `quantity × price` within floating-point tolerance

---

## Pipeline Steps

| Step      | Script         | Input              | Output             |
|-----------|----------------|--------------------|--------------------|
| Ingest    | `ingest.py`    | DummyJSON API      | `raw_orders.json`  |
| Transform | `transform.py` | `raw_orders.json`  | `clean_orders.csv` |
| Validate  | `validate.py`  | `clean_orders.csv` | (pass/fail)        |
| Load      | `load.py`      | `clean_orders.csv` | `orders.db`        |
