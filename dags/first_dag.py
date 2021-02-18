# From http://airflow.apache.org/docs/apache-airflow/stable/tutorial.html
from datetime import timedelta, datetime

# DAG object to instantiate a DAG
from airflow import DAG

# Operators
from airflow.operators.bash import BashOperator


# Arguments will be passed on to each operator
# BaseOperator's parameter reference:
# http://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/models/index.html#airflow.models.BaseOperator
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['hahafree12@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'yungon_first',
    default_args=default_args,
    description='First DAG example',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2021, 2, 18),
    tags=['example']
)

# Examples of tasks created by instantiating operators
t1 = BashOperator(
    task_id='print_date',
    bash_command='date',
    dag=dag
)

template_command = 'echo "{{ params.message }}"'

t2 = BashOperator(
    task_id='print_message',
    bash_command=template_command,
    params={ "message": "This is test."},
    dag=dag
)

# Run t1 first, after run t2
t1 >> t2