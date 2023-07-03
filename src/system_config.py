import json


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
            with open("resources/system-config.json") as json_file:
                Config._config = json.load(json_file)

    def subreddit_list(self):
        return Config._config["subreddit_list"]

    def default_subreddit(self):
        return Config._config["default_subreddit"]

    def display_day(self):
        return Config._config["display_day"]

    def display_hour(self):
        return Config._config["display_hour"]

    def check_crawl_interval(self):
        return Config._config["check_crawl_interval"]
