from logging_config import *
from mongodb_utils import get_mongo_database
from reddit_crawler_utils import create_reddit_instance


def fetch_new_submissions(subreddit_name, limit):
    # Access the database
    database = get_mongo_database()
    collection = database['submissions']

    reddit = create_reddit_instance()
    subreddit = reddit.subreddit(subreddit_name)
    submissions = subreddit.new(limit=limit)

    new_post_count = 0

    for submission in submissions:
        # Check if the submission already exists in the database
        existing_submission = collection.find_one({'id': submission.id})
        if existing_submission is None:
            submission_data = {
                'subreddit': subreddit_name,
                'author_fullname': submission.author_fullname,
                'title': submission.title,
                'hide_score': submission.hide_score,
                'name': submission.name,
                'upvote_ratio': submission.upvote_ratio,
                'ups': submission.ups,
                'score': submission.score,
                'created': submission.created,
                'domain': submission.domain,
                'id': submission.id,
                'is_robot_indexable': submission.is_robot_indexable,
                'num_comments': submission.num_comments,
                'send_replies': submission.send_replies,
                'permalink': submission.permalink,
                'url_overridden_by_dest': getattr(submission, 'url_overridden_by_dest', None),
                'selftext': getattr(submission, 'selftext', None),
                'post_hint': getattr(submission, 'post_hint', None),
                'link_flair_type': getattr(submission, 'link_flair_type', None),
                'author_flair_type': getattr(submission, 'author_flair_type', None),
            }
            # Insert the new submission into the database
            collection.insert_one(submission_data)
            new_post_count += 1

    logging.info(f"New posts added: {new_post_count}")


if __name__ == '__main__':
    logging.info("Starting fetch_new_submissions...")
    fetch_new_submissions('bitcoin', 200)
