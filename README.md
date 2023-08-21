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
