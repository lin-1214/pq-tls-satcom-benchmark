#!/bin/bash
# set -x

echo "Running signature experiment... ⚡"

ROOT="$(dirname $(pwd))"

NGINX_APP=${ROOT}/tmp/nginx/sbin/nginx
NGINX_CONF_DIR=${ROOT}/tmp/nginx/conf

##########################
# Run experiment
##########################
# set -e

for SIG in "ecdsap256" "dilithium2" "dilithium3";
do
    # Ask nginx to use ${SIG} cert and key
    sed "s/??SERVER_CERT??/${SIG}_server.crt/g; s/??SERVER_KEY??/${SIG}_server.key/g" nginx.conf > ${NGINX_CONF_DIR}/nginx.conf

    # Run experiment
    python3 experiment_mn.py ${SIG} ${NGINX_APP} ${NGINX_CONF_DIR}/nginx.conf

    # Wait a bit before restarting
    sleep 5
done
