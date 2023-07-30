from datetime import datetime, timedelta
from math import log
from urllib.parse import urlparse

from flask import Flask, render_template, redirect, request

from src.core.mongo_connection import MongoConnection
from src.core.mongo_credential import MongoCredential
from src.core.system_config import Config

app = Flask(__name__)


# MongoDB connection
connection = MongoConnection(MongoCredential.read_from_env())
database = connection.database


def get_chart_data(collection_name, time_range, time_formats, chart_type):
    subreddit_data = list(database[collection_name].find({
        'timestamp': {
            '$gte': int(time_range[0].timestamp()),
            '$lt': int(time_range[1].timestamp())
        }
    }, {'_id': 0, 'timestamp': 1, 'subreddit': 1, 'sum_sentiment_score': 1, 'sum_sentiment_score_sma': 1}).sort('timestamp', 1))

    chart_data = {}

    for item in subreddit_data:
        timestamp = item['timestamp']
        subreddit = item['subreddit']
        sum_sentiment_score = item.get('sum_sentiment_score_sma', 0)

        if subreddit not in chart_data:
            chart_data[subreddit] = []

        chart_data[subreddit].append({
            'timestamp': timestamp,
            'sum_sentiment_score': sum_sentiment_score,
            'tooltip': round(sum_sentiment_score, 2)
        })

    if chart_type == 'day':
        for name in ['nasdaq', 'bitcoin']:
            finance_indexes_data = list(database['finance_indexes'].find({
                'timestamp': {
                    '$gte': int(time_range[0].timestamp()),
                    '$lt': int(time_range[1].timestamp())
                },
                'name': name
            }, {'_id': 0, 'timestamp': 1, 'name': 1, 'value': 1}).sort('timestamp', 1))

            finance_indexes_values = [item.get('value') for item in finance_indexes_data if
                                      item.get('value') is not None]
            min_finance_indexes_value, max_finance_indexes_value = min(finance_indexes_values), max(
                finance_indexes_values)

            key = name + '_index'
            if key not in chart_data:
                chart_data[key] = []

            for item in finance_indexes_data:
                timestamp = item['timestamp']
                value = item.get('value')

                if value is not None:
                    scaled_value = 10 * (value - min_finance_indexes_value) / (
                                max_finance_indexes_value - min_finance_indexes_value)
                    chart_data[key].append({
                        'timestamp': timestamp,
                        'sum_sentiment_score': scaled_value,
                        'tooltip': round(value, 2)
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
            'day': 'YYYY-MM-DD ddd'
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
