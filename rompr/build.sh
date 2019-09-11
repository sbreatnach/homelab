#!/usr/bin/env bash

set -e

ROMPR_VERSION=1.31

wget https://github.com/fatg3erman/RompR/releases/download/${ROMPR_VERSION}/rompr-${ROMPR_VERSION}.zip
unzip rompr-${ROMPR_VERSION}.zip
rm rompr-${ROMPR_VERSION}.zip
mkdir -p rompr/prefs rompr/albumart

docker build -t sbreatnach/rmprdckr:${ROMPR_VERSION} .

rm -rf rompr