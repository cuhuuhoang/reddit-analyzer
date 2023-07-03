# Reddit Analyzer

Reddit Analyzer is a tool that crawls Reddit data, performs sentiment analysis, and visualizes the sentiment scores on a web-based chart. It uses the PRAW library for crawling Reddit, the NLTK library for sentiment analysis using VADER (Valence Aware Dictionary and sEntiment Reasoner), Spark for data aggregation and Flask for the web server.

## Demo

Check out the live demo of Reddit Analyzer: [Demo Link](https://reddit.ikuhi.com/)

## System Diagram

![System Diagram](http://reddit.ikuhi.com/.public/reddit-analyzer/RedditAnalyzer.png)

The system consists of three main components: the data fetching component, the analysis component, and the web server component.

The data fetching component retrieves new submissions from a specified subreddit using the Reddit API. It interacts with the API using the PRAW library and updates the submission information in a MongoDB collection. The component also updates submission scores and calculates sentiment values for each submission using a SentimentAnalyzer object. The updated data is stored in separate collections within the MongoDB database.

The analysis component utilizes the Apache Spark framework to analyze the fetched submission data. It establishes a connection to the MongoDB database and retrieves the submissions. The component performs sentiment analysis by grouping the submissions based on time (e.g., hourly) and subreddit. It calculates the sum of sentiment scores for each group and writes the analyzed results back to the MongoDB database.

The web server component is implemented using the Flask framework. It provides routes for different endpoints, such as displaying charts and submission details. The routes interact with the MongoDB database to retrieve the necessary data and pass it to the corresponding HTML templates for rendering. The web server component handles requests from clients and serves the generated charts and submission details through the specified routes.

Overall, the system's structure involves a data fetching component that retrieves and stores new submissions, an analysis component that performs sentiment analysis on the fetched data, and a web server component that serves the analyzed results and visualizations to clients through various routes. The MongoDB database acts as the central repository for storing the submissions, analysis results, and other related data.

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

7. (Optional) To have a Slack notification for crawl monitor, we can create a file resources/slack-credential.json with content:
```
{
    "hook_url": "https://hooks.slack.com/services/XXXXXX/xxxx/xxxxxx"
}
```

## Dependencies

- [PRAW](https://praw.readthedocs.io/en/stable/): Python Reddit API Wrapper for crawling Reddit data.
- [MongoDB](https://www.mongodb.com/docs/manual/core/document/): NoSQL database for storing the crawled Reddit data and sentiment analysis results.
- [NLTK](https://www.nltk.org/_modules/nltk/sentiment/vader.html): Natural Language Toolkit for sentiment analysis using VADER (Valence Aware Dictionary and sEntiment Reasoner).
- [Spark](https://spark.apache.org/docs/latest/index.html): Distributed computing framework for data aggregation.
- [Flask](https://flask.palletsprojects.com/en/2.3.x/): Web framework for serving the sentiment analysis results.

## License

This project is licensed under the `MIT License`.

If you have any further questions or need assistance, feel free to reach out to me at cuhuuhoang@gmail.com. I'll be happy to help!
