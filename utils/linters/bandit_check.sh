#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/../.."

bandit -r -c .bandit.yaml -q . "$@"
