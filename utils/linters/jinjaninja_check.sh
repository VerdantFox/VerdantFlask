#!/usr/bin/env bash

set -euo pipefail
cd "$(dirname "$0")/../.."

jinja-ninja root/templates "$@"
