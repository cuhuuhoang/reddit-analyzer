#!/bin/bash

if [ $# -eq 1 ]; then
  path="$1"
else
  path="mongo-local-credential.json"
fi

export SOURCE_DIR="$(pwd)"
python3 src/core/setup_index.py "$path"
