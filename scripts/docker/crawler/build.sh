#!/bin/bash

MONGO_MODE="$1"

docker build -t reddit_analyzer_crawler -f scripts/docker/crawler/Dockerfile \
  --build-arg MONGO_MODE="${MONGO_MODE}" .
