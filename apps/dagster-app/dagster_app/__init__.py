from dagster import Definitions
from dagster_dbt import DbtCliResource

from . import project
from .assets import customer_dbt_assets, orders_dbt_assets
from .schedules import customer_schedule, orders_schedule, run_customer_job, run_orders_job

profiles_dir = project.REPO_ROOT / "infrastructure" / "dbt" / "profiles"

defs = Definitions(
    assets=[customer_dbt_assets, orders_dbt_assets],
    schedules=[customer_schedule, orders_schedule],
    resources={
        "dbt": DbtCliResource(
            project_dir=project.dbt_project,
            profiles_dir=profiles_dir,
        ),
    },
)
