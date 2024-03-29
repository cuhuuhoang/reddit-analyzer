import sys
import time

from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import col, floor, log, when, avg, row_number, lag
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, BooleanType, DoubleType

from src.core.mongo_connection import MongoConnection
from src.core.mongo_credential import MongoCredential


class SparkAnalyzer:
    def __init__(self, _mongo_connection_string, _mongo_database_name):
        """
        Initializes the SparkAnalyzer class.

        It sets the necessary environment variables for Spark and MongoDB configurations,
        initializes a MongoDB client, and creates a SparkSession.

        Returns:
            None
        """

        self.connection = MongoConnection(MongoCredential(_mongo_connection_string, _mongo_database_name))
        self.spark = SparkSession.builder.appName('SubmissionAnalyzer').getOrCreate()

    def get_submissions_df(self):
        """
        Retrieves the submissions DataFrame from the 'submissions' collection.

        Returns:
            The submissions DataFrame.
        """
        # Define the schema for the 'submissions' collection
        submissions_schema = StructType([
            StructField("_id", StringType()),
            StructField("id", StringType()),
            StructField("subreddit", StringType()),
            StructField("title_length", IntegerType()),
            StructField("hide_score", BooleanType()),
            StructField("created", IntegerType()),
            StructField("author_fullname", StringType()),
            StructField("selftext_length", IntegerType()),
            StructField("post_hint", StringType()),
            StructField("url", StringType())
        ])

        submissions_df = self.spark.read \
            .format('com.mongodb.spark.sql.DefaultSource') \
            .option('spark.mongodb.input.collection', 'submissions') \
            .schema(submissions_schema) \
            .load()
        return submissions_df

    def get_submission_scores_df(self):
        """
        Retrieves the submission_scores DataFrame from the 'submission_scores' collection.

        Returns:
            The submission_scores DataFrame.
        """
        # Define the schema for the 'submission_scores' collection
        submission_scores_schema = StructType([
            StructField("_id", StringType()),
            StructField("id", StringType()),
            StructField("timestamp", IntegerType()),
            StructField("upvote_ratio", DoubleType()),
            StructField("ups", IntegerType()),
            StructField("score", IntegerType()),
            StructField("num_comments", IntegerType())
        ])

        submission_scores_df = self.spark.read \
            .format('com.mongodb.spark.sql.DefaultSource') \
            .option('spark.mongodb.input.collection', 'submission_scores') \
            .schema(submission_scores_schema) \
            .load()
        return submission_scores_df

    def get_submission_sentiments_df(self):
        """
        Retrieves the submission_sentiments DataFrame from the 'submission_sentiments' collection.

        Returns:
            The submission_sentiments DataFrame.
        """
        # Define the schema for the 'submission_sentiments' collection
        submission_sentiments_schema = StructType([
            StructField("_id", StringType()),
            StructField("id", StringType()),
            StructField("hash_check", StringType()),
            StructField("updated_timestamp", IntegerType()),
            StructField("sentiment_value", DoubleType())
        ])

        submission_sentiments_df = self.spark.read \
            .format('com.mongodb.spark.sql.DefaultSource') \
            .option('spark.mongodb.input.collection', 'submission_sentiments') \
            .schema(submission_sentiments_schema) \
            .load()
        return submission_sentiments_df

    def get_composite_sentiment_df(self):
        """
        This function combines the data from submissions, submission scores, and submission sentiments DataFrames
        to calculate the composite sentiment for each submission. It returns a DataFrame containing the composite
        sentiment scores.

        Returns:
            The composite sentiment DataFrame.
        """
        submissions_df = self.get_submissions_df()
        submission_scores_df = self.get_submission_scores_df()
        submission_sentiments_df = self.get_submission_sentiments_df()

        # Calculate the timestamp for last concerned timestamp
        last_timestamp = int(time.time()) - 90 * 24 * 3600

        # Filter the DataFrame based on the created timestamp and selftext_length
        filtered_submissions_df = submissions_df \
            .filter(submissions_df.created > last_timestamp) \
            .filter(submissions_df.selftext_length > 100)

        # Join with submission_scores to get the last value of score
        joined_score_df = filtered_submissions_df.join(
            submission_scores_df,
            "id",
            "inner"
        ).select(
            filtered_submissions_df.id,
            filtered_submissions_df.subreddit,
            filtered_submissions_df.created,
            submission_scores_df.score
        )

        # Join with submission_sentiments to get sentiment_value
        joined_sentiments_df = joined_score_df.join(
            submission_sentiments_df,
            "id",
            "inner"
        ).select(
            joined_score_df.id,
            joined_score_df.subreddit,
            joined_score_df.created,
            joined_score_df.score,
            submission_sentiments_df.sentiment_value
        )

        # Calculate sentiment_composite
        composite_sentiment_df = joined_sentiments_df \
            .withColumn("sentiment_composite",
                        col("sentiment_value") * when(col("score") > 0, log(col("score"))).otherwise(0))
        return composite_sentiment_df

    def analyze_by_hours(self):
        """
        This function performs sentiment analysis on submissions grouped by hours. It calculates the sum of
        sentiment scores for each subreddit within each hour and writes the results to the MongoDB collection
        named "analyzed_by_created_hours".

        Returns:
            None
        """
        composite_sentiment_df = self.get_composite_sentiment_df()

        # Round down the created timestamp to the nearest hour
        floor_created_df = composite_sentiment_df.withColumn("created_hour", floor(col('created') / 3600) * 3600)

        # Group by created_hour, subreddit, and find the sum of sentiment_composite
        result_df = floor_created_df.groupby("created_hour", "subreddit").agg({"sentiment_composite": "sum"}) \
            .withColumnRenamed("sum(sentiment_composite)", "sum_sentiment_score")

        # Write the result back to the MongoDB collection analyzed_by_created_hours
        database = self.connection.database
        output_collection = database['analyzed_by_created_hours']
        # Iterate over the result_df DataFrame and perform an upsert operation
        for row in result_df.collect():
            created_hour = row["created_hour"]
            subreddit = row["subreddit"]
            sum_sentiment_score = row["sum_sentiment_score"]

            # Perform an upsert operation
            output_collection.update_many(
                {"timestamp": created_hour, "subreddit": subreddit},
                {"$set": {"sum_sentiment_score": sum_sentiment_score}},
                upsert=True
            )

    def analyze_by_days(self):
        """
        This function performs sentiment analysis on submissions grouped by days. It calculates the sum of
        sentiment scores for each subreddit within each day and writes the results to the MongoDB collection named
        "analyzed_by_created_days".

        Returns:
            None
        """
        composite_sentiment_df = self.get_composite_sentiment_df()

        # Round down the created timestamp to the nearest day
        floor_created_df = composite_sentiment_df.withColumn("created_day", floor(col('created') / 86400) * 86400)

        # Group by created_day, subreddit, and find the sum of sentiment_composite
        result_df = floor_created_df.groupby("created_day", "subreddit").agg({"sentiment_composite": "sum"}) \
            .withColumnRenamed("sum(sentiment_composite)", "sum_sentiment_score")

        # Create window by sorting the DataFrame by timestamp within each subreddit group
        window_spec = Window.partitionBy("subreddit").orderBy("created_day")

        # calculate the Simple Moving Average (SMA) based on the last few values within each subreddit group
        result_df = result_df.withColumn("sum_sentiment_score_sma",
                                         avg("sum_sentiment_score").over(window_spec.rowsBetween(-3, 0)))

        database = self.connection.database
        output_collection = database['analyzed_by_created_days']
        # Iterate over the result_df DataFrame and perform an upsert operation
        for row in result_df.collect():
            created_day = row["created_day"]
            subreddit = row["subreddit"]
            sum_sentiment_score = row["sum_sentiment_score"]
            sum_sentiment_score_sma = row["sum_sentiment_score_sma"]

            # Perform an upsert operation
            output_collection.update_many(
                {"timestamp": created_day, "subreddit": subreddit},
                {"$set": {"sum_sentiment_score": sum_sentiment_score, "sum_sentiment_score_sma": sum_sentiment_score_sma}},
                upsert=True
            )

    def stop(self):
        """
        Stops the Spark session and closes the MongoDB connection.

        Returns:
            None
        """
        self.spark.stop()
        # close connection
        self.connection.close_connection()


if __name__ == '__main__':
    mongo_connection_string = sys.argv[1]
    mongo_database_name = sys.argv[2]
    analyzer = SparkAnalyzer(mongo_connection_string, mongo_database_name)
    analyzer.analyze_by_hours()
    analyzer.analyze_by_days()
    analyzer.stop()
