## Context

Dagster's `@dbt_assets(manifest=...)` without a `select` parameter creates one asset node per dbt model, all under one asset function. To split into two independent jobs, the `select` parameter is used to scope each `@dbt_assets` function to specific models. Each scoped function becomes its own asset group, and `define_asset_job` can then target each group independently.

Current structure:
```
assets.py
  └── data_playground_dbt_assets    @dbt_assets (all models)

schedules.py
  └── run_dbt_job → every_10_min_schedule

__init__.py
  └── Definitions(assets=[all_assets], schedules=[every_10_min_schedule])
```

Target structure:
```
assets.py
  ├── customer_dbt_assets           @dbt_assets(select="stg_customers stg_events customer_summary")
  └── orders_dbt_assets             @dbt_assets(select="stg_orders order_summary")

schedules.py
  ├── run_customer_job → customer_schedule (every 10 min)
  └── run_orders_job  → orders_schedule   (every 10 min)

__init__.py
  └── Definitions(
        assets=[customer_dbt_assets, orders_dbt_assets],
        schedules=[customer_schedule, orders_schedule]
      )
```

## Goals / Non-Goals

**Goals:**
- Two independently triggerable Dagster jobs visible in the UI
- Each job runs only its domain's dbt models
- Both jobs share the same `DbtCliResource` (same dbt project, same profiles)

**Non-Goals:**
- Changing dbt model logic or dependencies
- Different schedules per pipeline (both stay at 10 min for now)
- Asset partitioning or backfills

## Decisions

**Use `select` parameter on `@dbt_assets`, not separate dbt projects**
Dagster's `dbt_assets(select="model1 model2")` uses the same dbt manifest but filters which models the asset function covers. This avoids duplicating dbt project config and keeps a single `dbt compile` step.

**Two `@dbt_assets` functions, not one with `AssetSelection`**
`define_asset_job(selection=AssetSelection.groups("orders"))` could work but requires asset group tags on dbt models (via dbt `config(group=...)`). Using `select` on `@dbt_assets` is simpler and doesn't require modifying model SQL files.

**Both jobs keep the same 10-min schedule**
Keeps the change minimal. Schedules can be adjusted independently later since they're now separate.

## Risks / Trade-offs

- **`stg_orders` and `order_summary` must exist in the manifest** before the new `orders_dbt_assets` can compile — `dbt compile` must be run first (already done as part of setup.sh).
- **Dagster restart required** after `assets.py` changes — the manifest is loaded at startup.
- **No cross-job dependencies** — if `order_summary` ever needed `stg_customers`, the job split would break that. Currently it doesn't, so this is safe.
