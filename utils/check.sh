#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/.."

./utils/pre_commit.sh
./utils/linters/jinjaninja_check.sh
./utils/pytest.sh --tb=line
