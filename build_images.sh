#!/usr/bin/env bash

ROMPR_VERSION=1.31
MOPIDY_VERSION=2.2.3

docker build --build-arg ROMPR_VERSION=${ROMPR_VERSION} \
    -t sbreatnach/rmprdckr:${ROMPR_VERSION} ./rompr
docker build --build-arg MOPIDY_VERSION=${MOPIDY_VERSION} \
    -t sbreatnach/mopidy:${MOPIDY_VERSION} ./mopidy