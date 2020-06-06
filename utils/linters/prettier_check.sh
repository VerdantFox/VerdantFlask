#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/../.." || return

docker run --rm -v "$PWD:/work" tmknom/prettier --check . "$@"
echo "prettier passes..."
