#!/usr/bin/env bash
# exit on error
set -o errexit

# Install and configure the Rust toolchain
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
export PATH="/opt/render/.cargo/bin:$PATH"

# Install Python dependencies
pip install -r requirements.txt