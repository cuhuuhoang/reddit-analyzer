#!/bin/bash

# Get the path to the MongoDB credential file from the command-line argument
credential_file="$1"

# Parse the credential file using jq
host=$(jq -r '.host' "$credential_file")
port=$(jq -r '.port' "$credential_file")
username=$(jq -r '.username' "$credential_file")
password=$(jq -r '.password' "$credential_file")
database=$(jq -r '.database' "$credential_file")

# Construct the connection string
connection_string="mongodb://$username:$password@$host:$port/$database?authSource=admin"

# Connect to MongoDB using mongosh
mongosh "$connection_string"
