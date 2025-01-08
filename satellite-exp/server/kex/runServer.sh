#!/bin/bash
# set -ex

echo "Running key exchange experiment on server... ⚡"

ROOT="$(dirname $(pwd))"

NGINX_APP=${ROOT}/tmp/nginx/sbin/nginx
NGINX_CONF_DIR=${ROOT}/tmp/nginx/conf

sudo python3 ${ROOT}/kex/server.py ${NGINX_APP} ${NGINX_CONF_DIR}/nginx.conf

