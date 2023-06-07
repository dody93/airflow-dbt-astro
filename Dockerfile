FROM quay.io/astronomer/astro-runtime:8.4.0

# install dbt into a venv to avoid package dependency conflicts
WORKDIR "/usr/local/airflow"
COPY dbt-requirements.txt ./
RUN python -m venv dbt_venv && source dbt_venv/bin/activate && \
pip install --no-cache-dir dbt-postgres && deactivate
