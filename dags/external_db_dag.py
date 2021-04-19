from datetime import datetime

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator


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

task_1