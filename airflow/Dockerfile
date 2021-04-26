FROM python:3.8-slim

WORKDIR /airflow

# Airflow Home Directory
ENV AIRFLOW_HOME=/airflow

# Install Airflow
RUN apt-get update -qq && apt-get -y upgrade -qq && \
    apt-get install -y -qq default-libmysqlclient-dev gcc && \
    pip install -q --upgrade pip && \
    pip install -q 'apache-airflow[mysql,postgres,cncf.kubernetes,amazon]>=2.0.2'

# Copy Airflow configuration
COPY airflow.cfg kubernetes_pod_template.yaml /airflow/

VOLUME [ "/dags" ]

VOLUME [ "/airflow/logs" ]

CMD echo "Airflow Container Started!"