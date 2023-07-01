FROM python:3.8-slim-bullseye

ARG MONGO_MODE
# Install necessary dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Install PRAW and pymongo
RUN pip install praw pymongo

# Copy the necessary files to the container
COPY src /app/src
COPY scripts /app/scripts
COPY resources /app/resources
RUN mv "/app/resources/mongo-${MONGO_MODE}-credential.json" "/app/resources/mongo-credential.json"

# Set the main command to run the submissions_main.py script
CMD python src/submissions_main.py
