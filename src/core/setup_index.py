import pymongo

from src.core.mongo_connection import MongoConnection


class IndexCreator:
    def __init__(self, mongo_credential):
        self.connection = MongoConnection(mongo_credential)
        self.database = self.connection.database

    def setup_index(self):
        # collection submissions
        collection_submissions = self.database['submissions']
        index_info = collection_submissions.index_information()
        if 'id_1' not in index_info:
            collection_submissions.create_index('id', unique=True)

        # collection submission_scores
        collection_submission_scores = self.database['submission_scores']
        index_info = collection_submission_scores.index_information()
        if 'id_1' not in index_info:
            collection_submission_scores.create_index('id', unique=True)

        # collection submission_scores
        submission_sentiments_collection = self.database['submission_sentiments']
        index_info = submission_sentiments_collection.index_information()
        if 'id_1' not in index_info:
            submission_sentiments_collection.create_index('id', unique=True)

        # collection analyzed_by_created_hours
        analyzed_by_created_hours_collection = self.database['analyzed_by_created_hours']
        index_exists = False
        for index_name, index_key in index_info.items():
            if (
                    "timestamp" in index_key["key"]
                    and "subreddit" in index_key["key"]
                    and index_key["unique"] is False
            ):
                index_exists = True
                break

        # Create the index only if it doesn't exist
        if not index_exists:
            analyzed_by_created_hours_collection.create_index([
                ("timestamp", pymongo.ASCENDING),
                ("subreddit", pymongo.ASCENDING)
            ])

        # collection analyzed_by_created_days
        analyzed_by_created_days_collection = self.database['analyzed_by_created_days']
        index_exists = False

        # Check if the index already exists
        for index_name, index_key in analyzed_by_created_days_collection.index_information().items():
            if (
                    "timestamp" in index_key["key"]
                    and "subreddit" in index_key["key"]
                    and index_key["unique"] is False
            ):
                index_exists = True
                break

        # Create the index if it doesn't exist
        if not index_exists:
            analyzed_by_created_days_collection.create_index([
                ("timestamp", pymongo.ASCENDING),
                ("subreddit", pymongo.ASCENDING)
            ])

        # close
        self.connection.close_connection()

        print("Finish creating index")
