#!/bin/bash
# set -x

echo "Running signature experiment... ⚡"

ROOT="$(dirname $(pwd))"

NGINX_APP=${ROOT}/tmp/nginx/sbin/nginx
NGINX_CONF_DIR=${ROOT}/tmp/nginx/conf

for SIG in "ecdsap256" "dilithium2";
do
    # Ask nginx to use ${SIG} cert and key
    sed "s/??SERVER_CERT??/${SIG}_server.crt/g; s/??SERVER_KEY??/${SIG}_server.key/g" nginx.conf > ${NGINX_CONF_DIR}/nginx.conf

    # Run experiment
    sudo python3 ${ROOT}/sig/server.py ${NGINX_APP} ${NGINX_CONF_DIR}/nginx.conf

    # Wait a bit before restarting
    sleep 5
done
