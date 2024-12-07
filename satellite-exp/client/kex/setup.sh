#!/bin/bash
# set -ex

ROOT="$(dirname $(pwd))"

OPENSSL=${ROOT}/tmp/openssl/apps/openssl
OPENSSL_CNF=${ROOT}/tmp/openssl/apps/openssl.cnf

##########################
# Build s_timer
##########################
make s_timer.o

##########################
# Generate ECDSA P-256 cert
##########################
# generate curve parameters
# need to be copy to server
${OPENSSL} ecparam -out prime256v1.pem -name prime256v1

# generate CA key and cert
${OPENSSL} req -x509 -new -newkey ec:prime256v1.pem -keyout CA.key -out CA.crt -nodes -subj "/CN=OQS test ecdsap256 CA" -days 365 -config ${OPENSSL_CNF}

