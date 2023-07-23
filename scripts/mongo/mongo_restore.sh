#!/bin/bash

# Construct the connection string
connection_string="$1"

[ ! -d "/opt/airflow/data/db_dump" ] && exit 1
mongorestore --uri="$connection_string" --drop "/opt/airflow/data/db_dump/reddit_analyzer"
