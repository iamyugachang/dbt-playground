from dagster import Definitions, load_assets_from_modules
from dagster_dbt import DbtCliResource

from . import assets, project, schedules

# Load assets
all_assets = load_assets_from_modules([assets])

# Point to the existing profiles directory in infrastructure/dbt/profiles
# Correct path relative to the repo root we defined in project.py
profiles_dir = project.REPO_ROOT / "infrastructure" / "dbt" / "profiles"

defs = Definitions(
    assets=all_assets,
    schedules=[schedules.every_10_min_schedule],
    resources={
        "dbt": DbtCliResource(
            project_dir=project.dbt_project,
            profiles_dir=profiles_dir,
        ),
    },
)
