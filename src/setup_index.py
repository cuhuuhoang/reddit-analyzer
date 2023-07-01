import sys

from mongodb_utils import get_mongo_database


def setup_index(path):
    # Access the database
    database = get_mongo_database(path)
    collection = database['submissions']
    # Create an index for the 'id' field
    index_info = collection.index_information()
    if 'id_1' not in index_info:
        collection.create_index('id', unique=True)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        first_argument = sys.argv[1]
        print("First argument:", first_argument)
        setup_index(first_argument)
