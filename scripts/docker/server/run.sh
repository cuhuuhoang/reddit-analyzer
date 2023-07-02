#!/bin/bash

set -e

name="reddit_analyzer_server"

docker stop "$name"_instance || true
docker rm "$name"_instance || true

docker run -d --name "$name"_instance \
  --network internal \
  --restart unless-stopped \
  "$name"
