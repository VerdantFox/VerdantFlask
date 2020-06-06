#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/.."

./utils/linters/isort_auto.sh
./utils/linters/black_auto.sh
./utils/linters/prettier_auto.sh
