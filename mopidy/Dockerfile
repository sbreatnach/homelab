FROM debian:buster

ARG MOPIDY_VERSION
ENV MOPIDY_SCROBBLER_VERSION=1.2.1 \
    MOPIDY_INTERNETARCHIVE_VERSION=2.0.3 \
    MOPIDY_LOCAL_SQLITE_VERSION=1.0.0 \
    MOPIDY_HOME=/var/lib/mopidy

RUN apt update && apt install -y \
    python python-pip gir1.2-gst-plugins-base-1.0 gir1.2-gstreamer-1.0 \
    gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly gstreamer1.0-tools \
    ffmpeg gstreamer1.0-plugins-bad \
    adduser bash curl netcat-openbsd && \
    curl -sSL https://git.io/get-mo -o /usr/bin/mo && \
    chmod 755 /usr/bin/mo
COPY mopidy.conf.tmpl ${MOPIDY_HOME}/mopidy.conf.tmpl
COPY entrypoint.sh /entrypoint.sh
RUN useradd -m mopidy && \
    mkdir -p ${MOPIDY_HOME}/local ${MOPIDY_HOME}/media && \
    chown -R mopidy:mopidy ${MOPIDY_HOME} /home/mopidy

USER mopidy
RUN pip install --user --no-cache-dir mopidy==${MOPIDY_VERSION} \
    mopidy-scrobbler==${MOPIDY_SCROBBLER_VERSION} \
    mopidy-internetarchive==${MOPIDY_INTERNETARCHIVE_VERSION} \
    mopidy-local-sqlite==${MOPIDY_LOCAL_SQLITE_VERSION}
ENV PATH=$PATH:/home/mopidy/.local/bin

VOLUME ["/var/lib/mopidy/local-sqlite", "/var/lib/mopidy/media"]

EXPOSE 6600 6680 5555/udp

ENTRYPOINT [ "/entrypoint.sh" ]
CMD ["mopidy", "--config", "/var/lib/mopidy/mopidy.conf"]
