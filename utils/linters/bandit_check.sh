#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/../.." || return

bandit -r -c .bandit.yaml -q . "$@"
echo "bandit passes..."
