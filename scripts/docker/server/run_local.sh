#!/bin/bash

export PYTHONPATH=$(pwd)
export SOURCE_DIR=$(pwd)
export CREDENTIAL_FILE=mongo-local-credential.json

python3 src/server/server.py
