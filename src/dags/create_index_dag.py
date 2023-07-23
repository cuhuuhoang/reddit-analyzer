from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from src.core.setup_index import IndexCreator
from src.plugins.mongodb_hook import MongoDBHook

# Define the DAG's default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 7, 1),
    'catchup': False,  # Set to False to skip past runs when the DAG is created
}

mongo_credential = MongoDBHook(conn_id='local_mongo_conn').get_credential()

# Create the Airflow DAG
dag = DAG(
    'setup_index_dag',
    default_args=default_args,
    description='Setup Index DAG',
    schedule_interval=None,  # Set to None to run manually
    max_active_runs=1
)

setup_index_task = PythonOperator(
    task_id='setup_index_task',
    python_callable=IndexCreator(mongo_credential).setup_index,
    dag=dag,
)
