#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/../.." || return

echo "Running flake8"
flake8 root "$@"
echo "flake8 passes..."
