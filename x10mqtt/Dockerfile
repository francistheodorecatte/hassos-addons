ARG BUILD_FROM=hassioaddons/base:8.0.6
# hadolint ignore=DL3006
FROM ${BUILD_FROM}

ENV LANG C.UTF-8

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install packages
# hadolint ignore=DL3003

RUN \
    apk add --no-cache --virtual .build-dependencies \
        tar \
		curl \
		build-base \
    \
    && apk add --no-cache \
	   python3 \
                py3-paho-mqtt \
    \
    && mkdir -p /opt/build \
    && curl -L -s "https://github.com/HeyuX10Automation/heyu/archive/refs/tags/v2.10.3.tar.gz" \
        | tar zxvf - -C /opt/build \
    \
    && cd /opt/build/heyu-2.10.3/ \
	\
    && sh ./Configure darwin \
    \
	&& make -j$(nproc) \
    \
    && mkdir -p /etc/heyu \
    && touch /etc/heyu/x10.conf \
    && make install \
    \
    && mkdir -p /usr/local/var/lock \
    && mkdir -p /usr/local/var/tmp/heyu	\
	&& chmod 777 /usr/local/var/tmp/heyu \
	&& chmod 777 /usr/local/var/lock \
	\
    && apk del --purge .build-dependencies \
    && rm -fr /tmp/* \
	&& rm -rf /opt/build/* 
	
# Copy data
COPY data/x10mqtt.py /usr/local/bin/
COPY data/run.sh /
RUN chmod a+x /run.sh

WORKDIR /
CMD [ "/run.sh" ]
