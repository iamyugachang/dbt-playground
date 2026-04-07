### Requirement: Orders source data exists in Postgres
The system SHALL seed a `shop.orders` table in Postgres via `infrastructure/postgres/init_data.sql` containing at least 5 rows with fields: `order_id`, `customer_id`, `product_id`, `quantity`, `order_date`. All `customer_id` and `product_id` values SHALL reference existing rows in `shop.customers` and `shop.products`.

#### Scenario: Orders table seeded on fresh start
- **WHEN** `docker compose down -v && docker compose up -d --build` is run
- **THEN** `shop.orders` exists in Postgres with at least 5 rows

#### Scenario: Orders accessible via Trino
- **WHEN** a Trino query runs `SELECT * FROM postgres.public.orders`
- **THEN** all seeded rows are returned with correct column names and types

### Requirement: Orders registered as a dbt source
The system SHALL declare `orders` as a table under the `shop` source in `apps/dbt-analytics/models/sources.yml` so dbt models can reference it via `{{ source('shop', 'orders') }}`.

#### Scenario: dbt source compiles without error
- **WHEN** `dbt compile` runs after adding the source
- **THEN** no source-not-found errors appear in the output

### Requirement: Staging model cleans orders data
The system SHALL provide a dbt model `stg_orders` at `apps/dbt-analytics/models/staging/stg_orders.sql` that selects from `{{ source('shop', 'orders') }}` and renames/casts columns into canonical form: `order_id`, `customer_id`, `product_id`, `quantity`, `order_date`.

#### Scenario: stg_orders model runs successfully
- **WHEN** `dbt run --select stg_orders` executes
- **THEN** the model materializes without errors and row count matches source

### Requirement: Mart model aggregates orders per customer
The system SHALL provide a dbt model `order_summary` at `apps/dbt-analytics/models/marts/order_summary.sql` that references `{{ ref('stg_orders') }}` and produces one row per `customer_id` with columns: `customer_id`, `total_orders` (count), `total_spend` (sum of quantity × product price, or sum of order amounts), `last_order_date`.

#### Scenario: order_summary materializes as Iceberg table
- **WHEN** `dbt run --select order_summary` executes
- **THEN** an Iceberg table `iceberg.public.order_summary` is created in MinIO via Polaris

#### Scenario: Aggregation is correct
- **WHEN** `SELECT * FROM iceberg.public.order_summary` runs in Trino
- **THEN** each customer appears at most once and `total_orders` equals the count of their rows in `shop.orders`

### Requirement: Dagster materializes the orders pipeline
The existing Dagster `run_dbt_job` SHALL include `stg_orders` and `order_summary` as assets without any code changes to `assets.py` — they are discovered automatically from the recompiled `manifest.json`.

#### Scenario: New assets visible in Dagster UI after manifest recompile
- **WHEN** `dbt compile` runs and Dagster restarts
- **THEN** `stg_orders` and `order_summary` appear as assets in the Dagster UI at http://localhost:3000

#### Scenario: Full pipeline run succeeds
- **WHEN** `run_dbt_job` is triggered in Dagster
- **THEN** both `stg_orders` and `order_summary` materialize successfully alongside existing assets
