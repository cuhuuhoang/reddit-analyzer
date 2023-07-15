import logging

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from src.analyzer.sentiment_analyzer import SentimentAnalyzer
from src.crawler.submissions_crawler import fetch_new_submissions

subreddit_list = [
    "wallstreetbets",
    "bitcoin",
    "stocks",
    "StockMarket",
    "investing",
    "cryptocurrency",
    "ethereum",
    "altcoin"
]


def fetch_submissions(subreddit):
    sentiment_analyzer = SentimentAnalyzer()
    logging.info(f"Fetching new submissions for subreddit: '{subreddit}'")
    fetch_new_submissions(subreddit, sentiment_analyzer, 1000)


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1)
}

dag = DAG(
    'crawler_dag',
    default_args=default_args,
    description='Crawler DAG',
    schedule_interval='*/20 * * * *',  # Run every 20 minutes
    catchup=False,
    max_active_runs=1
)

start_task = EmptyOperator(task_id='start_task', dag=dag)
end_task = EmptyOperator(task_id='end_task', dag=dag)

for subreddit in subreddit_list:
    subreddit_task = PythonOperator(
        task_id=f'fetch_submissions_{subreddit}',
        python_callable=fetch_submissions,
        op_kwargs={'subreddit': subreddit},
        dag=dag,
        pool='praw'
    )
    start_task >> subreddit_task >> end_task
