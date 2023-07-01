#!/bin/bash

set -e

docker stop reddit_analyzer_instance || true
docker rm reddit_analyzer_instance || true

docker run -d --name reddit_analyzer_instance \
  --network host \
  --restart unless-stopped \
  reddit_analyzer
