#!/bin/bash

# Construct the connection string
connection_string="$1"

[ -d "/opt/airflow/data/db_dump" ] && rm -r "/opt/airflow/data/db_dump"
mongodump --uri="$connection_string" --out "/opt/airflow/data/db_dump"
