#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/../.." || return

flake8 root "$@"
echo "flake8 passes..."
