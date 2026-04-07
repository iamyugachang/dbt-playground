from dagster import AssetExecutionContext
from dagster_dbt import DbtCliResource, dbt_assets

from .project import dbt_project


@dbt_assets(
    manifest=dbt_project.manifest_path,
    select="stg_customers stg_events customer_summary",
)
def customer_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["run"], context=context).stream()


@dbt_assets(
    manifest=dbt_project.manifest_path,
    select="stg_orders order_summary",
)
def orders_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["run"], context=context).stream()
