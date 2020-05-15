#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/.."

echo "Autoformatting with isort"
./utils/linters/isort_auto.sh
echo "Autoformatting with black"
./utils/linters/black_auto.sh
