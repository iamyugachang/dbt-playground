## Why

A single `run_dbt_job` runs all dbt models together, making it impossible to schedule, trigger, or monitor the customer and orders pipelines independently. Splitting them into dedicated Dagster jobs gives each pipeline its own run history, schedule, and failure isolation.

## What Changes

- **Remove** the single `data_playground_dbt_assets` / `run_dbt_job` pattern
- **Add** `customer_dbt_assets` — `@dbt_assets` selecting `stg_customers`, `stg_events`, `customer_summary`
- **Add** `orders_dbt_assets` — `@dbt_assets` selecting `stg_orders`, `order_summary`
- **Add** `run_customer_job` and `run_orders_job` as separate `define_asset_job` definitions
- **Update** `schedules.py` to define two schedules (one per job)
- **Update** `__init__.py` `Definitions` to register both asset groups, jobs, and schedules

## Capabilities

### New Capabilities

- `dagster-pipeline-separation`: Two independently runnable and schedulable Dagster jobs — one per domain pipeline (customer, orders)

### Modified Capabilities

- *(none — dbt models themselves are unchanged)*

## Impact

- `apps/dagster-app/dagster_app/assets.py` — replace single `@dbt_assets` with two selective ones
- `apps/dagster-app/dagster_app/schedules.py` — replace one schedule with two
- `apps/dagster-app/dagster_app/__init__.py` — update `Definitions` to include both asset groups, jobs, and schedules
- No changes to dbt models, Postgres, Trino, or infrastructure
- Dagster restart required after code changes (`docker compose restart dagster`)
