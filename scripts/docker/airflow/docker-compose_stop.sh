#!/bin/bash

set -e

#export AIRFLOW_UID="10005"
#export AIRFLOW_GID="10005"

docker-compose -f scripts/docker/airflow/docker-compose.yaml down --remove-orphans
