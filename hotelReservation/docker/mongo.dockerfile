ARG ENVOY_VERSION
ARG CONSUL_VERSION
ARG GRAMINE_VERSION
FROM envoyproxy/envoy:v${ENVOY_VERSION} as envoy
FROM hashicorp/consul:${CONSUL_VERSION} as consul

FROM gramineproject/gramine:v${GRAMINE_VERSION}

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    dnsutils \
    gettext-base \
    gcc \
    git \
    g++ \
    iproute2 \
    libcurl4-openssl-dev \
    libgoogle-perftools-dev \
    libpcre3-dev \
    libsnappy-dev \
    libssl-dev \
    libstemmer-dev \
    libunwind-dev \
    libyaml-cpp-dev \
    liblzma-dev \
    libzstd-dev \
    python3-pip \
    python-dev-is-python3 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Build Mongo from source and apply patch
ARG MONGO_VERSION
COPY gramine-manifests/mongod.diff /mongod.diff
RUN git clone --branch=r${MONGO_VERSION} --depth=1 https://github.com/mongodb/mongo /mongo/ \
    && cd /mongo/ \
    && python3 -m pip install -r --no-cache-dir etc/pip/compile-requirements.txt \
    && git apply /mongod.diff \
    && python3 buildscripts/scons.py install-mongod --disable-warnings-as-errors \
        --use-system-pcre --use-system-snappy --use-system-stemmer --use-system-tcmalloc \
        --use-system-libunwind --use-system-yaml --use-system-zlib --use-system-zstd \
    && cp ./build/install/bin/mongod /work/mongod \
    && rm -rf /mongo/

COPY --from=envoy /usr/local/bin/envoy /usr/local/bin/envoy
COPY --from=consul /bin/consul /usr/local/bin/consul
COPY ./bin/mongo_docker_entrypoint.sh /work/docker_entrypoint.sh

# Generate Gramine manifest
COPY gramine-manifests/mongod.manifest.template \
    /work/mongod.manifest.template
WORKDIR /work
# Template manifest
RUN gramine-manifest \
    -Dlog_level=warning \
    -Darch_libdir=/lib/x86_64-linux-gnu \
    -Dentrypoint=/work/mongod \
    mongod.manifest.template > mongod.manifest
# Generate key and sign manifest
RUN gramine-sgx-gen-private-key \
    && gramine-sgx-sign \
    --manifest mongod.manifest \
    --output mongod.manifest.sgx \
    && gramine-sgx-get-token --output mongod.token --sig mongod.sig
