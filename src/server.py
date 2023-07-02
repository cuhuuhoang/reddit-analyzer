from datetime import datetime

from flask import Flask, render_template

from mongodb_client import MongoDBClient

app = Flask(__name__)

# MongoDB connection
client = MongoDBClient()
database = client.database
collection = database['analyzed_by_created_days']


@app.route('/chart')
def chart():
    # Retrieve and process the data from the collection
    data = collection.find({}, {'_id': 0, 'timestamp': 1, 'subreddit': 1, 'sum_sentiment_score': 1})\
        .sort('timestamp', 1)
    chart_data = {}

    for item in data:
        timestamp = item['timestamp']
        subreddit = item['subreddit']
        sum_sentiment_score = item['sum_sentiment_score']
        formatted_timestamp = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")

        if subreddit not in chart_data:
            chart_data[subreddit] = []

        chart_data[subreddit].append({
            'timestamp': formatted_timestamp,
            'sum_sentiment_score': sum_sentiment_score
        })

    return render_template('chart.html', chart_data=chart_data)


if __name__ == '__main__':
    app.run(port=8077)
