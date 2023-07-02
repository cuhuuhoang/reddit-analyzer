from datetime import datetime, timedelta
from flask import Flask, render_template, redirect

from mongodb_client import MongoDBClient

app = Flask(__name__)

# MongoDB connection
client = MongoDBClient()
database = client.database

default_subreddit = ['bitcoin', 'wallstreetbets']


def get_chart_data(collection_name, time_range, time_formats):
    # Retrieve and process the filtered data from the collection
    collection = database[collection_name]
    data = collection.find({
        'timestamp': {
            '$gte': int(time_range[0].timestamp()),
            '$lt': int(time_range[1].timestamp())
        }
    }, {'_id': 0, 'timestamp': 1, 'subreddit': 1, 'sum_sentiment_score': 1}).sort('timestamp', 1)

    chart_data = {}

    for item in data:
        timestamp = item['timestamp']
        subreddit = item['subreddit']
        sum_sentiment_score = item['sum_sentiment_score']

        if subreddit not in chart_data:
            chart_data[subreddit] = []

        chart_data[subreddit].append({
            'timestamp': timestamp,
            'sum_sentiment_score': sum_sentiment_score
        })

    return render_template('chart.html', chart_data=chart_data, time_formats=time_formats,
                           default_subreddit=default_subreddit)


@app.route('/')
def root():
    return redirect('/chart/day')


@app.route('/chart/day')
def chart_day():
    # Calculate the date range for filtering
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    last_month = today - timedelta(days=30)

    time_formats = {
        'unit': 'day',
        'displayFormats': {
            'day': 'YYYY-MM-DD'
        }
    }

    return get_chart_data('analyzed_by_created_days', (last_month, today), time_formats)


@app.route('/chart/hour')
def chart_hour():
    # Calculate the date range for filtering
    now = datetime.now()
    last_24_hours = now - timedelta(hours=24)
    current_hour = now.replace(minute=0, second=0, microsecond=0)

    time_formats = {
        'unit': 'hour',
        'displayFormats': {
            'hour': 'YYYY-MM-DD_HH'
        }
    }

    return get_chart_data('analyzed_by_created_hours', (last_24_hours, current_hour), time_formats)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8077)
