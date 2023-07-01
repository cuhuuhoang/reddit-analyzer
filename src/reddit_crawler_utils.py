import json
import praw


def read_credentials_from_file(credentials_file):
    with open(credentials_file) as json_file:
        credentials = json.load(json_file)
    return credentials


def create_reddit_instance(credentials=None):
    if credentials is None:
        credentials = read_credentials_from_file('resources/praw-credential.json')

    return praw.Reddit(
        client_id=credentials['client_id'],
        client_secret=credentials['client_secret'],
        user_agent=credentials['user_agent']
    )
