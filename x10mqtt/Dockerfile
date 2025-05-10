ARG BUILD_FROM=ghcr.io/hassio-addons/base:3.21
# hadolint ignore=DL3006
FROM ${BUILD_FROM} AS install

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
	libc-dev \
    && apk add --no-cache \
	   python3 \
           py3-paho-mqtt

WORKDIR /opt/build
RUN curl -L -s "https://github.com/HeyuX10Automation/heyu/archive/refs/tags/v2.10.3.tar.gz" \
        | tar zxvf - -C /opt/build

WORKDIR ./heyu-2.10.3
RUN sh ./Configure darwin -noext0 -norfxm -nodmx -noore -nokaku
RUN make -j$(nproc)
RUN mkdir -p /etc/heyu \
    && touch /etc/heyu/x10.conf
RUN make install
RUN mkdir -p /usr/local/var/lock \
    && mkdir -p /usr/local/var/tmp/heyu	\
	&& chmod 777 /usr/local/var/tmp/heyu \
	&& chmod 777 /usr/local/var/lock \
RUN apk del --purge .build-dependencies \
    && rm -fr /tmp/* \
	&& rm -rf /opt/build/* 
	
# Copy data
COPY data/x10mqtt.py /usr/local/bin/
COPY data/run.sh /
COPY data/rcs_mon.sh /etc/heyu
RUN chmod a+x /run.sh
RUN chmod a+x /etc/heyu/rcs_mon.sh

WORKDIR /
CMD [ "/run.sh" ]
