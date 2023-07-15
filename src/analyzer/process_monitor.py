import json
import os
import traceback
from datetime import datetime, timedelta

import requests

from src.core.logging_config import *
from src.core.mongodb_client import MongoDBClient
from src.core.system_config import Config


class ProcessMonitor:
    """
    This class performs monitoring tasks and sends notifications via Slack for specific conditions.

    To have a Slack notification, we should create a file resources/slack-credential.json with content:
    {
        "hook_url": "https://hooks.slack.com/services/XXXXXX/xxxx/xxxxxx"
    }
    """
    def __init__(self, slack_credential_file='slack-credential.json'):
        """
        Constructor for ProcessMonitor class. Initializes the ProcessMonitor object and reads the Slack
        credential file to obtain the Slack hook URL. If the file is not found, it sets the `only_console`
        flag to `True`, indicating that only console notifications should be used.

        Args:
            slack_credential_file (str): The path to the Slack credential file.

        Returns:
            None
        """
        try:
            abs_path = os.environ.get('SOURCE_DIR') + '/resources/' + slack_credential_file
            with open(abs_path) as json_file:
                credentials = json.load(json_file)
                hook_url = credentials.get('hook_url')
                if hook_url:
                    self.slack_hook_url = hook_url
                    self.only_console = False
        except FileNotFoundError:
            logging.warning("Use only console for notify error")
            self.slack_hook_url = None
            self.only_console = True

    def notify_error(self, message):
        """
        Sends an error message to the logging system and, if applicable, sends a Slack notification.

        Args:
            message (str): The error message to be logged and notified.

        Returns:
            None
        """
        logging.error(message)
        if not self.only_console:
            payload = {
                'text': message
            }
            response = requests.post(self.slack_hook_url, json=payload)
            if response.status_code != 200:
                logging.error(f"Failed to send Slack message: {response.text}")

    def check_and_notify(self):
        """
        Performs monitoring tasks and sends notifications based on certain conditions. Initializes a MongoDB
        client and checks the last crawl check time from the database. If no previous check time is found,
        it inserts the current time as the initial check time. Otherwise, it performs the following checks:
        - It checks the max submission created timestamp from the `submissions` collection. If the timestamp
          is older than 1 hour, it sends an error notification.
        - It checks the max analyzed_by_created_days timestamp from the `analyzed_by_created_days`
          collection. If the timestamp is older than 30 hours, it sends an error notification.
        - It checks the max analyzed_by_created_hours timestamp from the `analyzed_by_created_hours`
          collection. If the timestamp is older than 2 hours, it sends an error notification.
        - After performing the checks, it updates the last crawl check time to the current time.

        If an exception occurs during the monitoring process, it catches the exception, closes the MongoDB
        connection (if it exists), sends an error notification, and prints the exception traceback.

        Returns:
            None
        """
        mongo_client = None
        try:
            mongo_client = MongoDBClient()

            # Check max submission created timestamp
            max_submission_created = mongo_client.database.submissions.find_one(
                projection=['created'],
                sort=[('created', -1)]
            )

            if not max_submission_created or datetime.fromtimestamp(max_submission_created['created']) < \
                    datetime.now() - timedelta(hours=1):
                # Notify if submissions are too old
                self.notify_error("No new posts. Submissions are too old.")

            # Check max analyzed_by_created_days timestamp
            max_analyzed_by_created_days = mongo_client.database.analyzed_by_created_days.find_one(
                projection=['timestamp'],
                sort=[('timestamp', -1)]
            )

            if not max_analyzed_by_created_days \
                    or datetime.fromtimestamp(max_analyzed_by_created_days['timestamp']) < \
                    datetime.now() - timedelta(hours=30):

                # Notify if analyzed_by_created_days is not updated for a long time
                self.notify_error("analyzed_by_created_days is not updated for a long time.")

            # Check max analyzed_by_created_hours timestamp
            max_analyzed_by_created_hours = mongo_client.database.analyzed_by_created_hours.find_one(
                projection=['timestamp'],
                sort=[('timestamp', -1)]
            )

            if not max_analyzed_by_created_hours \
                    or datetime.fromtimestamp(max_analyzed_by_created_hours['timestamp']) < \
                    datetime.now() - timedelta(hours=12):
                # Notify if analyzed_by_created_hours is not updated for a long time
                self.notify_error("analyzed_by_created_hours is not updated for a long time.")

        except Exception as e:
            if mongo_client is not None:
                mongo_client.close_connection()
            self.notify_error(f"An exception occurred when do monitor: {str(e)}")
            traceback.print_exc()


if __name__ == '__main__':
    monitor = ProcessMonitor()
    monitor.check_and_notify()
