#!/bin/bash

set -e

# should run as scripts/mongo/docker_mongodb.sh

. scripts/mongo/settings.sh

docker stop "$MONGO_INSTANCE" || true
docker rm "$MONGO_INSTANCE" || true

# sudo chown -R 1001:1001 "$(pwd)/output/mongo"
[ ! -d "$(pwd)/output/mongo" ] && echo "Not exist output/mongo" && exit 1

docker run -d \
	--name="$MONGO_INSTANCE" \
	-v "$(pwd)/output/mongo":/bitnami/mongodb \
	-e MONGODB_ROOT_PASSWORD="$MONGO_ROOT_PW" \
	--network internal \
	-p 27017:27017 \
	--restart unless-stopped \
	bitnami/mongodb:5.0-debian-10
