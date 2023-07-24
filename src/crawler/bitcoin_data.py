import requests
from bs4 import BeautifulSoup

url = 'https://www.investing.com/crypto/bitcoin/historical-data'
# Send a request to the website and get the content
response = requests.get(url)
html_content = response.text

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Find all rows ('tr') in the table body
rows = soup.select('#results_box table tbody tr')

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
        print(f"Date: {date}, Price: {value_numeric}")
