#!/bin/bash
# set -x

echo "Running signature experiment... ⚡"

ROOT="$(dirname $(pwd))"

for SIG in "ecdsap256" "dilithium2";
do
    # Run experiment
    sudo python3 ${ROOT}/sig/client.py ${SIG}

    # Wait a bit longer then server
    sleep 10
done