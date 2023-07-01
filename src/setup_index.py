import sys

from mongodb_utils import get_mongo_database


def setup_index(path):
    # Access the database
    database = get_mongo_database(path)

    # collection submissions
    collection_submissions = database['submissions']
    index_info = collection_submissions.index_information()
    if 'id_1' not in index_info:
        collection_submissions.create_index('id', unique=True)

    # collection submission_scores
    collection_submission_scores = database['submission_scores']
    index_info = collection_submission_scores.index_information()
    if 'id_1' not in index_info:
        collection_submission_scores.create_index('id', unique=True)

    # collection submission_scores
    submission_sentiments_collection = database['submission_sentiments']
    index_info = submission_sentiments_collection.index_information()
    if 'id_1' not in index_info:
        submission_sentiments_collection.create_index('id', unique=True)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        credential_path = sys.argv[1]
        print("Credential path:", credential_path)
        setup_index(credential_path)
