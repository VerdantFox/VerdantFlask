#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/../.."

isort -rc -c root "$@"
