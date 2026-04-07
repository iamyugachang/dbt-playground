## Context

The existing pipeline runs all dbt models via a single `dbt_assets` decorator in Dagster that reads from `manifest.json`. Any new dbt model added to the project is automatically picked up — no new Dagster asset code is needed. The `shop` Postgres source already has `customers` and `products` tables. Orders is the natural missing link.

Current data flow:
```
postgres.shop.customers → stg_customers ─┐
                                          ├→ customer_summary (Iceberg)
iceberg.public_data.events → stg_events ─┘
```

Target:
```
postgres.shop.customers → stg_customers ─┐
                                          ├→ customer_summary (Iceberg)
iceberg.public_data.events → stg_events ─┘

postgres.shop.orders ──→ stg_orders ──→ order_summary (Iceberg)
```

## Goals / Non-Goals

**Goals:**
- Seed `shop.orders` in Postgres with realistic sample data referencing existing customers and products
- Add `stg_orders` staging model (light cleaning, no joins)
- Add `order_summary` mart model (per-customer aggregation: total orders, total spend, last order date)
- Have the new models materialize as Iceberg tables via the existing Dagster job

**Non-Goals:**
- Joining orders with the events pipeline (out of scope for this change)
- Real-time or streaming ingestion
- Any changes to Dagster scheduling or the existing `customer_summary` model

## Decisions

**Use existing `dbt_assets` Dagster asset, not a new one**
Dagster's `dbt_assets(manifest=...)` pattern automatically discovers all dbt models in the compiled manifest. Adding new dbt models and re-running `dbt compile` is sufficient. Creating a separate Dagster asset would be unnecessary complexity.

**Seed orders in `init_data.sql`, not as a dbt seed file**
Orders reference `customer_id` and `product_id` from Postgres tables — placing them in `init_data.sql` keeps all relational Postgres seeding in one place and lets Postgres enforce FK integrity at init time. dbt seeds are appropriate for flat reference data (like the Iceberg events CSV), not relational transactional data.

**`order_summary` materializes to Iceberg (not Postgres)**
Consistent with the existing `customer_summary` mart — all output tables land in Iceberg via Trino, keeping the output layer uniform and queryable via Polaris.

**Staging model does no joins**
`stg_orders` only renames and casts columns from the raw source. Joins and aggregations belong in the mart layer (`order_summary`), following the existing staging conventions in `stg_customers.sql`.

## Risks / Trade-offs

- **Re-seed required**: Adding `orders` to `init_data.sql` only takes effect on a fresh `docker compose down -v && docker compose up -d --build`. Existing running environments need a full teardown.
- **Manifest must be recompiled**: Dagster reads `manifest.json` — after adding models, `dbt compile` must run before Dagster sees the new assets. `setup.sh` already does this in step 5, so a full `setup.sh` re-run handles it.
- **No FK constraints in Postgres init**: The init SQL uses plain `INSERT` — if seed data references non-existent customer/product IDs it will silently succeed. Care needed in seed data authoring.
