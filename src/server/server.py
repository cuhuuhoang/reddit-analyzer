from datetime import datetime, timedelta
from math import log
from urllib.parse import urlparse

from flask import Flask, render_template, redirect, request

from src.core.mongodb_client import MongoDBClient
from src.core.system_config import Config

app = Flask(__name__)

# MongoDB connection
client = MongoDBClient()
database = client.database


def get_chart_data(collection_name, time_range, time_formats, chart_type):
    """
    This function retrieves and processes filtered data from a specified MongoDB collection.
    It filters the data based on the given time range and organizes it to be used for generating charts.
    It returns the rendered template for displaying the chart.

    Args:
        collection_name (str): The name of the collection in the database.
        time_range (tuple): A tuple containing the start and end timestamps for filtering the data.
        time_formats (dict): A dictionary containing the time unit and display formats for the chart.
        chart_type (str): The type of chart (e.g., 'day' or 'hour').

    Returns:
        A rendered template with the chart data.
    """
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

    default_subreddit = Config.get().default_subreddit()

    return render_template('chart.html', chart_data=chart_data, time_formats=time_formats,
                           default_subreddit=default_subreddit, chart_type=chart_type)


@app.route('/')
def root():
    """
    Redirects the root URL to the '/chart/day' route.
    """
    return redirect('/chart/day')


@app.route('/chart/day')
def chart_day():
    """
    This function is the route handler for "/chart/day". It calculates the date range for filtering data from the
    last 30 days and calls the get_chart_data() function to retrieve and process the data for generating a daily chart.
    It returns the rendered template for displaying the chart.

    Returns:
        The rendered chart template for the 'day' chart.
    """
    display_day = Config.get().display_day()
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    last_month = today - timedelta(days=display_day)

    time_formats = {
        'unit': 'day',
        'displayFormats': {
            'day': 'YYYY-MM-DD'
        }
    }

    return get_chart_data('analyzed_by_created_days', (last_month, today), time_formats, 'day')


@app.route('/chart/hour')
def chart_hour():
    """
    This function is the route handler for "/chart/hour". It calculates the date range for filtering data
    from the last 24 hours and calls the get_chart_data() function to retrieve and process the data for
    generating an hourly chart. It returns the rendered template for displaying the chart.

    Returns:
        The rendered chart template for the 'hour' chart.
    """
    display_hour = Config.get().display_hour()
    now = datetime.now()
    last_24_hours = now - timedelta(hours=display_hour)
    current_hour = now.replace(minute=0, second=0, microsecond=0)

    time_formats = {
        'unit': 'hour',
        'displayFormats': {
            'hour': 'YYYY-MM-DD_HH'
        }
    }

    return get_chart_data('analyzed_by_created_hours', (last_24_hours, current_hour), time_formats, 'hour')


def timestamp_to_datetime(timestamp):
    """
    Converts a timestamp to a datetime object.

    Args:
        timestamp (int): The timestamp to convert.

    Returns:
        A datetime object corresponding to the timestamp.
    """
    return datetime.fromtimestamp(timestamp)


@app.route('/details')
def details():
    """
    This function is the route handler for "/details". It retrieves detailed information about submissions within
    a specific time range and subreddit. It retrieves data from the "submissions", "submission_scores", and
    "submission_sentiments" collections in the MongoDB database and processes the data to compute composite sentiment,
    absolute sentiment, and effect. The result is passed to the "details.html" template for rendering.

    Returns:
        The rendered template with the submission details.
    """
    chart_type = request.args.get('type')
    subreddit = request.args.get('subreddit')
    timestamp = int(request.args.get('timestamp'))

    if chart_type == 'hour':
        start_timestamp = timestamp
        end_timestamp = timestamp + 3600
        chart_label = f"{chart_type.capitalize()} {timestamp_to_datetime(timestamp).strftime('%Y-%m-%d %Hh')}"
    elif chart_type == 'day':
        start_timestamp = timestamp
        end_timestamp = timestamp + 86400
        chart_label = f"{chart_type.capitalize()} {timestamp_to_datetime(timestamp).strftime('%Y-%m-%d')}"
    else:
        return 'Invalid chart type'

    submissions = database['submissions'].find({
        'created': {'$gte': start_timestamp, '$lt': end_timestamp},
        'subreddit': subreddit
    })

    result = []

    for submission in submissions:
        submission_id = submission['id']
        subreddit = submission['subreddit']
        created = timestamp_to_datetime(submission['created']).strftime('%Y-%m-%d %H:%M:%S')
        url = submission['url']
        selftext_length = submission['selftext_length']

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

        submission_sentiments = database['submission_sentiments'].find_one({'id': submission_id})
        if submission_sentiments:
            sentiment_value = round(submission_sentiments['sentiment_value'], 3)
        else:
            sentiment_value = 'N/A'

        try:
            composite_sentiment = sentiment_value * log(score)
        except (ValueError, ZeroDivisionError, TypeError):
            composite_sentiment = 0
        abs_sentiment = round(abs(composite_sentiment), 2)
        effect = 'positive' if composite_sentiment >= 0 else 'negative'

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

    title = f"Details for {chart_label} of {subreddit}"

    return render_template('details.html', result=result, title=title)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8077)