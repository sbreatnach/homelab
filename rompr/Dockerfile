FROM trafex/alpine-nginx-php7:1.2.0

ARG ROMPR_VERSION
ENV ROMPR_HOME=/var/www/rompr

USER root
RUN apk --update --no-cache add \
    wget unzip php7-sqlite3 imagemagick php7-pdo_mysql php7-simplexml && \
    wget https://github.com/fatg3erman/RompR/releases/download/${ROMPR_VERSION}/rompr-${ROMPR_VERSION}.zip && \
    unzip rompr-${ROMPR_VERSION}.zip && \
    rm rompr-${ROMPR_VERSION}.zip && \
    mkdir -p rompr/prefs rompr/albumart && \
    mv rompr /var/www && \
    chown -R nobody:nobody ${ROMPR_HOME}

COPY --chown=nobody nginx.conf /etc/nginx/nginx.conf

WORKDIR /var/www/html
USER nobody
