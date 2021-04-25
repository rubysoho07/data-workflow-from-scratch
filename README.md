# Data Workflow From Scratch

데이터 분석을 위한 워크플로우를 처음부터 구현해 보는 것을 목표로 합니다. 

## Airflow Docker 이미지 만들기

```shell
cd airflow
docker build -t dwfs-airflow .
docker login
docker tag dwfs-airflow hahafree12/dwfs-airflow
docker push hahafree12/dwfs-airflow
```

### 로컬에서 DB 설정

메타데이터 DB는 MySQL을 이용한다고 가정합니다.

```shell
docker run --rm -it -v $PWD/dags:/dags \ 
-e AIRFLOW__CORE__SQL_ALCHEMY_CONN=mysql://(username):(password)\@(Database Address)/(Database) dwfs-airflow bash

# 여기서부터는 컨테이너에서 실행합니다. 
airflow db init

airflow users create --username admin \
    --role Admin --firstname yungon --lastname park \
    --email myemail@address

# 비밀번호를 입력하고 나면 아래 메시지를 볼 수 있습니다. 
Admin user admin created

# 컨테이너에서 나갑니다. 
exit
```

### 로컬에서 테스트

먼저 웹서버를 실행합니다. 

```shell
docker run --rm -d -v $PWD/dags:/dags -v $PWD/logs:/airflow/logs \
-e AIRFLOW__CORE__SQL_ALCHEMY_CONN=mysql://(username):(password)\@(Database Address)/(Database) \
-p 8080:8080 --name airflow-web \
dwfs-airflow airflow webserver
```

그리고 스케줄러를 실행합니다. 

```shell
docker run --rm -d -v $PWD/dags:/dags -v $PWD/logs:/airflow/logs \
-e AIRFLOW__CORE__SQL_ALCHEMY_CONN=mysql://(username):(password)\@(Database Address)/(Database) \
--name airflow-scheduler \
dwfs-airflow airflow scheduler
```

웹 브라우저에서 `localhost:8080`으로 접속해 보면, 정상적으로 동작하는 것을 볼 수 있습니다.

정리할 때는 터미널에서 다음과 같이 입력합니다. 

```shell
docker stop airflow-web airflow-scheduler
```

## Helm으로 Kubernetes에 배포하기

```shell
helm install --set database_url=mysql://(username):(password)\@(Database Address)/(Database) airflow-test .
```

### minikube로 테스트 하는 경우

로컬 디렉터리를 minikube 클러스터에 바로 마운트 할 수 없으므로 사전 작업이 필요합니다. 

터미널 창을 켜고 다음과 같이 입력합니다.

```shell
minikube mount $PWD/dags:/data/airflow-dags
```

다른 터미널 창을 켜고 다음과 같이 입력합니다. 

```shell
minikube mount $PWD/logs:/data/airflow-logs
```

이들 프로세스는 로컬 환경에서 테스트 하는 동안 계속 켜져 있어야 합니다. 

그리고 다른 터미널 창에서 Helm Chart를 시작합니다. 

```shell
helm install --set database_url=mysql://(username):(password)\@(Database Address)/(Database) --set cluster_config.local_test=true airflow-test .
```

### NFS를 DAGs/Log 저장소로 사용하는 경우

```shell
helm install --set database_url=mysql://(username):(password)\@(Database Address)/(Database) \
--set cluster_config.use_nfs=true \
--set nfs.dags_server=(NFS 서버 주소) --set nfs.dags_path=(NFS 서버 내 경로) \
--set nfs.logs_server=(NFS 서버 주소) --set nfs.logs_path=(NFS 서버 내 경로) \
yg-airflow .
```

### 삭제할 때

삭제할 때는 다음과 같이 입력합니다. 

```shell
helm uninstall airflow-test
```

## Apache Airflow

### 로그를 S3에 저장하기 위한 과정

먼저 아래 스크립트를 활용하여 Connection URI를 생성합니다. 

```python
import json

from airflow.models.connection import Connection

c = Connection(
    conn_id='s3_log_default',
    conn_type='s3',
    host='s3-bucket-name',
    extra=json.dumps({
        "aws_access_key_id": "your aws access key",
        "aws_secret_access_key": "your aws secret access key"
    })
)

print(c.get_uri())
```

이 결과를 하나의 변수로 구성한 뒤, 다음과 같이 Helm Chart를 설치합니다. 아래 예제에서는 PostgreSQL을 메타데이터 DB로 사용하였습니다. 

```shell
AWS_CONN_URI="(위의 스크립트를 실행한 결과)"

helm install --set database_url=postgresql+psycopg2://(username):(password)\@(Database Address)/(Database) --set cluster_config.local_test=true \
--set airflow_config.remote_logging.enabled="True" --set airflow_config.remote_logging.conn_id=s3_log_default --set airflow_config.remote_logging.remote_base_log_folder="s3://s3_bucket_name" \
--set airflow_config.remote_logging.conn_id_uri=$AWS_CONN_URI \
--set airflow_config.executor=KubernetesExecutor airflow-test .
```


### DAG 생성하기

`dags/first_dags.py` 파일을 생성하고 dags_folder에 지정한 폴더에 넣습니다. 

자세한 내용은 [Airflow의 Tutorial](http://airflow.apache.org/docs/apache-airflow/stable/tutorial.html) 문서를 참고합니다.

#### Task를 테스트 하기

Airflow를 실행 중인 컨테이너에 들어가서 다음 명령을 실행합니다. 

```shell
airflow tasks test (DAG ID) (TASK ID) (날짜 - 'YYYY-MM-DD' 형식) 

# Example
airflow tasks test yungon_first print_date 2020-02-18
```

그러면 다음과 같이 output이 출력됨을 볼 수 있습니다.
```
... (앞부분 생략)
[2021-02-18 10:47:49,186] {bash.py:169} INFO - Output:
[2021-02-18 10:47:49,188] {bash.py:173} INFO - This is test.
... (뒷부분 생략)
```

#### DAG 실행을 테스트 하기

DAG 실행을 테스트하고 싶은 경우, Airflow를 실행 중인 컨테이너에서 다음 명령을 실행합니다. 

```shell
airflow dags test (DAG ID) (날짜 - 'YYYY-MM-DD' 형식)

# Example
airflow dags test yungon_first 2020-02-18
```

### 작업 예약하기

DAG을 설정할 때, `schedule_interval` 속성을 설정하여 작업을 예약할 수 있습니다. 

예시)

```python
dag = DAG(
    'dag_id',
    # ...
    schedule_interval=timedelta(days=1),
    # ...
)
```

`schedule_interval` 속성에 들어갈 수 있는 값들은 다음과 같습니다.

* Cron expression을 문자열로 넘겨줌
* `datetime.timedelta` object를 넘겨줌
* Cron preset 중 하나를 지정하여 문자열로 넘겨줌: (None, '@once', '@hourly', ...)

자세한 내용은 [DAG Runs](https://airflow.apache.org/docs/apache-airflow/stable/dag-run.html) 문서를 참고하세요. 

### 외부 DB 연결하기

외부 DB(MySQL, PostgreSQL, ...)에 연결하려면, Connection ID를 적절히 생성해 줍니다. 

Connection ID는 CLI로 생성하는 방법이나 웹서버에서 생성하는 방법이 있습니다. 

자세한 내용은 [Airflow의 문서](https://airflow.apache.org/docs/apache-airflow/stable/howto/connection.html)를 참고하여 생성합니다. 

DB에서 바로 쿼리해서 결과를 넣을 경우, 다음과 같이 수행하면 됩니다. 아례 예제는 PostgreSQL에서 쿼리를 수행할 때의 예제입니다.

```python
from airflow.providers.postgres.operators.postgres import PostgresOperator

task_1 = PostgresOperator(
    task_id='your_task_id',
    postgres_conn_id='Your Connection ID',
    sql="""SQL Query""",
    dag=dag
)
```

하지만 DB 쿼리 결과를 이용해서 다른 작업을 해야 할 경우가 있습니다. 이 때는 [Hook](https://airflow.apache.org/docs/apache-airflow/stable/concepts.html#hooks)을 이용해서 DB에 연결 후 쿼리를 수행합니다. 

```python
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

def task_test_query():
    hook = PostgresHook(postgres_conn_id='yungon_postgres_test')

    rows = hook.get_records("SELECT * FROM scheduler_core_movieschedule LIMIT 10;")

    for row in rows:
        print(row)

task_2 = PythonOperator(
    task_id='run_query_with_python',
    python_callable=task_test_query,
    dag=dag
)
```

DbApiHook 클래스를 상속하는 Hook들은 공통 기능들을 가지고 있습니다. Connection을 가져오거나, 쿼리를 수행하거나, 쿼리 수행 결과를 Pandas의 DataFrame으로 가져오는 등의 기능들을 지원합니다. MySqlHook이나, PostgresHook 등이 대표적인 사례입니다. 

DbApiHook 클래스가 제공하는 기본 기능은 [이 문서](https://airflow.apache.org/docs/apache-airflow/stable/_api/airflow/hooks/dbapi/index.html)를 참고하세요. 

### 앞의 실행 결과를 뒤에서 사용하기



### 어떻게 운영해야 할까?



## 참고자료

* [Airflow Documentation](http://airflow.apache.org/docs/apache-airflow/stable/index.html)
    * [Set Up A Database Backend](http://airflow.apache.org/docs/apache-airflow/stable/howto/set-up-database.html)
    * [Command Line Interface and Environment Variables Reference](http://airflow.apache.org/docs/apache-airflow/stable/cli-and-env-variables-ref.html)
    * [Tutorial](http://airflow.apache.org/docs/apache-airflow/stable/tutorial.html)