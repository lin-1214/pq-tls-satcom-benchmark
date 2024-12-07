#!/bin/bash
# set -ex
# build client environment

apt update
apt install -y git \
               build-essential \
               autoconf \
               automake \
               libtool \
               ninja-build \
               libssl-dev \
               libpcre3-dev \
               wget \
               python3-pip

pip3 install tqdm

CMAKE_VERSION=3.18
CMAKE_BUILD=3

mkdir -p tmp
cd tmp
ROOT=$(pwd)

# Fetch all the files we need
wget https://cmake.org/files/v${CMAKE_VERSION}/cmake-${CMAKE_VERSION}.${CMAKE_BUILD}-Linux-x86_64.sh
git clone --single-branch --branch pq-tls-experiment https://github.com/xvzcf/liboqs
git clone --single-branch --branch pq-tls-experiment https://github.com/xvzcf/openssl

# Install the latest CMake
mkdir cmake
sh cmake-${CMAKE_VERSION}.${CMAKE_BUILD}-Linux-x86_64.sh --skip-license --prefix=${ROOT}/cmake

# build liboqs
cd liboqs
mkdir build && cd build
${ROOT}/cmake/bin/cmake -GNinja -DCMAKE_INSTALL_PREFIX=${ROOT}/openssl/oqs ..
ninja && ninja install
