#!/bin/bash
set -e

THIS_DIR=$(dirname $(readlink -f $0))
PROJ_ROOT=${THIS_DIR}/..

pushd ${PROJ_ROOT} > /dev/null

function usage() {
    echo "Usage: "
    echo "./bin/cli.sh <container>"
    echo ""
    echo "container being one of: "
    echo "- dsb           Managing DSB cluster"
}

if [[ -z "$1" ]]; then
    usage
    exit 1
elif [[ "$1" == "dsb" ]]; then
    CLI_CONTAINER="cli"
fi

# Set necessary env. variables for the client
if [[ -z "${CONSUL_DISABLE_UI}" ]]; then
    export CONSUL_UI_PORT_STRING='8500'
else
    export CONSUL_UI_PORT_STRING='8500:8500'
fi

# Make sure the CLI is running already in the background (avoids creating a new
# container every time)
docker compose \
    up \
    --no-recreate \
    -d \
    ${CLI_CONTAINER}

# Attach to the CLI container
docker compose \
    exec \
    ${CLI_CONTAINER} \
	bash

popd > /dev/null
