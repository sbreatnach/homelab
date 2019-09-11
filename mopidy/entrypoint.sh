#!/usr/bin/env bash

# create config from any env variables supplied + mo template
mo ${MOPIDY_HOME}/mopidy.conf.tmpl > ${MOPIDY_HOME}/mopidy.conf

exec "$@"