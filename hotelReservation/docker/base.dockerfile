FROM cc-uservice-security/sof_root:0.2.1 as root
FROM ubuntu:20.04

# Install DCAP and PSW
ARG PSW_VERSION=2.17.100.3-focal1
ARG DCAP_VERSION=1.14.100.3-focal1
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates gnupg wget \
    && wget -qO- https://download.01.org/intel-sgx/sgx_repo/ubuntu/intel-sgx-deb.key | apt-key add \
    && echo 'deb [arch=amd64] https://download.01.org/intel-sgx/sgx_repo/ubuntu focal main' >> /etc/apt/sources.list \
    && wget -qO- https://packages.microsoft.com/keys/microsoft.asc | apt-key add \
    && echo 'deb [arch=amd64] https://packages.microsoft.com/ubuntu/20.04/prod focal main' >> /etc/apt/sources.list \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && apt-get update && apt-get install -y --no-install-recommends \
    az-dcap-client \
    libsgx-ae-id-enclave=${DCAP_VERSION} \
    libsgx-ae-pce=${PSW_VERSION} \
    libsgx-ae-qe3=${DCAP_VERSION} \
    libsgx-dcap-default-qpl=${DCAP_VERSION} \
    libsgx-dcap-ql=${DCAP_VERSION} \
    libsgx-dcap-ql-dev=${DCAP_VERSION} \
    libsgx-enclave-common=${PSW_VERSION} \
    libsgx-headers=${PSW_VERSION} \
    libsgx-launch=${PSW_VERSION} \
    libsgx-pce-logic=${DCAP_VERSION} \
    libsgx-qe3-logic=${DCAP_VERSION} \
    libsgx-urts=${PSW_VERSION} && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install minimal dependencies to run entrypoint
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    dnsutils \
    gettext-base \
    iproute2 \
    python3 \
    python3-requests && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy Gramine dependencies
COPY --from=root /usr/local/bin/gramine-manifest /usr/local/bin/gramine-manifest
COPY --from=root /usr/local/bin/gramine-sgx /usr/local/bin/gramine-sgx
COPY --from=root /usr/local/bin/gramine-sgx-gen-private-key /usr/local/bin/gramine-sgx-gen-private-key
COPY --from=root /usr/local/bin/gramine-sgx-get-token /usr/local/bin/gramine-sgx-get-token
COPY --from=root /usr/local/bin/gramine-sgx-sign /usr/local/bin/gramine-sgx-sign
COPY --from=root /usr/local/lib/x86_64-linux-gnu/gramine /usr/local/lib/x86_64-linux-gnu/gramine
COPY --from=root /usr/local/lib/python3.8/dist-packages/graminelibos /usr/local/lib/python3.8/dist-packages/graminelibos
COPY --from=root /lib/x86_64-linux-gnu/libprotobuf-c.so.1.0.0 /lib/x86_64-linux-gnu/libprotobuf-c.so.1.0.0
COPY --from=root /lib/x86_64-linux-gnu/libprotobuf-c.so.1 /lib/x86_64-linux-gnu/libprotobuf-c.so.1

# Copy dependencies from root image
COPY --from=root /usr/local/bin/consul /usr/local/bin/consul
COPY --from=root /opt/ego /opt/ego
RUN ln -s /opt/ego/bin/ego /usr/local/bin/ego \
    && ln -s /opt/ego/bin/ego-go /usr/local/bin/ego-go
COPY --from=root /usr/local/bin/envoy /usr/local/bin/envoy
COPY --from=root /usr/local/go /usr/local/go
