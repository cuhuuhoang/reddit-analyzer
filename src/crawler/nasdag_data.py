from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

url = 'https://www.investing.com/indices/nasdaq-composite-historical-data'
response = requests.get(url)
html_content = response.text

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Find all rows ('tr') in the table body
rows = soup.find_all('tr', class_='datatable_row__Hk3IV')

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

    print(f"Date: {timestamp}, Value: {value_numeric}")
