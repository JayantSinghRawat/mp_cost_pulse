FROM apache/airflow:2.7.3

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy DAGs and plugins
COPY --chown=airflow:root dags/ ${AIRFLOW_HOME}/dags/
COPY --chown=airflow:root plugins/ ${AIRFLOW_HOME}/plugins/

