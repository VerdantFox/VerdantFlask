#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/../.." || return

npx prettier --check . "$@"
echo "prettier passes..."
