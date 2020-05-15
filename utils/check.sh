#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/.."

./utils/linters/isort_check.sh
echo "isort passes..."
./utils/linters/black_check.sh
echo "black passes..."
./utils/linters/jinjaninja_check.sh
echo "jinjaninja passes..."
./utils/linters/flake8_check.sh
echo "flake8 passes..."
./utils/linters/bandit_check.sh
echo "bandit passes..."
