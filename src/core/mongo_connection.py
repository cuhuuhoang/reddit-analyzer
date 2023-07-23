from pymongo import MongoClient


class MongoConnection:
    def __init__(self, mongo_credential):
        self.connection_string = mongo_credential.connection_string()
        self.database_name = mongo_credential.database_name()
        self.client = MongoClient(self.connection_string)
        self.database = self.client[self.database_name]

    def close_connection(self):
        self.client.close()
