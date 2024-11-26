#!/bin/bash
set -x

##########################
# Setup Mininet
##########################

sudo apt install -y openvswitch-switch \
                     openvswitch-common \
                     iproute2 \
                     net-tools \
                     wireshark \
                     curl

git clone https://github.com/mininet/mininet.git
cd mininet

sudo ./util/install.sh -a

sudo mn --test pingall
echo "✅ Notification: Mininet setup complete"