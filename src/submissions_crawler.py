import hashlib
import time

from logging_config import *
from reddit_crawler_utils import create_reddit_instance
from sentiment_analyzer import PARSER_KEY, SentimentAnalyzer
from mongodb_client import MongoDBClient


def update_submission(submission_collection, submission_data):
    """
    This function is responsible for updating the submission information in the database collection.
    It checks if the submission already exists in the collection based on its ID. If the submission exists,
    it compares the fields in the submission_data with the existing submission and updates the collection
    if there are any differences. If the submission is new, it inserts it into the collection.

    Args:
        submission_collection (MongoDB collection): The collection to update.
        submission_data (dict): The submission data to update.

    Returns:
        bool: True if it's a new post, False otherwise.
    """
    # Remove selftext for saving disk
    submission_data.pop('selftext')
    # Remove title as well
    submission_data.pop('title')

    existing_submission = submission_collection.find_one({'id': submission_data['id']})

    if existing_submission:
        # Check if any field in submission_data is different from the existing submission
        fields_to_update = {k: v for k, v in submission_data.items() if existing_submission.get(k) != v}

        if fields_to_update:
            submission_collection.update_one({'id': submission_data['id']}, {'$set': fields_to_update})
            return False  # Not a new post

    else:
        # Insert the new submission into the collection
        submission_collection.insert_one(submission_data)
        return True  # New post


def update_submission_scores(collection, submission_score_data):
    """
    This function updates the scores and metrics of a submission in the database collection.
    It checks if the submission already exists in the collection based on its ID. If it exists,
    it compares the score-related fields (upvote ratio, ups, score, num_comments) in the
    submission_score_data with the existing submission and updates the collection if there are any differences.
    If the submission is new, it inserts it into the collection.

    Args:
        collection (MongoDB collection): The collection to update.
        submission_score_data (dict): The submission score data to update.

    Returns:
        bool: True if the submission was updated, False otherwise.
    """
    submission_id = submission_score_data['id']

    # Check if the submission exists in the submission_scores collection
    existing_submission = collection.find_one({'id': submission_id})

    if existing_submission:
        # Check if any of the values have changed
        if (existing_submission['upvote_ratio'] != submission_score_data['upvote_ratio'] or
                existing_submission['ups'] != submission_score_data['ups'] or
                existing_submission['score'] != submission_score_data['score'] or
                existing_submission['num_comments'] != submission_score_data['num_comments']):
            # Update the submission in the collection
            collection.update_one(
                {'id': submission_id},
                {'$set': submission_score_data}
            )
            return True

    else:
        # Insert the new submission into the collection
        collection.insert_one(submission_score_data)
        return True

    return False


def update_sentiment_values(collection, analyzer, submission_data):
    """
    This function calculates the sentiment value of a submission and updates it in the database collection.
    It first checks if the submission meets the criteria for sentiment analysis (having a minimum length for
    the title and selftext). It then generates a hash check value based on the title, selftext, and a predefined key.
    If the submission already exists in the collection and the hash check matches, it skips the update.
    Otherwise, it calculates the sentiment value using the analyzer object and inserts or updates the sentiment
    value in the collection.

    Args:
        collection (MongoDB collection): The collection to update.
        analyzer (SentimentAnalyzer): The sentiment analyzer object.
        submission_data (dict): The submission data to update.

    Returns:
        bool: True if the sentiment value was updated, False otherwise.
    """
    if 'selftext' not in submission_data or submission_data['title_length'] < 10 \
            or submission_data['selftext_length'] < 100:
        return False

    title = submission_data['title']
    selftext = submission_data['selftext']

    hash_check = hashlib.sha256((PARSER_KEY + title + selftext).encode()).hexdigest()

    existing_object = collection.find_one({'id': submission_data['id']})

    if existing_object and existing_object.get('hash_check') == hash_check:
        return False

    sentiment_value = analyzer.get_sentiment(title + "\n" + selftext)
    updated_timestamp = int(time.time())

    updated_object = {
        'id': submission_data['id'],
        'hash_check': hash_check,
        'updated_timestamp': updated_timestamp,
        'sentiment_value': sentiment_value
    }

    if existing_object:
        collection.update_one({'id': submission_data['id']}, {'$set': updated_object})
    else:
        collection.insert_one(updated_object)
    return True


def fetch_new_submissions(subreddit_name, analyzer, limit):
    """
    This is the main function that fetches new submissions from a specified subreddit using the Reddit API.
    It creates connections to the MongoDB database using the MongoDBClient class. It retrieves the submissions
    from the subreddit, iterates over each submission, process and update database with corresponding function.

    Args:
        subreddit_name (str): The name of the subreddit to fetch submissions from.
        analyzer (SentimentAnalyzer): The sentiment analyzer object.
        limit (int): The maximum number of submissions to fetch.

    Returns:
        None
    """
    # Access the database
    client = MongoDBClient()
    database = client.database
    submissions_collection = database['submissions']
    submission_scores_collection = database['submission_scores']
    submission_sentiments_collection = database['submission_sentiments']

    reddit = create_reddit_instance()
    subreddit = reddit.subreddit(subreddit_name)
    submissions = subreddit.new(limit=limit)

    new_post_count = 0
    updated_post_score_count = 0
    updated_sentiment_count = 0

    logging.info(f"Fetched posts from praw")
    for submission in submissions:
        submission_data = {
            'id': submission.id,
            'subreddit': subreddit_name,
            'title': submission.title,
            'hide_score': submission.hide_score,
            'created': submission.created,
            'author_fullname': getattr(submission, 'author_fullname', None),
            'selftext': getattr(submission, 'selftext', None),
            'post_hint': getattr(submission, 'post_hint', None),
            'url': getattr(submission, 'permalink', None),
            'selftext_length': len(submission.selftext) if submission.selftext else 0,
            'title_length': len(submission.title) if submission.title else 0
        }

        # Update sentiment_values (should be done first or selftext will be removed)
        if update_sentiment_values(submission_sentiments_collection, analyzer, submission_data):
            updated_sentiment_count += 1

        # Update post value
        if update_submission(submissions_collection, submission_data):
            new_post_count += 1

        # Prepare submission_score_data dictionary
        submission_score_data = {
            'id': submission.id,
            'timestamp': int(time.time()),
            'upvote_ratio': submission.upvote_ratio,
            'ups': submission.ups,
            'score': submission.score,
            'num_comments': submission.num_comments
        }

        # Update the submission_scores collection
        if update_submission_scores(submission_scores_collection, submission_score_data):
            updated_post_score_count += 1

    logging.info(f"New posts added: {new_post_count}; Updated post score: {updated_post_score_count}; Sentiment Value "
                 f"updated: {updated_sentiment_count}")
    client.close_connection()


if __name__ == '__main__':
    logging.info("Starting fetch_new_submissions...")
    _analyzer = SentimentAnalyzer()
    fetch_new_submissions('bitcoin', _analyzer, 200)
