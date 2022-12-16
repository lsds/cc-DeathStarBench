ARG ENVOY_VERSION
ARG CONSUL_VERSION
ARG GRAMINE_VERSION
FROM envoyproxy/envoy:v${ENVOY_VERSION} as envoy
FROM hashicorp/consul:${CONSUL_VERSION} as consul

FROM gramineproject/gramine:v${GRAMINE_VERSION}

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    autotools-dev \
    automake \
    build-essential \
    curl \
    dnsutils \
    gettext-base \
    git \
    iproute2 \
    libevent-dev \
    pkg-config \
    wget \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Download and build native memcached from source
ARG MEMCACHED_VERSION
RUN mkdir -p /tmp \
    && cd /tmp \
    && git clone -b ${MEMCACHED_VERSION} \
        https://github.com/memcached/memcached.git \
    && cd /tmp/memcached \
    && ./autogen.sh \
    && ./configure \
    && make \
    && mkdir -p /work \
    && cp memcached /work/memcached

# Generate Gramine manifest
COPY gramine-manifests/memcached.manifest.template \
    /work/memcached.manifest.template
WORKDIR /work
# Template manifest
RUN gramine-manifest \
    -Dlog_level=warning \
    -Darch_libdir=/lib/x86_64-linux-gnu \
    -Dentrypoint=/work/memcached \
    memcached.manifest.template > memcached.manifest
# Generate key and sign manifest
RUN gramine-sgx-gen-private-key
RUN gramine-sgx-sign \
    --manifest memcached.manifest \
    --output memcached.manifest.sgx
RUN gramine-sgx-get-token --output memcached.token --sig memcached.sig

COPY --from=envoy /usr/local/bin/envoy /usr/local/bin/envoy
COPY --from=consul /bin/consul /usr/local/bin/consul
COPY ./bin/memcached_docker_entrypoint.sh /work/docker_entrypoint.sh
