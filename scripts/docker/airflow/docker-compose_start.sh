#!/bin/bash

set -e

export REPO_DIR="$(pwd)"
export DATA_DIR="$HOME/working/reddit_data/airflow"
export AIRFLOW_UID="50000"
export AIRFLOW_GID="50000"

mkdir -p "$DATA_DIR"/{logs,data,mongodb}
sudo chown "$AIRFLOW_UID" "$DATA_DIR"/{logs,data}
sudo chown 1001:1001 "$DATA_DIR"/mongodb

docker-compose -f scripts/docker/airflow/docker-compose.yaml up -d
