# PQC-TLS Satellite Performance Testing

A research project to evaluate the performance impact of post-quantum cryptography (PQC) algorithms on TLS handshake times in satellite network environments.

## Overview

This repository contains tools and experiments for measuring how post-quantum cryptographic algorithms affect TLS handshake latency when operating over satellite links. The research focuses on understanding the practical implications of implementing quantum-resistant security in high-latency satellite communications.

## Features

- TLS handshake timing measurements for various PQC algorithms
- Satellite network condition simulation
- Comparison between classical and post-quantum TLS performance
- Support for multiple NIST PQC candidates
- Network latency and bandwidth analysis tools

## Environment Setup

### Prerequisites

- OpenSSL with PQC support
- Network emulation tools (e.g., tc, netem)
- Python 3.8+
- Satellite link simulator

### Installation
