FROM debian:buster

ARG MOPIDY_VERSION
ENV MOPIDY_IRIS_VERSION=3.43.0 \
    MOPIDY_LOCAL_IMAGES_VERSION=1.0.0 \
    MOPIDY_LOCAL_SQLITE_VERSION=1.0.0 \
    MOPIDY_HOME=/var/lib/mopidy

RUN apt update && apt install -y \
    python python-pip gir1.2-gst-plugins-base-1.0 gir1.2-gstreamer-1.0 \
    gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly gstreamer1.0-tools \
    ffmpeg gstreamer1.0-plugins-bad \
    adduser bash curl netcat-openbsd && \
    curl -sSL https://git.io/get-mo -o /usr/bin/mo && \
    chmod 755 /usr/bin/mo
COPY entrypoint.sh /entrypoint.sh
RUN useradd -m mopidy && \
    mkdir -p ${MOPIDY_HOME}/local ${MOPIDY_HOME}/media && \
    chown -R mopidy:mopidy ${MOPIDY_HOME} /home/mopidy

USER mopidy
RUN pip install --user --no-cache-dir mopidy==${MOPIDY_VERSION} \
    mopidy-local-images==${MOPIDY_LOCAL_IMAGES_VERSION} \
    mopidy-iris==${MOPIDY_IRIS_VERSION} \
    mopidy-local-sqlite==${MOPIDY_LOCAL_SQLITE_VERSION}
ENV PATH=$PATH:/home/mopidy/.local/bin

COPY --chown=mopidy mopidy.conf.tmpl ${MOPIDY_HOME}/mopidy.conf.tmpl
VOLUME ["/var/lib/mopidy/local-sqlite", "/var/lib/mopidy/media"]

EXPOSE 6600 6680 5555/udp

ENTRYPOINT [ "/entrypoint.sh" ]
CMD ["mopidy", "--config", "/var/lib/mopidy/mopidy.conf"]
