# Reddit Analyzer

Reddit Analyzer is a tool that crawls Reddit data, performs sentiment analysis, and visualizes the sentiment scores on a web-based chart. It uses the PRAW library for crawling Reddit, the NLTK library for sentiment analysis using VADER (Valence Aware Dictionary and sEntiment Reasoner), and Flask for the web server.

## Demo

Check out the live demo of Reddit Analyzer: [Demo Link](https://reddit.ikuhi.com/)

## Usage

To use Reddit Analyzer, you'll need to follow these steps:

1. Install the required dependencies by running:
```
pip install -r requirements.txt
```

2. Configure the Reddit API credentials in the `resources/praw-credential.json` file. Make sure to provide your Reddit username, password, client ID, and client secret. You can obtain the client ID and client secret by creating a Reddit application on the Reddit website.
Example:
```
{
  "client_id": "xxxxxx",
  "client_secret": "xxxxxx",
  "user_agent": "python/praw:CryptoTrending:v1.0 (by /u/huuhoangcu)"
}
```
3. Configure the MongoDB credentials in the `resources/mongo-credential.json` file.
Example:
```
{
  "host": "localhost",
  "port": "27017",
  "username": "root",
  "password": "dbpw11",
  "database": "reddit_analyzer"
}
```

4. Start the data crawler to fetch Reddit submissions. It also perform sentiment analysis on the crawled data. Sentiment analysis will be applied to the crawled submissions, and the results will be stored in the MongoDB database.
```
python src/submissions_main.py
```
Or build docker image for crawler and run
```
# resources/mongo-docker-credential.json should exist
scripts/docker/crawler/build.sh docker
scripts/docker/crawler/run.sh
```

5. Start the Flask server to visualize the sentiment scores:
```
python src/server.py
```
Or build docker image for server and run
```
# resources/mongo-docker-credential.json should exist
scripts/docker/server/build.sh docker
scripts/docker/server/run.sh
```
The Flask server will serve a web page at `http://localhost:8077/` where you can see a chart visualizing the sentiment scores by subreddit.

6. Initiate collection index with
```
python src/setup_index.py resources/mongo-docker-credential.json
```

## Dependencies

- [PRAW](https://praw.readthedocs.io/en/stable/): Python Reddit API Wrapper for crawling Reddit data.
- [NLTK](https://www.nltk.org/_modules/nltk/sentiment/vader.html): Natural Language Toolkit for sentiment analysis using VADER (Valence Aware Dictionary and sEntiment Reasoner).
- [Flask](https://flask.palletsprojects.com/en/2.3.x/): Web framework for serving the sentiment analysis results.

## License

This project is licensed under the `MIT License`.

If you have any further questions or need assistance, feel free to reach out to me at cuhuuhoang@gmail.com. I'll be happy to help!
