#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/../.." || return

black . --check "$@"
echo "black passes..."
