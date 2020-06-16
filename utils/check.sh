#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/.."

./utils/pre_commit.sh
./utils/linters/jinjaninja_check.sh
./utils/pytest.sh --cov=root --cov-report=html
echo "Open coverage report at ./htmlcov/index.html"
