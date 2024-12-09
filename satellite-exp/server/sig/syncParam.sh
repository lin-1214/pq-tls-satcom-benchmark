ROOT="$(dirname $(pwd))"
CLIENT_DIR="~/Desktop/pq-tls-benchmark/satellite-exp/client/sig/"

if [ $# -ne 1 ]; then
    echo "Usage: $0 <client_ip>"
    echo "check by ifconfig eth0"
    exit 1
fi

CLIENT_IP=$1

# copy CA cert with error handling
sudo scp "${ROOT}/kex/prime256v1.pem" "client@${CLIENT_IP}:${CLIENT_DIR}" || {
    echo "Error: Failed to copy prime256v1.pem"
    exit 1
}

sudo scp "${ROOT}/tmp/nginx/conf/ecdsap256_CA.crt" "client@${CLIENT_IP}:${CLIENT_DIR}" || {
    echo "Error: Failed to copy ecdsap256_CA.crt"
    exit 1
}

sudo scp "${ROOT}/tmp/nginx/conf/dilithium2_CA.crt" "client@${CLIENT_IP}:${CLIENT_DIR}" || {
    echo "Error: Failed to copy dilithium2_CA.key"
    exit 1
}