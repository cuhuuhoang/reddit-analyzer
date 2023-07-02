import json
from pymongo import MongoClient


class MongoDBClient:
    def __init__(self, path='resources/mongo-credential.json'):
        self.database_name, self.connection_string = MongoDBClient.get_mongo_connection_string(path)
        self.client = MongoClient(self.connection_string)
        self.database = self.client[self.database_name]

    @staticmethod
    def get_mongo_connection_string(path='resources/mongo-credential.json'):
        # Read the credentials from the file
        with open(path) as json_file:
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

