import json
import os


class Config:
    _instance = None
    _config = None

    @classmethod
    def get(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if not Config._config:
            abs_path = os.environ.get('SOURCE_DIR') + '/resources/system-config.json'
            with open(abs_path) as json_file:
                Config._config = json.load(json_file)

    def default_subreddit(self):
        return Config._config["default_subreddit"]

    def display_day(self):
        return Config._config["display_day"]

    def display_hour(self):
        return Config._config["display_hour"]
