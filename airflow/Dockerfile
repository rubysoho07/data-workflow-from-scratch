FROM python:3.8-slim

WORKDIR /airflow

# Airflow Home Directory
ENV AIRFLOW_HOME=/airflow

# Install Airflow
RUN apt-get update -qq && apt-get -y upgrade -qq && \
    pip install -q apache-airflow pymysql psycopg2-binary

# Copy Airflow configuration
COPY airflow.cfg /airflow

VOLUME [ "/dags" ]

CMD echo "Airflow Container Started!"