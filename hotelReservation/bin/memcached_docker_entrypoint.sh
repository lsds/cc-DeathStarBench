#!/bin/bash

set -e

LOG_DIR=/var/log/dsb
mkdir -p ${LOG_DIR}
SERVICE_NAME=$1
USERVICE_RUNTIME=$2

if [[ "${ENABLE_CONSUL}" == "on" ]]; then
    # Given that there will always be a Consul Agent running in the same physical
    # host (co-located as a DaemonSet in k8s, or in the same container in compose)
    # we can always talk to our local agent on localhost. However, we need the
    # server's IP to join the mesh
    export CONSUL_SERVICE_NAME=${SERVICE_NAME}-memcached
    export CONSUL_IP_ADDR=$(host consul | awk '{ print $NF }')
    export CONSUL_HTTP_ADDR="https://localhost:8501"
    export CONSUL_GRPC_ADDR="https://localhost:8502"
    echo "Got consul's server details:"
    echo "- Service name: ${CONSUL_SERVICE_NAME}"
    echo "- IP address: ${CONSUL_IP_ADDR}"
    echo "- HTTP address: ${CONSUL_HTTP_ADDR}"
    echo "- gRPC address: ${CONSUL_GRPC_ADDR}"

    # Export TLS-related variables necessary to interact with Consul
    export CONSUL_HTTP_SSL=true
    export CONSUL_CACERT=/tls-client/consul-agent-ca.pem
    export CONSUL_CLIENT_CERT=/tls-client/dc1-client-consul-0.pem
    export CONSUL_CLIENT_KEY=/tls-client/dc1-client-consul-0-key.pem

    # Use the variables to populate the templated client agent config files
    TEMPLATED_FILES_DIR=/deploy/compose/templated
    TEMPLATE_FILES_DIR=/consul/config
    mkdir -p ${TEMPLATED_FILES_DIR}
    envsubst \
        < ${TEMPLATE_FILES_DIR}/${SERVICE_NAME}_memcached_client.hcl \
        > ${TEMPLATED_FILES_DIR}/consul_${SERVICE_NAME}_memcached_client.hcl

    # Deploy the client agent and wait for the Consul server to be ready
    consul agent \
        -config-file=${TEMPLATED_FILES_DIR}/consul_${SERVICE_NAME}_memcached_client.hcl \
        -log-file=${LOG_DIR}/consul_client_${SERVICE_NAME}_memcached.log > \
        ${LOG_DIR}/consul_client_${SERVICE_NAME}_memcached.log 2>&1 &
    until curl -s \
        --cacert ${CONSUL_CACERT} \
        --key ${CONSUL_CLIENT_KEY} \
        --cert ${CONSUL_CLIENT_CERT} \
        ${CONSUL_HTTP_ADDR}/v1/status/leader | grep 8300; do
      echo "Waiting for Consul to start..."
      sleep 1
    done

    # Register our service with Consul
    export CONSUL_SERVICE_IP_ADDR=$(ip addr show eth0 | grep "inet\b" | awk '{print $2}' | cut -d/ -f1)
    echo "Got service IP address: ${CONSUL_SERVICE_IP_ADDR}"
    envsubst \
        < ${TEMPLATE_FILES_DIR}/services/${SERVICE_NAME}_memcached.hcl \
        > ${TEMPLATED_FILES_DIR}/consul_service_${SERVICE_NAME}_memcached.hcl
    consul services register \
        ${TEMPLATED_FILES_DIR}/consul_service_${SERVICE_NAME}_memcached.hcl

    # Before starting the proxy, template and apply the service intentions
    envsubst \
        < ${TEMPLATE_FILES_DIR}/intentions/${SERVICE_NAME}_memcached.hcl \
        > ${TEMPLATED_FILES_DIR}/consul_intention_${SERVICE_NAME}_memcached.hcl
    until consul config write \
        ${TEMPLATED_FILES_DIR}/consul_intention_${SERVICE_NAME}_memcached.hcl; do
      echo "Waiting to write config entries"
      sleep 1
    done

    # Start the proxy
    consul connect envoy \
        -sidecar-for ${SERVICE_NAME}-memcached \
        > ${LOG_DIR}/consul_sidecar_${SERVICE_NAME}_memcached.log 2>&1 &
fi

MEMCACHED_BINARY=/work/memcached
if [[ ${USERVICE_RUNTIME} == "ego" ]] || [[ ${USERVICE_RUNTIME} == "gramine" ]]; then
    # Necessary to run as user `nobody`. See here for more details:
    # https://github.com/gramineproject/gramine/tree/master/CI-Examples/memcached#why-this-memcached-configuration
    gramine-sgx ${MEMCACHED_BINARY} start -u nobody
else
    ${MEMCACHED_BINARY} start -u root
fi
