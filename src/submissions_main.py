from logging_config import *
import time

from sentiment_analyzer import SentimentAnalyzer
from spark_analyzer import SparkAnalyzer
from submissions_crawler import fetch_new_submissions


if __name__ == '__main__':
    sentiment_analyzer = SentimentAnalyzer()

    while True:
        logging.info(f"spark_analyzer")
        spark_analyzer = SparkAnalyzer()
        spark_analyzer.analyze_by_hours()
        spark_analyzer.analyze_by_days()
        spark_analyzer.stop()

        subreddit_list = [
            'wallstreetbets',
            'bitcoin',
            'stocks',
            'StockMarket',
            'investing',
            'cryptocurrency',
            'ethereum',
            'altcoin'
        ]
        for subreddit in subreddit_list:
            logging.info(f"Fetching new submissions for subreddit: '{subreddit}'")
            fetch_new_submissions(subreddit, sentiment_analyzer, 1000)
            time.sleep(10)
