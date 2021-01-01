#!/bin/bash
set -euo pipefail

if [[ "$ARCH" == "armhf" ]]; then
  rust_bin_path="$(stat --format %n /usr/local/rustup/toolchains/*-armv7-unknown-linux-gnueabihf/bin)"
  export PATH=${rust_bin_path}:$PATH
fi

exec cargo install librespot --version "${LIBRESPOT_VERSION}"