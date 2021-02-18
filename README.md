# Data Workflow From Scratch

데이터 분석을 위한 워크플로우를 처음부터 구현해 보는 것을 목표로 합니다. 

## Airflow Docker 이미지 만들기

```shell
cd airflow
docker build -t dwfs-airflow .
```

### 로컬에서 DB 설정

메타데이터 DB는 MySQL을 이용한다고 가정합니다.

```shell
docker run --rm -it -v $PWD/dags:/dags \ 
-e AIRFLOW__CORE__SQL_ALCHEMY_CONN=mysql+pymysql://(username):(password)\@(Database Address)/(Database) dwfs-airflow bash

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
docker run --rm -d -v $PWD/dags:/dags \
-e AIRFLOW__CORE__SQL_ALCHEMY_CONN=mysql+pymysql://(username):(password)\@(Database Address)/(Database) \
-p 8080:8080 --name airflow-web \
dwfs-airflow airflow webserver
```

그리고 스케줄러를 실행합니다. 

```shell
docker run --rm -d -v $PWD/dags:/dags \
-e AIRFLOW__CORE__SQL_ALCHEMY_CONN=mysql+pymysql://(username):(password)\@(Database Address)/(Database) \
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
helm install --set database_url=mysql+pymysql://(username):(password)\@(Database Address)/(Database) airflow-test .
```

### NFS를 DAG 저장소로 사용하는 경우

```shell
helm install --set database_url=mysql+pymysql://(username):(password)\@(Database Address)/(Database) \
--set cluster_config.use_nfs=true \
--set nfs.server=(NFS 서버 주소) \
--set nfs.path=(NFS 서버 내 경로) \
yg-airflow .
```

### 삭제할 때

삭제할 때는 다음과 같이 입력합니다. 

```shell
helm uninstall airflow-test
```

## Apache Airflow



### DAG 생성하기



### 작업 순서 정하기



### 작업 예약하기



### 외부 DB 연결하기



### 앞의 실행 결과를 뒤에서 사용하기



### 어떻게 운영해야 할까?



## 참고자료

* [Airflow Documentation](http://airflow.apache.org/docs/apache-airflow/stable/index.html)
    * [Set Up A Database Backend](http://airflow.apache.org/docs/apache-airflow/stable/howto/set-up-database.html)
    * [Command Line Interface and Environment Variables Reference](http://airflow.apache.org/docs/apache-airflow/stable/cli-and-env-variables-ref.html)