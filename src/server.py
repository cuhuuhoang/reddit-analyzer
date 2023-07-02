from datetime import datetime, timedelta
from math import log
from urllib.parse import urlparse

from flask import Flask, render_template, redirect, request

from mongodb_client import MongoDBClient

app = Flask(__name__)

# MongoDB connection
client = MongoDBClient()
database = client.database

default_subreddit = ['bitcoin', 'wallstreetbets']


def get_chart_data(collection_name, time_range, time_formats, chart_type):
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
                           default_subreddit=default_subreddit, chart_type=chart_type)


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

    return get_chart_data('analyzed_by_created_days', (last_month, today), time_formats, 'day')


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

    return get_chart_data('analyzed_by_created_hours', (last_24_hours, current_hour), time_formats, 'hour')


@app.route('/details')
def details():
    chart_type = request.args.get('type')
    subreddit = request.args.get('subreddit')
    timestamp = int(request.args.get('timestamp'))

    if chart_type == 'hour':
        start_timestamp = timestamp
        end_timestamp = timestamp + 3600  # Add 1 hour (3600 seconds) to the start timestamp
    elif chart_type == 'day':
        start_timestamp = timestamp
        end_timestamp = timestamp + 86400  # Add 1 day (86400 seconds) to the start timestamp
    else:
        # Handle invalid chart type
        return 'Invalid chart type'

    # Retrieve submissions within the specified time range and subreddit
    submissions = database['submissions'].find({
        'created': {'$gte': start_timestamp, '$lt': end_timestamp},
        'subreddit': subreddit
    })

    # Prepare a list to store the result
    result = []

    for submission in submissions:
        submission_id = submission['id']
        subreddit = submission['subreddit']
        created = datetime.utcfromtimestamp(submission['created']).strftime('%Y-%m-%d %H:%M:%S')
        url = submission['url']
        selftext_length = submission['selftext_length']

        # Retrieve submission scores
        submission_scores = database['submission_scores'].find_one({'id': submission_id})
        if submission_scores:
            upvote_ratio = submission_scores['upvote_ratio']
            ups = submission_scores['ups']
            score = submission_scores['score']
            num_comments = submission_scores['num_comments']
        else:
            upvote_ratio = 'N/A'
            ups = 'N/A'
            score = 'N/A'
            num_comments = 'N/A'

        # Retrieve submission sentiments
        submission_sentiments = database['submission_sentiments'].find_one({'id': submission_id})
        if submission_sentiments:
            sentiment_value = round(submission_sentiments['sentiment_value'], 3)
        else:
            sentiment_value = 'N/A'

        # Compute composite sentiment, absolute sentiment, and effect
        try:
            composite_sentiment = sentiment_value * log(score)
        except (ValueError, ZeroDivisionError, TypeError):
            composite_sentiment = 0
        abs_sentiment = round(abs(composite_sentiment), 2)
        effect = 'positive' if composite_sentiment >= 0 else 'negative'

        # Generate slug
        url = 'https://www.reddit.com' + url
        parsed_url = urlparse(url)
        slug = parsed_url.path.strip('/').split('/')[-1]

        result.append({
            'id': submission_id,
            'subreddit': subreddit,
            'created': created,
            'url': url,
            'slug': slug,
            'selftext_length': selftext_length,
            'upvote_ratio': upvote_ratio,
            'ups': ups,
            'score': score,
            'num_comments': num_comments,
            'sentiment_value': sentiment_value,
            'composite_sentiment': composite_sentiment,
            'abs_sentiment': abs_sentiment,
            'effect': effect
        })

    return render_template('details.html', result=result)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8077)
