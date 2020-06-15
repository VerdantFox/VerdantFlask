#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/../.." || return

echo "Running bandit"
bandit -r -c .bandit.yaml -q . "$@"
echo "bandit passes..."
