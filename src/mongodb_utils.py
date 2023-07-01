import json

from pymongo import MongoClient


def get_mongo_database(path='resources/mongo-credential.json'):
    # Read the credentials from the file
    with open(path) as json_file:
        credentials = json.load(json_file)

    if 'connection_string' in credentials:
        connection_string = credentials['connection_string']
        client = MongoClient(connection_string)
        return client.get_default_database()

    # Extract the credential values
    host = credentials['host']
    port = credentials['port']
    username = credentials['username']
    password = credentials['password']
    database = credentials['database']

    # Create a MongoClient instance
    client = MongoClient(f'mongodb://{username}:{password}@{host}:{port}/{database}?authSource=admin')
    database_client = client[database]
    return database_client
