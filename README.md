# Data Playground

A local data stack demo with Dagster, dbt, Trino, Iceberg, Apache Polaris, and Postgres.

## Architecture

```
Dagster  ──schedules──>  dbt  ──transforms──>  Trino
                                                 ├── Postgres   (shop.customers)
                                                 └── Iceberg    (events via Polaris -> MinIO)
```

| Service | Role | Port |
|---------|------|------|
| **Dagster** | Pipeline orchestration & scheduling | 3000 |
| **dbt** | SQL transformations & docs | 8081 |
| **Trino** | Federated query engine | 8080 |
| **Apache Polaris** | Iceberg REST catalog | 8181 |
| **MinIO** | S3-compatible object storage (Iceberg data) | 9000 / 9001 |
| **Postgres** | Relational source (shop data) | 5432 |

## Quick Start

**1. Start all services**

```bash
docker compose up -d --build
```

**2. Run the setup script** (initializes Polaris, MinIO, seeds data, compiles dbt)

```bash
./scripts/setup.sh
```

That's it. Once setup completes:

- **Dagster UI** → http://localhost:3000 — go to *Jobs* → `run_dbt_job` → *Materialize All*
- **dbt Docs** → http://localhost:8081
- **MinIO Console** → http://localhost:9001 (user: `admin`, password: `password`)

## Data Flow

```
Postgres                 MinIO (S3)
shop.customers    +    iceberg.public_data.events
       │                        │
       ▼                        ▼
  stg_customers            stg_events
            \               /
             customer_summary   (Iceberg table in Trino)
```

- **Source 1** — `postgres.public.customers` (seeded via `infrastructure/postgres/init_data.sql`)
- **Source 2** — `iceberg.public_data.events` (seeded once by setup.sh via `apps/dbt-analytics/seeds/iceberg/events.csv`)
- **Output** — `iceberg.public.customer_summary` (materialized as an Iceberg table by Dagster on each run)

## Repository Structure

```
apps/
  dbt-analytics/       # dbt project (models, seeds, sources)
  dagster-app/         # Dagster definitions (assets, schedules)
infrastructure/
  trino/               # Trino config + catalog connectors
  postgres/            # Postgres init SQL
  dbt/                 # dbt Dockerfile + profiles.yml
scripts/
  setup.sh             # One-time initialization script
  init_polaris.py      # Creates Polaris catalog + grants
  init_minio.py        # Creates MinIO warehouse bucket
```

## Teardown

```bash
docker compose down -v   # stops containers and removes volumes
```

Re-running `docker compose up -d --build` followed by `./scripts/setup.sh` will give you a fresh stack.
