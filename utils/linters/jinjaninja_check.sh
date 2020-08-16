#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/../.." || return

echo "Running jinjaninja"
jinja-ninja src/templates "$@"
echo "jinjaninja passes..."
