from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.utils.dates import days_ago

from src.analyzer.process_monitor import ProcessMonitor
from src.plugins.mongodb_hook import MongoDBHook

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1)
}

# Define the MongoDB connection object
mongo_hook = MongoDBHook(conn_id='local_mongo_conn')
mongo_server_hook = MongoDBHook(conn_id='server_mongo_conn')

dag = DAG(
    'analyze_dag',
    default_args=default_args,
    description='Analyze DAG',
    schedule_interval='@hourly',  # Run hourly
    catchup=False,
    max_active_runs=1
)

spark_analyze = SparkSubmitOperator(
    task_id='spark_analyze',
    application='/opt/airflow/dags/src/analyzer/spark_analyzer.py',
    packages='org.mongodb.spark:mongo-spark-connector_2.12:3.0.1',
    conf={
        'spark.mongodb.input.uri': mongo_hook.get_uri()
    },
    application_args=[
        mongo_hook.get_uri(),
        mongo_hook.get_schema()
    ],
    executor_memory='1g',
    driver_memory='1g',
    conn_id='spark_local',
    dag=dag
)

mongo_dump = BashOperator(
    task_id='mongo_dump',
    bash_command='cd $SOURCE_DIR && scripts/mongo/mongo_dump.sh ' + mongo_hook.get_uri(),
    dag=dag
)

mongo_restore = BashOperator(
    task_id='mongo_restore',
    bash_command='cd $SOURCE_DIR && scripts/mongo/mongo_restore.sh ' + mongo_server_hook.get_uri(),
    dag=dag
)

verify_process = PythonOperator(
    task_id='verify_process',
    python_callable=ProcessMonitor(MongoDBHook(conn_id='local_mongo_conn').get_credential()).check_and_notify,
    dag=dag
)

spark_analyze >> mongo_dump >> mongo_restore
spark_analyze >> verify_process
