#!/bin/bash

set -e


docker-compose -f scripts/docker/airflow/docker-compose.yaml down --remove-orphans
