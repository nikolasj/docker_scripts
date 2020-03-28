#!/usr/bin/env bash

set -e

SOURCES=$1
ARG=$2

echo "Install python required"
python3 -mpip install -U pip
python3 -mpip install requests

echo "Run command: ${SOURCES} ${ARG}"

python3 ${SOURCES} ${ARG}
