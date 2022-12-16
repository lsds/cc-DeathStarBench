FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    autoconf \
    automake \
    bison \
    build-essential \
    ca-certificates \
    clang-10 \
    curl \
    dnsutils \
    doxygen \
    gawk \
    gettext \
    git \
    iproute2 \
    libcurl4-openssl-dev \
    libprotobuf-c-dev \
    libssl-dev \
    libtool \
    libtool-bin \
    linux-headers-$(uname -r) \
    luarocks \
    nasm \
    ninja-build \
    python3 \
    pkg-config \
    protobuf-c-compiler \
    protobuf-compiler \
    python3-cryptography \
    python3-pip \
    python3-protobuf \
    unzip \
    wget \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && python3 -m pip install --no-cache-dir "meson>=0.56" "toml>=0.10"

# Build and install CMake
ARG CMAKE_VERSION=3.23.2
RUN mkdir -p /tmp \
    && cd /tmp \
    && wget -q https://github.com/Kitware/CMake/releases/download/v${CMAKE_VERSION}/cmake-${CMAKE_VERSION}.tar.gz \
    && tar xzvf cmake-${CMAKE_VERSION}.tar.gz \
    && cd /tmp/cmake-${CMAKE_VERSION} \
    && ./bootstrap \
    && make \
    && make install

# Build and install Neovim
ARG NEOVIM_VERSION=v0.7.2
WORKDIR /tmp
RUN mkdir -p /tmp \
    && cd /tmp \
    && git clone -b ${NEOVIM_VERSION} https://github.com/neovim/neovim \
    && cd /tmp/neovim \
    && make CMAKE_BUILD_TYPE=RelWithDebInfoi \
    && make install

# Install Go
ARG GO_VERSION=1.18.3
RUN mkdir -p /tmp \
    && cd /tmp \
    && wget -q  https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz \
    && rm -rf /usr/local/go \
    && tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz

# Clone and build SDK
ARG EDGELESSRT_VERSION=v0.3.5
RUN mkdir /opt/edgelessrt \
    && cd /opt/edgelessrt \
    && git clone -b ${EDGELESSRT_VERSION} https://github.com/edgelesssys/edgelessrt \
    && cd edgelessrt \
    && mkdir build \
    && cd build \
    && cmake -GNinja .. \
    && ninja \
    && ninja install

# Clone and install EGo
ARG EGO_VERSION
RUN . /opt/edgelessrt/share/openenclave/openenclaverc \
    && export PATH=$PATH:/usr/local/go/bin \
    && git clone -b v${EGO_VERSION} https://github.com/edgelesssys/ego \
    && cd ego \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make \
    && make install

# Build and install Consul
ARG CONSUL_VERSION
RUN git clone -b v${CONSUL_VERSION} https://github.com/hashicorp/consul /tmp/consul \
    && cd /tmp/consul \
    && export PATH=$PATH:/usr/local/go/bin \
    && make dev \
    && cp ./bin/consul /usr/local/bin/consul

# Build and install Envoy
ARG ENVOY_VERSION
RUN curl -L https://func-e.io/install.sh | bash -s -- -b /usr/local/bin \
    && func-e use ${ENVOY_VERSION} \
    && cp /root/.func-e/versions/${ENVOY_VERSION}/bin/envoy /usr/local/bin/envoy

# Build and install Gramine
ARG GRAMINE_VERSION
RUN git clone -b v${GRAMINE_VERSION} https://github.com/gramineproject/gramine /tmp/gramine \
    && cd /tmp/gramine \
    && meson setup build/ --buildtype=release -Ddirect=enabled -Dsgx=enabled \
    && ninja -C build/ \
    && ninja -C build/ install

# Install Marblerun
RUN git clone https://github.com/edgelesssys/marblerun.git /tmp/marblerun \
    && cd marblerun \
    && . /opt/edgelessrt/share/openenclave/openenclaverc \
    && export PATH=$PATH:/usr/local/go/bin \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make
