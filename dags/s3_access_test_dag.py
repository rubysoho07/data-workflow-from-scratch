from datetime import datetime

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from botocore.retries import bucket


default_args = {
    'owner': 'airflow'
}


dag = DAG(
    's3_test_dag',
    default_args=default_args,
    description='Test DAG S3 log data analysis',
    start_date=datetime(2021, 4, 1),
    tags=['example']
)


def task_s3_log_load(params):
    hook = S3Hook(aws_conn_id='aws_default')

    # bucket = hook.get_bucket(params['bucket_name'])

    # Get list of objects on a bucket
    keys = hook.list_keys(params['bucket_name'])

    for key in keys:
        print(key)

        obj = hook.get_key(key, params['bucket_name'])

        print(type(obj))        # <class 'boto3.resources.factory.s3.Object'>
        print(obj.bucket_name, obj.key)


task_1 = PythonOperator(
    task_id='s3_analysis',
    python_callable=task_s3_log_load,
    dag=dag
)


task_1