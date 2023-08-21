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
