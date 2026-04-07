## ADDED Requirements

### Requirement: Customer pipeline runs as an independent Dagster job
The system SHALL define a `customer_dbt_assets` asset function using `@dbt_assets(select=...)` covering exactly `stg_customers`, `stg_events`, and `customer_summary`. A `run_customer_job` SHALL be defined via `define_asset_job` targeting this asset function, with its own schedule.

#### Scenario: Customer job visible in Dagster UI
- **WHEN** Dagster restarts after the code change
- **THEN** `run_customer_job` appears as a separate job in the Dagster UI at http://localhost:3000

#### Scenario: Customer job runs only customer models
- **WHEN** `run_customer_job` is triggered
- **THEN** only `stg_customers`, `stg_events`, and `customer_summary` are materialized — orders models are NOT run

### Requirement: Orders pipeline runs as an independent Dagster job
The system SHALL define an `orders_dbt_assets` asset function using `@dbt_assets(select=...)` covering exactly `stg_orders` and `order_summary`. A `run_orders_job` SHALL be defined via `define_asset_job` targeting this asset function, with its own schedule.

#### Scenario: Orders job visible in Dagster UI
- **WHEN** Dagster restarts after the code change
- **THEN** `run_orders_job` appears as a separate job in the Dagster UI at http://localhost:3000

#### Scenario: Orders job runs only orders models
- **WHEN** `run_orders_job` is triggered
- **THEN** only `stg_orders` and `order_summary` are materialized — customer models are NOT run

### Requirement: Both jobs are independently schedulable
The system SHALL register two `ScheduleDefinition` entries — one per job — in the Dagster `Definitions` object, so each pipeline can be enabled/disabled independently in the Dagster UI.

#### Scenario: Schedules appear independently in Dagster UI
- **WHEN** Dagster starts with the new definitions
- **THEN** two schedules are listed under the Schedules tab, one for each job

### Requirement: Single `run_dbt_job` is removed
The previous combined job `run_dbt_job` and its schedule SHALL be removed. No combined job that runs all models together SHALL exist after this change.

#### Scenario: Old job no longer appears
- **WHEN** Dagster restarts after the change
- **THEN** `run_dbt_job` does NOT appear in the Dagster UI
