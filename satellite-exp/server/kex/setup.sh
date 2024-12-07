#!/bin/bash
set -ex

ROOT="$(dirname $(pwd))"

OPENSSL=${ROOT}/tmp/openssl/apps/openssl
OPENSSL_CNF=${ROOT}/tmp/openssl/apps/openssl.cnf

NGINX_APP=${ROOT}/tmp/nginx/sbin/nginx
NGINX_CONF_DIR=${ROOT}/tmp/nginx/conf

##########################
# Generate ECDSA P-256 cert
##########################
# generate curve parameters

# generate server CSR
${OPENSSL} req -new -newkey ec:prime256v1.pem -keyout ${NGINX_CONF_DIR}/server.key -out ${NGINX_CONF_DIR}/server.csr -nodes -subj "/CN=oqstest CA ecdsap256" -config ${OPENSSL_CNF}

# generate server cert
${OPENSSL} x509 -req -in ${NGINX_CONF_DIR}/server.csr -out ${NGINX_CONF_DIR}/server.crt -CA ${NGINX_CONF_DIR}/CA.crt -CAkey ${NGINX_CONF_DIR}/CA.key -CAcreateserial -days 365

##########################
# Start nginx
##########################
cp nginx.conf ${NGINX_CONF_DIR}/nginx.conf
