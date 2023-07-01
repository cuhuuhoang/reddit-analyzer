import hashlib
import time

from logging_config import *
from mongodb_utils import get_mongo_database
from reddit_crawler_utils import create_reddit_instance
from sentiment_analyzer import PARSER_KEY, SentimentAnalyzer


def update_submission(submission_collection, submission_data):
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
        # Get the last entry from the values array
        last_entry = existing_submission['values'][-1]

        # Check if any of the values have changed
        if (last_entry['upvote_ratio'] != submission_score_data['upvote_ratio'] or
                last_entry['ups'] != submission_score_data['ups'] or
                last_entry['score'] != submission_score_data['score'] or
                last_entry['num_comments'] != submission_score_data['num_comments']):
            # Append the new values to the values array
            existing_submission['values'].append(submission_score_data)

            # Update the submission in the collection
            collection.update_one(
                {'id': submission_id},
                {'$set': {'values': existing_submission['values']}}
            )

    else:
        # Create a new submission entry in the submission_scores collection
        new_submission = {
            'id': submission_id,
            'values': [submission_score_data]
        }

        # Insert the new submission into the collection
        collection.insert_one(new_submission)


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
    updated_timestamp = time.time()

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
    database = get_mongo_database()
    submissions_collection = database['submissions']
    submission_scores_collection = database['submission_scores']
    submission_sentiments_collection = database['submission_sentiments']

    reddit = create_reddit_instance()
    subreddit = reddit.subreddit(subreddit_name)
    submissions = subreddit.new(limit=limit)

    new_post_count = 0
    updated_sentiment_count = 0

    for submission in submissions:
        submission_data = {
            'id': submission.id,
            'subreddit': subreddit_name,
            'title': submission.title,
            'hide_score': submission.hide_score,
            'created': submission.created,
            'author_fullname': getattr(submission, 'author_fullname', None),
            'selftext': getattr(submission, 'selftext', None),
            'post_hint': getattr(submission, 'post_hint', None)
        }

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
        update_submission_scores(submission_scores_collection, submission_score_data)

        # Update sentiment_values
        if update_sentiment_values(submission_sentiments_collection, analyzer, submission_data):
            updated_sentiment_count += 1

    logging.info(f"New posts added: {new_post_count}; Sentiment Value updated: {updated_sentiment_count}")


if __name__ == '__main__':
    logging.info("Starting fetch_new_submissions...")
    _analyzer = SentimentAnalyzer()
    fetch_new_submissions('bitcoin', _analyzer, 200)
