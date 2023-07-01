from logging_config import *
import time

from submissions_crawler import fetch_new_submissions


def run_sample_crawl(subreddit_name, limit):
    start_time = time.time()
    fetch_new_submissions(subreddit_name, limit)
    end_time = time.time()
    runtime = end_time - start_time
    logging.info(f"fetch_new_submissions completed in {runtime:.3f} seconds")


if __name__ == '__main__':
    while True:
        subreddit_list = [
            'wallstreetbets',
            'bitcoin',
            'cryptocurrency',
            'ethereum',
            'altcoin'
        ]
        for subreddit in subreddit_list:
            logging.info(f"Fetching new submissions for subreddit: '{subreddit}'")
            fetch_new_submissions(subreddit, 1000)
            time.sleep(10)
        logging.info("Waiting for 5 minutes before running again...")
        time.sleep(300) # Wait for 5 minutes (300 seconds) before running again
