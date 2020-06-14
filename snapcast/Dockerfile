FROM alpine:3.12

ARG SNAPCAST_VERSION

RUN apk -U add bash snapcast-server

RUN mkdir -p /shared && chown -R snapcast:snapcast /shared
ADD entrypoint.sh /entrypoint.sh

VOLUME [ "/shared" ]

USER snapcast