#!/bin/bash
# set -ex

ROOT="$(dirname $(pwd))"

##########################
# Build s_timer
##########################
make s_timer.o

chmod 755 ./runClient.sh

