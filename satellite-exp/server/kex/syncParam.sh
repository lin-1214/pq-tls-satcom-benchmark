#!/bin/bash

ROOT="$(dirname $(pwd))"
CLIENT_DIR="~/Desktop/pq-tls-benchmark/client/kex/"

if [ $# -ne 1 ]; then
    echo "Usage: $0 <client_ip>"
    echo "check by ifconfig eth0"
    exit 1
fi

CLIENT_IP=$1

# copy CA key and cert with error handling
scp ${ROOT}/prime256v1.pem client@${CLIENT_IP}:${CLIENT_DIR} || {
    echo "Error: Failed to copy prime256v1.pem"
    exit 1
}

scp ${ROOT}/../tmp/nginx/conf/CA.crt client@${CLIENT_IP}:${CLIENT_DIR} || {
    echo "Error: Failed to copy CA.crt"
    exit 1
}
