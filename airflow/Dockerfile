FROM python:3.8-slim

WORKDIR /airflow

# Airflow Home Directory
ENV AIRFLOW_HOME=/airflow

# Install Airflow
RUN apt-get update -qq && apt-get -y upgrade -qq && \
    pip install -q apache-airflow && airflow db init

# If you want to use MySQL as database backend, install pymysql
RUN pip install -q pymysql

# If you want to use PostgreSQL as database backend, install psycopg2-binary
RUN pip install -q psycopg2-binary

# Copy Airflow configuration
COPY airflow.cfg /airflow

VOLUME [ "/dags" ]