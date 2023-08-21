Overview
========

Welcome to Astronomer! This project was generated after you ran 'astro dev init' using the Astronomer CLI. This readme describes the contents of the project, as well as how to run Apache Airflow on your local machine.

Setup
================
```
astro dev init
```

Install packages required for astronomer-cosmos's underlying packages

```
# packages.txt
gcc
python3-dev
```
In requirements.txt
```
astronomer-cosmos[dbt.all]
```
Using `dbt.all`will install all Cosmos, dbt, and all of the supported database types (postgres, bigquery, redshift, snowflake)

Create a new folder dbt

Clone the repo ‣ in it

```
git clone https://github.com/dbt-labs/jaffle_shop.git
```
jaffle_shop is a fictional ecommerce store. This dbt project transforms raw data from an app database into a customers and orders model ready for analytics.
- models: Each model lives in a single SQL/Python file and contains logic that either transforms raw data into a dataset ready for analytics or, more often, is an intermediate step in such a transformation.
- - You can create dependencies between different models that get resolved when running dbt run. That’s the power of Jinja. Take ref as an example in customers.sql with staging.
- Staging models are those that read from a source (csv, SQL table, etc) and involve data cleaning. Sometimes joins and more involved transformations are required.
- `seeds`: CSV files with static data that you can load into your data platform with dbt.
- `dbt_project.yml`: defines the directory of the dbt project and other project configurations such as the name, the version, profile (will come back at it in a minute) etc.

Create a folder `macros` in jaffle_shop

Macros in Jinja are pieces of code that can be reused multiple times – they are analogous to "functions" in other programming languages. They are extremely useful if you find yourself repeating code across multiple models.

```
# macros/drop_table.sql
{%- macro drop_table(table_name) -%}
    {%- set drop_query -%}
        DROP TABLE IF EXISTS {{ target.schema }}.{{ table_name }} CASCADE
    {%- endset -%}
    {% do run_query(drop_query) %}
{%- endmacro -%}
```
Create a new file docker-compose.override.yml

```
version: "3.1"
services:
  scheduler:
    volumes:
      - ./dbt:/usr/local/airflow/dbt:rw

  webserver:
    volumes:
      - ./dbt:/usr/local/airflow/dbt:rw

  triggerer:
    volumes:
      - ./dbt:/usr/local/airflow/dbt:rw
```

Add the following code to the Dockerfile to run dbt in a python virtual environment and avoid dependency conflicts with Airflow

```
# install dbt into a venv to avoid package dependency conflicts
WORKDIR "/usr/local/airflow"
COPY dbt-requirements.txt ./
RUN python -m virtualenv dbt_venv && source dbt_venv/bin/activate && \
    pip install --no-cache-dir -r dbt-requirements.txt && deactivate
```
Create the file dbt-requirements.txt

```
dbt-core==1.3.1
dbt-postgres==1.3.1
```
Code
================
**Seeds**

```
from airflow import DAG
from airflow.datasets import Dataset
from airflow.utils.task_group import TaskGroup
from pendulum import datetime

from cosmos.providers.dbt.core.operators import (
    DbtDepsOperator,
    DbtRunOperationOperator,
    DbtSeedOperator,
)

with DAG(
    dag_id="import-seeds",
    start_date=datetime(2023, 1, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
) as dag:

    project_seeds = [
        {
            "project": "jaffle_shop",
            "seeds": ["raw_customers", "raw_payments", "raw_orders"],
        }
    ]

    deps_install = DbtDepsOperator(
        task_id="jaffle_shop_install_deps",
        project_dir=f"/usr/local/airflow/dbt/jaffle_shop",
        schema="public",
        dbt_executable_path="/usr/local/airflow/dbt_venv/bin/dbt",
        conn_id="postgres",
    )

    with TaskGroup(group_id="drop_seeds_if_exist") as drop_seeds:
        for project in project_seeds:
            for seed in project["seeds"]:
                DbtRunOperationOperator(
                    task_id=f"drop_{seed}_if_exists",
                    macro_name="drop_table",
                    args={"table_name": seed},
                    project_dir=f"/usr/local/airflow/dbt/{project['project']}",
                    schema="public",
                    dbt_executable_path="/usr/local/airflow/dbt_venv/bin/dbt",
                    conn_id="postgres",
                )

    create_seeds = DbtSeedOperator(
        task_id=f"jaffle_shop_seed",
        project_dir=f"/usr/local/airflow/dbt/jaffle_shop",
        schema="public",
        dbt_executable_path="/usr/local/airflow/dbt_venv/bin/dbt",
        conn_id="postgres",
        outlets=[Dataset(f"SEED://JAFFLE_SHOP")],
     )

    deps_install >> drop_seeds >> create_seeds
```
