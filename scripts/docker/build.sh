#!/bin/bash

MONGO_MODE="$1"

docker build -t reddit_analyzer -f scripts/docker/Dockerfile \
  --build-arg MONGO_MODE="${MONGO_MODE}" .
