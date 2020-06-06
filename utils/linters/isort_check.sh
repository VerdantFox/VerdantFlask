#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/../.." || return

isort -rc -c root "$@"
echo "isort passes..."
