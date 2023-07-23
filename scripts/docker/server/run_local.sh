#!/bin/bash

export PYTHONPATH=$(pwd)
export SOURCE_DIR=$(pwd)
export CREDENTIAL_PATH=resources/mongo-local2-credential.json

python3 src/server/server.py
