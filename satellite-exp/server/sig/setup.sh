#!/bin/bash
# set -ex

ROOT="$(dirname $(pwd))"

OPENSSL=${ROOT}/tmp/openssl/apps/openssl
OPENSSL_CNF=${ROOT}/tmp/openssl/apps/openssl.cnf

NGINX_CONF_DIR=${ROOT}/tmp/nginx/conf

# generate curve parameters
${OPENSSL} ecparam -out prime256v1.pem -name prime256v1
# generate CA key and cert
${OPENSSL} req -x509 -new -newkey ec:prime256v1.pem -keyout ${NGINX_CONF_DIR}/ecdsap256_CA.key -out ${NGINX_CONF_DIR}/ecdsap256_CA.crt -nodes -subj "/CN=OQS test ecdsap256 CA" -days 365 -config ${OPENSSL_CNF}
# generate server CSR
${OPENSSL} req -new -newkey ec:prime256v1.pem -keyout ${NGINX_CONF_DIR}/ecdsap256_server.key -out ${NGINX_CONF_DIR}/ecdsap256_server.csr -nodes -subj "/CN=oqstest ecdsap256" -config ${OPENSSL_CNF}
# generate server cert
${OPENSSL} x509 -req -in ${NGINX_CONF_DIR}/ecdsap256_server.csr -out ${NGINX_CONF_DIR}/ecdsap256_server.crt -CA ${NGINX_CONF_DIR}/ecdsap256_CA.crt -CAkey ${NGINX_CONF_DIR}/ecdsap256_CA.key -CAcreateserial -days 365

## Generate all other certs
SIG="dilithium2"
# generate CA key and cert
${OPENSSL} req -x509 -new -newkey ${SIG} -keyout ${NGINX_CONF_DIR}/${SIG}_CA.key -out ${NGINX_CONF_DIR}/${SIG}_CA.crt -nodes -subj "/CN=OQS test ${SIG} CA" -days 365 -config ${OPENSSL_CNF}
# generate server CSR
${OPENSSL} req -new -newkey ${SIG} -keyout ${NGINX_CONF_DIR}/${SIG}_server.key -out ${NGINX_CONF_DIR}/${SIG}_server.csr -nodes -subj "/CN=oqstest ${SIG}" -config ${OPENSSL_CNF}
# generate server cert
${OPENSSL} x509 -req -in ${NGINX_CONF_DIR}/${SIG}_server.csr -out ${NGINX_CONF_DIR}/${SIG}_server.crt -CA ${NGINX_CONF_DIR}/${SIG}_CA.crt -CAkey ${NGINX_CONF_DIR}/${SIG}_CA.key -CAcreateserial -days 365

SIG="dilithium3"
# generate CA key and cert
${OPENSSL} req -x509 -new -newkey ${SIG} -keyout ${NGINX_CONF_DIR}/${SIG}_CA.key -out ${NGINX_CONF_DIR}/${SIG}_CA.crt -nodes -subj "/CN=OQS test ${SIG} CA" -days 365 -config ${OPENSSL_CNF}
# generate server CSR
${OPENSSL} req -new -newkey ${SIG} -keyout ${NGINX_CONF_DIR}/${SIG}_server.key -out ${NGINX_CONF_DIR}/${SIG}_server.csr -nodes -subj "/CN=oqstest ${SIG}" -config ${OPENSSL_CNF}
# generate server cert
${OPENSSL} x509 -req -in ${NGINX_CONF_DIR}/${SIG}_server.csr -out ${NGINX_CONF_DIR}/${SIG}_server.crt -CA ${NGINX_CONF_DIR}/${SIG}_CA.crt -CAkey ${NGINX_CONF_DIR}/${SIG}_CA.key -CAcreateserial -days 365

cp nginx.conf ${NGINX_CONF_DIR}/nginx.conf

chmod 755 ./syncParam.sh
chmod 755 ./runServer.sh

echo "[+]Execute syncParam.sh to sync CA key and cert to client"
echo "[+]Usage: ./syncParam.sh <client_ip>"