import logging
import time

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from src.crawler.finance_index_crawler import FinanceIndexCrawler
from src.plugins.mongodb_hook import MongoDBHook


def fetch_finance_data():
    logging.info("Fetching finance data")
    mongo_credential = MongoDBHook(conn_id='local_mongo_conn').get_credential()
    crawler = FinanceIndexCrawler(mongo_credential)
    crawler.fetch_nasdaq_data()
    time.sleep(10)
    crawler.fetch_bitcoin_data()
    crawler.close_connection()


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
}

dag = DAG(
    'finance_crawler_dag',
    default_args=default_args,
    description='Finance Crawler DAG',
    schedule_interval='@hourly',  # Run hourly
    catchup=False,
    max_active_runs=1
)

fetch_finance_data_task = PythonOperator(
    task_id='fetch_finance_data_task',
    python_callable=fetch_finance_data,
    dag=dag
)
