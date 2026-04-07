## 1. Postgres — Seed Orders Data

- [x] 1.1 Add `shop.orders` table definition and seed rows to `infrastructure/postgres/init_data.sql` (fields: `order_id`, `customer_id`, `product_id`, `quantity`, `order_date`; at least 5 rows referencing existing customers and products)
- [ ] 1.2 Tear down and restart services to re-seed: `docker compose down -v && docker compose up -d --build`
- [ ] 1.3 Verify: `SELECT * FROM postgres.public.orders` in Trino returns seeded rows

## 2. dbt — Source Registration

- [x] 2.1 Add `orders` table under the `shop` source in `apps/dbt-analytics/models/sources.yml`

## 3. dbt — Staging Model

- [x] 3.1 Create `apps/dbt-analytics/models/staging/stg_orders.sql` selecting from `{{ source('shop', 'orders') }}` with renamed/cast columns: `order_id`, `customer_id`, `product_id`, `quantity`, `order_date`

## 4. dbt — Mart Model

- [x] 4.1 Create `apps/dbt-analytics/models/marts/order_summary.sql` referencing `{{ ref('stg_orders') }}`, aggregating per `customer_id`: `total_orders` (COUNT), `total_spend` (SUM of quantity × price via join with `stg_customers` or products source), `last_order_date` (MAX)

## 5. Verification

- [ ] 5.1 Run `docker compose exec dbt dbt run --select stg_orders order_summary` and confirm both models succeed
- [ ] 5.2 Run `docker compose exec dbt dbt compile` to regenerate `manifest.json`
- [ ] 5.3 Restart Dagster: `docker compose restart dagster`
- [ ] 5.4 Confirm `stg_orders` and `order_summary` appear as assets in Dagster UI at http://localhost:3000
- [ ] 5.5 Trigger `run_dbt_job` in Dagster and confirm all assets materialize successfully
