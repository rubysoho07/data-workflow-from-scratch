from datetime import datetime

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

default_args = {
    'owner': 'airflow'
}


dag = DAG(
    'postgres_test_dag',
    default_args=default_args,
    description='Test DAG using PostgreSQL',
    start_date=datetime(2021, 4, 1),
    tags=['example']
)


task_1 = PostgresOperator(
    task_id='run_query',
    postgres_conn_id='yungon_postgres_test',
    sql="""SELECT * FROM scheduler_core_movieschedule;""",
    dag=dag
)


def task_test_query():
    hook = PostgresHook(postgres_conn_id='yungon_postgres_test')
    # hook = PostgresHook('yungon_postgres_test')

    rows = hook.get_records("SELECT * FROM scheduler_core_movieschedule LIMIT 10;")

    for row in rows:
        print(row)

task_2 = PythonOperator(
    task_id='run_query_with_python',
    python_callable=task_test_query,
    dag=dag
)


task_1 >> task_2