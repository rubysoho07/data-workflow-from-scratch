FROM python:3.8-slim

WORKDIR /airflow

# Airflow Home Directory
ENV AIRFLOW_HOME=/airflow

# Install Airflow
RUN apt-get update -qq && apt-get -y upgrade -qq && \
    pip install -q apache-airflow && airflow db init

# Export 8080 port for airflow webserver
EXPOSE 8080