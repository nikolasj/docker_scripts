#!/usr/bin/env bash

set -e

SOURCES=$1
ARG=$2

echo "Run command: ${SOURCES} ${ARG}"

python3 ${SOURCES} ${ARG}
