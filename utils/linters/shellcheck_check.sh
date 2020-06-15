#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/../.." || return
sources="$(find utils -name "*.sh")"

echo "Running shellcheck"
# shellcheck disable=SC2086
docker run --rm --mount "type=bind,source=$(pwd),target=/mnt" \
    koalaman/shellcheck:stable $sources
echo "Shellcheck passed on all known '.sh' sources."
