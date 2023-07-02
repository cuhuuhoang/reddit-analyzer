FROM python:3.8-slim-bullseye
ENV TZ=Asia/Ho_Chi_Minh
RUN yes | cp -f /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ARG MONGO_MODE
# Install necessary dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc wget \
    && rm -rf /var/lib/apt/lists/*

# java
COPY --from=adoptopenjdk/openjdk8:jdk8u-debianslim-nightly /opt/java/openjdk /usr/lib/jvm/java-8-openjdk-amd64

# spark
RUN mkdir -p "/content"
RUN wget -qO "/content/spark-bin-hadoop3.tgz" "https://downloads.apache.org/spark/spark-3.3.2/spark-3.3.2-bin-hadoop3.tgz"
RUN tar xf "/content/spark-bin-hadoop3.tgz" -C "/content/" && rm "/content/spark-bin-hadoop3.tgz"

# env
ENV SPARK_HOME=/content/spark-3.3.2-bin-hadoop3
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64

# Set the working directory
WORKDIR /app

# Install pip package
RUN pip install --no-cache-dir praw pymongo spacy nltk pyspark findspark

# Copy the necessary files to the container
COPY src /app/src
COPY scripts /app/scripts
COPY resources /app/resources
RUN mv "/app/resources/mongo-${MONGO_MODE}-credential.json" "/app/resources/mongo-credential.json"

# Set the main command to run the submissions_main.py script
CMD python src/submissions_main.py
