import os
import time

import findspark
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, floor
from pyspark.sql.types import StructType, StructField, IntegerType, StringType, BooleanType, DoubleType

from mongodb_client import MongoDBClient


class SparkAnalyzer:
    def __init__(self):
        os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
        os.environ["SPARK_HOME"] = "/content/spark-3.3.2-bin-hadoop3"

        findspark.init()

        [database, connection_string] = MongoDBClient.get_mongo_connection_string()

        self.spark = SparkSession \
            .builder \
            .master('local') \
            .appName('SubmissionAnalyzer') \
            .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.12:3.0.1') \
            .config('spark.mongodb.input.uri', connection_string) \
            .config('spark.mongodb.output.uri', connection_string) \
            .getOrCreate()

    def get_submissions_df(self):
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

    def analyze_by_hours(self):
        submissions_df = self.get_submissions_df()
        submission_scores_df = self.get_submission_scores_df()
        submission_sentiments_df = self.get_submission_sentiments_df()

        # Calculate the timestamp for one month ago
        one_month_ago = int(time.time()) - 30 * 24 * 3600

        # Filter the DataFrame based on the created timestamp and selftext_length
        filtered_submissions_df = submissions_df\
            .filter(submissions_df.created > one_month_ago)\
            .filter(submissions_df.selftext_length > 50)

        # Join with submission_scores to get the last value of score
        joined_df = filtered_submissions_df.join(
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
        final_df = joined_df.join(
            submission_sentiments_df,
            "id",
            "inner"
        ).select(
            joined_df.id,
            joined_df.subreddit,
            joined_df.created,
            joined_df.score,
            submission_sentiments_df.sentiment_value
        )

        # Calculate sentiment_composite
        final_df = final_df.withColumn("sentiment_composite", col("sentiment_value") * col("score"))

        # Round down the created timestamp to the nearest hour
        final_df = final_df.withColumn("created_hour", floor(final_df.created / 3600) * 3600)

        # Group by created_hour, subreddit, and find the sum of sentiment_composite
        result_df = final_df.groupby("created_hour", "subreddit").agg({"sentiment_composite": "sum"})\
            .withColumnRenamed("sum(sentiment_composite)", "sum_sentiment_score")

        # Write the result back to the MongoDB collection analyzed_by_created_hours
        client = MongoDBClient()
        database = client.database
        analyzed_by_created_hours_collection = database['analyzed_by_created_hours']
        # Iterate over the result_df DataFrame and perform an upsert operation
        for row in result_df.collect():
            created_hour = row["created_hour"]
            subreddit = row["subreddit"]
            sum_sentiment_score = row["sum_sentiment_score"]

            # Perform an upsert operation
            analyzed_by_created_hours_collection.update_many(
                {"created_hour": created_hour, "subreddit": subreddit},
                {"$set": {"sum_sentiment_score": sum_sentiment_score}},
                upsert=True
            )
        # close connection
        client.close_connection()


if __name__ == '__main__':
    analyzer = SparkAnalyzer()
    analyzer.analyze_by_hours()
