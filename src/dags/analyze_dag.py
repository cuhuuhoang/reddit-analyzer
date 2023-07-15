from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from src.analyzer.process_monitor import ProcessMonitor
from src.analyzer.spark_analyzer import SparkAnalyzer

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1)
}

dag = DAG(
    'analyze_dag',
    default_args=default_args,
    description='Analyze DAG',
    schedule_interval='@hourly',  # Run hourly
    catchup=False,
    max_active_runs=1
)

spark_analyze = PythonOperator(
    task_id='spark_analyze',
    python_callable=SparkAnalyzer().analyze_by_hours,
    dag=dag
)

mongo_dump = BashOperator(
    task_id='mongo_dump',
    bash_command='cd $SOURCE_DIR && scripts/mongo/mongo_dump.sh resources/mongo-docker-compose-credential.json',
    dag=dag
)

mongo_restore = BashOperator(
    task_id='mongo_restore',
    bash_command='cd $SOURCE_DIR && scripts/mongo/mongo_restore.sh resources/mongo-docker-prod2-credential.json',
    dag=dag
)

verify_process = PythonOperator(
    task_id='verify_process',
    python_callable=ProcessMonitor().check_and_notify,
    dag=dag
)

spark_analyze >> mongo_dump >> mongo_restore
spark_analyze >> verify_process
