import hashlib
import time

from logging_config import *
from reddit_crawler_utils import create_reddit_instance
from sentiment_analyzer import PARSER_KEY, SentimentAnalyzer
from mongodb_client import MongoDBClient


def update_submission(submission_collection, submission_data):
    # remove selftext for saving disk
    selftext = submission_data.get('selftext')
    submission_data['selftext_length'] = 0 if selftext is None else len(selftext)
    submission_data.pop('selftext')
    # remove title also
    title = submission_data.get('title')
    submission_data['title_length'] = 0 if title is None else len(title)
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
    if 'selftext' not in submission_data:
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

    logging.info(f"fetched posts from praw")
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
            'url': getattr(submission, 'url', None)
        }

        # Update sentiment_values (should be done first or selftext will be removed)
        if update_sentiment_values(submission_sentiments_collection, analyzer, submission_data):
            updated_sentiment_count += 1

        # update post value
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
