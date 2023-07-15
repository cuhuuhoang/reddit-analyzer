#!/bin/bash

. scripts/mongo/commons.sh

# Construct the connection string
connection_string="$(get_connection_string "$1")"

[ -d "output/db_dump" ] && rm -r "output/db_dump"
mongodump --uri="$connection_string" --out "output/db_dump"
