#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/../.." || return

echo "Running black"
black . --check "$@"
echo "black passes..."
