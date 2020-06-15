#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/.."

./utils/linters/isort_check.sh
./utils/linters/black_check.sh
./utils/linters/flake8_check.sh
./utils/linters/mypy_check.sh
./utils/linters/jinjaninja_check.sh
./utils/linters/prettier_check.sh
./utils/linters/shellcheck_check.sh
# ./utils/linters/markdownlint_check.sh  # Too slow right now, need changes
./utils/linters/bandit_check.sh
./utils/pytest.sh --cov=root --cov-report=html
