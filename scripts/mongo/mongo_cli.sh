#!/bin/bash

. scripts/mongo/commons.sh

# Construct the connection string
connection_string="$(get_connection_string "$1")"

# Connect to MongoDB using mongosh
mongosh "$connection_string"
