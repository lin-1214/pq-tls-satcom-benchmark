#!/bin/bash
set -ex

ROOT="$(dirname $(pwd))"

NGINX_APP=${ROOT}/tmp/nginx/sbin/nginx
NGINX_CONF_DIR=${ROOT}/tmp/nginx/conf

sudo python3 ${ROOT}/kex/experiment_mn.py ${NGINX_APP} ${NGINX_CONF_DIR}