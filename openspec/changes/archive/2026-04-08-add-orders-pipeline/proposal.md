## Why

The playground currently has a customer_summary pipeline but no order data, leaving the `products` table in Postgres unused and the shop domain incomplete. Adding an orders pipeline closes the loop — connecting customers, products, and transactions into a meaningful end-to-end data flow.

## What Changes

- **New Postgres table**: `shop.orders` seeded via `infrastructure/postgres/init_data.sql` with `order_id`, `customer_id`, `product_id`, `quantity`, `order_date`
- **New dbt staging model**: `stg_orders` reading from `postgres.shop.orders` via Trino
- **New dbt mart model**: `order_summary` — aggregated per customer (total orders, total spend, last order date) written as an Iceberg table
- **New Dagster asset**: `order_summary` asset wired to the existing dbt resource, included in the existing `run_dbt_job`
- **Updated dbt sources**: add `orders` to the existing Postgres source definition

## Capabilities

### New Capabilities

- `orders-pipeline`: End-to-end pipeline from `shop.orders` (Postgres) → `stg_orders` → `order_summary` (Iceberg), orchestrated by Dagster

### Modified Capabilities

- *(none — existing customer_summary pipeline is unchanged)*

## Impact

- `infrastructure/postgres/init_data.sql` — add `orders` table + seed rows (requires fresh `docker compose down -v` + `up` to re-seed)
- `apps/dbt-analytics/models/sources.yml` — add `orders` source under `shop`
- `apps/dbt-analytics/models/staging/` — new `stg_orders.sql`
- `apps/dbt-analytics/models/marts/` — new `order_summary.sql`
- `apps/dagster-app/dagster_app/assets.py` — new Dagster dbt asset for `order_summary`
- No changes to docker-compose.yml, Trino config, or Polaris
- Re-running `setup.sh` after data re-seed is sufficient to apply dbt changes
