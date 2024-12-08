#!/bin/bash
# set -ex

ROOT="$(dirname $(pwd))"

OPENSSL=${ROOT}/tmp/openssl/apps/openssl
OPENSSL_CNF=${ROOT}/tmp/openssl/apps/openssl.cnf

##########################
# Build s_timer
##########################
make s_timer.o

chmod 755 ./runClient.sh

