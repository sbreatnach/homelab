#!/usr/bin/env bash

ROMPR_VERSION=1.31
MOPIDY_VERSION=2.2.3
SNAPCAST_VERSION=0.15.0

docker build --build-arg ROMPR_VERSION=${ROMPR_VERSION} \
    -t registry.nas.home/rmprdckr:${ROMPR_VERSION} ./rompr
docker push registry.nas.home/rmprdckr:${ROMPR_VERSION}

docker build --build-arg MOPIDY_VERSION=${MOPIDY_VERSION} \
    -t registry.nas.home/mopidy:${MOPIDY_VERSION} ./mopidy
docker push registry.nas.home/mopidy:${MOPIDY_VERSION}

docker build --build-arg SNAPCAST_VERSION=${SNAPCAST_VERSION} \
    -t registry.nas.home/snapcast:${SNAPCAST_VERSION} ./snapcast
docker push registry.nas.home/snapcast:${SNAPCAST_VERSION}