import json
import os

from pymongo import MongoClient


class MongoDBClient:
    def __init__(self, path='mongo-credential.json'):
        credential_file = os.environ.get('CREDENTIAL_FILE')
        if credential_file and len(credential_file) > 0:
            path = credential_file
        abs_path = os.environ.get('SOURCE_DIR') + "/resources/" + path

        self.database_name, self.connection_string = MongoDBClient.get_mongo_connection_string(abs_path)
        self.client = MongoClient(self.connection_string)
        self.database = self.client[self.database_name]

    @staticmethod
    def get_mongo_connection_string(abs_path):
        # Read the credentials from the file
        with open(abs_path) as json_file:
            credentials = json.load(json_file)

        # Extract the credential values
        host = credentials['host']
        port = credentials['port']
        username = credentials['username']
        password = credentials['password']
        database = credentials['database']

        return database, f'mongodb://{username}:{password}@{host}:{port}/{database}?authSource=admin'

    def close_connection(self):
        self.client.close()

