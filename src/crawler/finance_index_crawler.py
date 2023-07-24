import sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

from src.core.mongo_connection import MongoConnection
from src.core.mongo_credential import MongoCredential


class FinanceIndexCrawler:
    def __init__(self, _mongo_credential):
        self.connection = MongoConnection(_mongo_credential)
        self.database = self.connection.database

    def close_connection(self):
        self.connection.close_connection()

    def upsert_data(self, data_list):
        finance_index_collection = self.database['finance_indexes']
        for data in data_list:
            # Check if a document with the same timestamp and name exists
            filter_query = {"timestamp": data["timestamp"], "name": data["name"]}
            update_data = {"$set": {"value": data["value"]}}
            finance_index_collection.update_one(filter_query, update_data, upsert=True)

    def fetch_nasdaq_data(self):
        url = 'https://www.investing.com/indices/nasdaq-composite-historical-data'
        response = requests.get(url)
        html_content = response.text

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all rows ('tr') in the table body
        rows = soup.find_all('tr', class_='datatable_row__Hk3IV')

        data_list = []
        # Loop through each row and extract the datetime and the corresponding value
        for row in rows:
            # Check if the row is for time display
            if not row.find('time'):
                continue

            # Find the first 'td' child and extract the datetime
            datetime_element = row.select('td:nth-child(1)')[0]
            date_str = datetime_element.text.strip()

            # Convert the date to a Unix timestamp
            date = datetime.strptime(date_str, '%m/%d/%Y')

            # Setting the time components to 0 to represent 00:00:00.
            date = date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

            # Converting the "date" object to a Unix timestamp (number of seconds since 1970-01-01 00:00:00 UTC).
            timestamp = int(date.timestamp())

            # Find the second 'td' child and extract the value
            value_element = row.select('td:nth-child(2)')[0]
            value = value_element.text.strip()
            value_numeric = float(value.replace(",", ""))

            data_list.append({"timestamp": timestamp, "value": value_numeric, "name": "nasdaq"})

        # Call the upsert function to insert or update data in the collection
        self.upsert_data(data_list)

    def fetch_bitcoin_data(self):
        url = 'https://www.investing.com/crypto/bitcoin/historical-data'
        # Send a request to the website and get the content
        response = requests.get(url)
        html_content = response.text

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all rows ('tr') in the table body
        rows = soup.select('#results_box table tbody tr')

        data_list = []
        # Loop through each row and extract the date and price values
        for row in rows:
            # Find the first 'td' child and extract the date and its 'data-real-value' attribute
            date_element = row.select('td:nth-child(1)')[0]
            date = date_element.get('data-real-value')

            # Find the second 'td' child and extract the price and its 'data-real-value' attribute
            price_element = row.select('td:nth-child(2)')[0]
            value = price_element.get('data-real-value')

            if date and value:
                value_numeric = float(value.replace(",", ""))
                data_list.append({"timestamp": int(float(date)), "value": value_numeric, "name": "bitcoin"})

        # Call the upsert function to insert or update data in the collection
        self.upsert_data(data_list)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python finance_index_crawler.py <connection_string> <database_name>")
        sys.exit(1)

    connection_string = sys.argv[1]
    database_name = sys.argv[2]

    mongo_credential = MongoCredential(connection_string, database_name)

    crawler = FinanceIndexCrawler(mongo_credential)

    crawler.fetch_nasdaq_data()
    crawler.fetch_bitcoin_data()

    # Close the MongoDB connection
    crawler.close_connection()
