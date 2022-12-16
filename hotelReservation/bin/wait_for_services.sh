#!/bin/bash

set -e

# If consul is enabled, this script will wait for all services and nodes to
# be healthy. Note that the script must be run from a node with a running
# Consul client agent (i.e. _not_ the client one)
if [[ "${ENABLE_CONSUL}" == "on" ]]; then
    export CONSUL_HTTP_ADDR="https://localhost:8501"
    export CONSUL_GRPC_ADDR="https://localhost:8502"
    export CONSUL_CACERT=/tls-client/consul-agent-ca.pem
    export CONSUL_CLIENT_CERT=/tls-client/dc1-client-consul-0.pem
    export CONSUL_CLIENT_KEY=/tls-client/dc1-client-consul-0-key.pem
fi

# Wait for all transitive service dependencies to be healthy before starting
until python3 ./bin/check_services_health.py ${SERVICE_NAME}; do
    echo "Waiting for Consul services to be healthy"
    sleep 5
done
