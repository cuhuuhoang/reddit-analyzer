#!/bin/bash

MONGO_MODE="$1"

docker build -t reddit_analyzer_server -f scripts/docker/server/Dockerfile \
  --build-arg MONGO_MODE="${MONGO_MODE}" .
