#!/bin/bash

set -e

docker build -t "reddit_airflow" -f scripts/docker/airflow/Dockerfile .
