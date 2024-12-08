#!/bin/bash
# set -ex

echo "Running key exchange experiment on client... ⚡"

ROOT="$(dirname $(pwd))"

sudo python3 ${ROOT}/kex/client.py