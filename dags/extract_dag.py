from airflow import DAG
from airflow.datasets import Dataset
from airflow.utils.task_group import TaskGroup
from pendulum import datetime

from cosmos.providers.dbt.core.operators import (
    DbtRunOperationOperator,
    DbtSeedOperator
)



with DAG(
    dag_id="extraxt_dag",
    start_date=datetime(2023, 6, 6),
    schedule="@daily",
    doc_md=__doc__,
    catchup=False,
    max_active_runs=1,
    default_args={"owner": "01-EXTRACT"}
) as dag:

    project_seeds = [
        {"project": "jaffle_shop", "seeds": [
            "raw_customers", "raw_payments", "raw_orders"]}
    ]

   

    with TaskGroup(group_id="drop_seeds_if_exist") as drop_seeds:
        for project in project_seeds:
            for seed in project["seeds"]:
                DbtRunOperationOperator(
                    task_id=f"drop_{seed}_if_exists",
                    macro_name="drop_table",
                    args={"table_name": seed},
                    project_dir=f"/usr/local/airflow/dbt/{project['project']}",
                    schema="public",
                    dbt_executable_path='/usr/local/airflow/dbt_venv/bin/dbt',
                    conn_id="postgres",
                )

    with TaskGroup(group_id="all_seeds") as create_seeds:
        for project in ["jaffle_shop"]:
            name_underscores = project.replace("-", "_")
            DbtSeedOperator(
                task_id=f"{name_underscores}_seed",
                project_dir=f"/usr/local/airflow/dbt/{project}",
                schema="public",
                dbt_executable_path='/usr/local/airflow/dbt_venv/bin/dbt',
                conn_id="postgres",
                outlets=[Dataset(f"SEED://{name_underscores.upper()}")],
            )

    drop_seeds >> create_seeds