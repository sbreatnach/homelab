FROM alpine:3.10

ARG MOPIDY_VERSION
ENV MOPIDY_SCROBBLER_VERSION=1.2.1 \
    MOPIDY_YOUTUBE_VERSION=2.0.2 \
    MOPIDY_EMBY_VERSION=0.2.6 \
    MOPIDY_INTERNETARCHIVE_VERSION=2.0.3 \
    MOPIDY_HOME=/var/lib/mopidy

RUN apk --no-cache --update add \
    python2 python2-dev py2-pip gstreamer gstreamer-tools gst-plugins-base \
    gst-plugins-ugly gst-plugins-good py2-gst youtube-dl lame bash curl && \
    curl -sSL https://git.io/get-mo -o /usr/bin/mo && \
    chmod 755 /usr/bin/mo
COPY mopidy.conf.tmpl ${MOPIDY_HOME}/mopidy.conf.tmpl
COPY entrypoint.sh /entrypoint.sh
RUN addgroup -S mopidy && \
    adduser -S mopidy -G mopidy && \
    mkdir -p ${MOPIDY_HOME}/local ${MOPIDY_HOME}/media && \
    chown -R mopidy:mopidy ${MOPIDY_HOME}

USER mopidy
RUN pip install --user --no-cache-dir mopidy==${MOPIDY_VERSION} \
    mopidy-scrobbler==${MOPIDY_SCROBBLER_VERSION} \
    mopidy-youtube==${MOPIDY_YOUTUBE_VERSION} \
    mopidy-emby==${MOPIDY_EMBY_VERSION} \
    mopidy-internetarchive==${MOPIDY_INTERNETARCHIVE_VERSION}
ENV PATH=$PATH:/home/mopidy/.local/bin

VOLUME ["/var/lib/mopidy/local", "/var/lib/mopidy/media"]

EXPOSE 6600 6680 5555/udp

ENTRYPOINT [ "/entrypoint.sh" ]
CMD ["mopidy", "--config", "/var/lib/mopidy/mopidy.conf"]
