#!/bin/bash

. scripts/mongo/commons.sh

# Construct the connection string
connection_string="$(get_connection_string "$1")"

[ ! -d "output/db_dump" ] && exit 1
mongorestore --uri="$connection_string" --drop "output/db_dump/reddit_analyzer"
