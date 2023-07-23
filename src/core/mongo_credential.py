import json
import os


class MongoCredential:
    def __init__(self, _connection_string, _database_name):
        self._connection_string = _connection_string
        self._database_name = _database_name

    def connection_string(self):
        return self._connection_string

    def database_name(self):
        return self._database_name

    @staticmethod
    def read_from_env():
        credential_path = os.environ.get('CREDENTIAL_PATH')
        if not credential_path:
            raise ValueError("Environment variable 'CREDENTIAL_PATH' not set.")

        with open(credential_path, 'r') as file:
            data = json.load(file)

        connection_string = data.get('connection_string')
        database_name = data.get('database_name')

        if not connection_string or not database_name:
            raise ValueError("Invalid JSON data. 'connection_string' and 'database_name' are required.")

        return MongoCredential(connection_string, database_name)
