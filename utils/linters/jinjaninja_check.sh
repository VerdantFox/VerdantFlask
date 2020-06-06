#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/../.." || return

jinja-ninja root/templates "$@"
echo "jinjaninja passes..."
