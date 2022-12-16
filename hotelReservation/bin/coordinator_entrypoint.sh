#!/bin/bash

set -e

OPEN_ENCLAVE_PATH=$1
USERVICE_RUNTIME=$2

# Start the coordinator
if [[ ${USERVICE_RUNTIME} == "ego" ]]; then
   . ${OPEN_ENCLAVE_PATH} && OE_SIMULATION=0 erthost \
        ./build/coordinator-enclave.signed
elif  [[ ${USERVICE_RUNTIME} == "ego-sim" ]]; then
    . ${OPEN_ENCLAVE_PATH} && OE_SIMULATION=1 erthost \
        ./build/coordinator-enclave.signed
fi