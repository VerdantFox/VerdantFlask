#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/../.."

flake8 root "$@"
