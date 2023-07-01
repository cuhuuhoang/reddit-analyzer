#!/bin/bash

set -e

. scripts/mongo/settings.sh

mongosh -u root -p "$MONGO_ROOT_PW" --authenticationDatabase admin
