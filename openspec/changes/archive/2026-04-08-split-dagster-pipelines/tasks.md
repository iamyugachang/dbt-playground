## 1. Dagster — Split Asset Functions

- [x] 1.1 Replace `data_playground_dbt_assets` in `apps/dagster-app/dagster_app/assets.py` with two `@dbt_assets` functions:
  - `customer_dbt_assets` with `select="stg_customers stg_events customer_summary"`
  - `orders_dbt_assets` with `select="stg_orders order_summary"`

## 2. Dagster — Split Jobs and Schedules

- [x] 2.1 Replace `run_dbt_job` and `every_10_min_schedule` in `apps/dagster-app/dagster_app/schedules.py` with:
  - `run_customer_job = define_asset_job(selection=[customer_dbt_assets])`
  - `run_orders_job = define_asset_job(selection=[orders_dbt_assets])`
  - `customer_schedule = ScheduleDefinition(job=run_customer_job, cron_schedule="*/10 * * * *")`
  - `orders_schedule = ScheduleDefinition(job=run_orders_job, cron_schedule="*/10 * * * *")`

## 3. Dagster — Update Definitions

- [x] 3.1 Update `apps/dagster-app/dagster_app/__init__.py` to register both asset groups, both jobs, and both schedules in `Definitions`

## 4. Verification

- [ ] 4.1 Restart Dagster: `docker compose restart dagster`
- [ ] 4.2 Confirm `run_customer_job` and `run_orders_job` appear as separate jobs in the Dagster UI at http://localhost:3000
- [ ] 4.3 Confirm `run_dbt_job` no longer appears
- [ ] 4.4 Trigger `run_customer_job` — verify only `stg_customers`, `stg_events`, `customer_summary` materialize
- [ ] 4.5 Trigger `run_orders_job` — verify only `stg_orders`, `order_summary` materialize
