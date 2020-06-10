#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/.." || return

pytest tests/ "$@"
echo "pytest passes..."
