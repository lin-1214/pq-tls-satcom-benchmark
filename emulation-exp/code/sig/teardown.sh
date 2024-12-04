#!/bin/bash
ROOT="$(dirname $(pwd))"

##########################
# Stop Mininet
##########################
sudo mn -c  # Clean up all Mininet instances

##########################
# Remove files
##########################
rm -f prime256v1.pem \
      s_timer.o
