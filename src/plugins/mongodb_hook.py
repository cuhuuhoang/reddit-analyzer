from airflow.hooks.base import BaseHook

from src.core.mongo_credential import MongoCredential


class MongoDBHook:

    def __init__(self, conn_id):
        self.conn = BaseHook.get_connection(conn_id)

    def get_uri(self):
        return self.conn.get_uri().replace("mongo://", "mongodb://")

    def get_schema(self):
        return self.conn.schema

    def get_credential(self):
        return MongoCredential(self.get_uri(), self.get_schema())
