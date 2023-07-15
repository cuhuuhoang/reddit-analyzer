import json
import os

import praw


def read_credentials_from_file(credentials_file):
    with open(credentials_file) as json_file:
        credentials = json.load(json_file)
    return credentials


def create_reddit_instance(credentials=None):
    if credentials is None:
        abs_path = os.environ.get('SOURCE_DIR') + "/resources/praw-credential.json"
        credentials = read_credentials_from_file(abs_path)

    return praw.Reddit(
        client_id=credentials['client_id'],
        client_secret=credentials['client_secret'],
        user_agent=credentials['user_agent']
    )
