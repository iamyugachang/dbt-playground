from dagster import ScheduleDefinition, define_asset_job

from .assets import customer_dbt_assets, orders_dbt_assets

run_customer_job = define_asset_job(
    name="run_customer_job",
    selection=[customer_dbt_assets],
)

run_orders_job = define_asset_job(
    name="run_orders_job",
    selection=[orders_dbt_assets],
)

customer_schedule = ScheduleDefinition(
    job=run_customer_job,
    cron_schedule="*/10 * * * *",
)

orders_schedule = ScheduleDefinition(
    job=run_orders_job,
    cron_schedule="*/10 * * * *",
)
