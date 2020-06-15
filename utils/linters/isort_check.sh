#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/../.." || return

echo "Running isort"
isort -rc -c root "$@"
echo "isort passes..."
