# Reddit Analyzer

Reddit Analyzer is a tool that crawls Reddit data, performs sentiment analysis, and visualizes the sentiment scores on a web-based chart. It uses the PRAW library for crawling Reddit, the NLTK library for sentiment analysis using VADER (Valence Aware Dictionary and sEntiment Reasoner), Spark for data aggregation and Flask for the web server.

## Demo

Check out the live demo of Reddit Analyzer: [Demo Link](https://reddit.ikuhi.com/)

## System Diagram

![System Diagram](http://reddit.ikuhi.com/.public/reddit-analyzer/RedditAnalyzer_trans.png)

(1) The data fetching component retrieves new posts from a specified subreddit using the Reddit PRAW library.

(2) The component updates post scores and calculates sentiment values for each post.

(3) The updated data is stored within the MongoDB database.

(4) The analysis component utilizes the Apache Spark framework to analyze the fetched post data. It establishes a connection to the MongoDB database and retrieves the posts. The component performs sentiment analysis by grouping the submissions based on time (e.g., hourly) and subreddit. It calculates the sum of sentiment scores for each group and writes the analyzed results back to the MongoDB database.

(5) The web server component is implemented using the Flask framework. It provides routes for different endpoints, such as displaying charts and submission details. The routes interact with the MongoDB database to retrieve the necessary data and pass it to the corresponding HTML templates for rendering.

[Slide](https://docs.google.com/presentation/d/17lG2dDLDoovDo2uMZcyHC-xHwkkPQ48E5lBV0djGDTc/edit?usp=sharing) in Vietnamese

## Usage

To use Reddit Analyzer, you'll need to follow these steps:

1. Configure the Reddit API credentials in the `resources/praw-credential.json` file. Make sure to provide your Reddit username, password, client ID, and client secret. You can obtain the client ID and client secret by creating a Reddit application on the Reddit website.
Example:
```
{
  "client_id": "xxxxxx",
  "client_secret": "xxxxxx",
  "user_agent": "python/praw:CryptoTrending:v1.0 (by /u/huuhoangcu)"
}
```
2. Configure the MongoDB credentials in the `resources/mongo-credential.json` file.
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

3. Start the airflow in docker-compose to start DAG to crawl Reddit submissions. It also perform sentiment analysis on the crawled data. Sentiment analysis will be applied to the crawled submissions, and the results will be stored in the MongoDB database. Another DAG to do spark analysis on submissions data.
```
python src/submissions_main.py
```
Or build docker image for crawler and run
```
# build airflow image
scripts/docker/airflow/build.sh
# to start airflow resources/mongo-docker-compose-credential.json should exist
scripts/docker/airflow/docker-compose_start.sh
# to stop
scripts/docker/airflow/docker-compose_stop.sh
# then go to localhost:8080 to start DAG
```

4. Start the Flask server to visualize the sentiment scores:
```
scripts/docker/server/run_local.sh
```
Or build docker image for server and run
```
# resources/mongo-docker-credential.json should exist
scripts/docker/server/build_image.sh
scripts/docker/server/run_image.sh
```
The Flask server will serve a web page at `http://localhost:8077/` where you can see a chart visualizing the sentiment scores by subreddit.

5. Initiate collection index with
```
scripts/mongo/setup_index.sh
```

6. (Optional) To have a Slack notification for crawl monitor, we can create a file resources/slack-credential.json with content:
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
