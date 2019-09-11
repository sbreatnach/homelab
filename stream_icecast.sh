#!/usr/bin/env bash

URL=http://icecast.nas.home/mopidy

PLAY_BIN=$(/c/Users/deesn/Apps/MPlayer-x86_64-r38135+gb272d5b9b6/mplayer.exe -quiet -cache 256 $URL)
#PLAY_BIN=$(wget -qO- $URL | lame --quiet --decode --mp3input - - | aplay)

trap 'kill $(jobs -p)' EXIT
while true
do
    ${PLAY_BIN}
    sleep 1
done
