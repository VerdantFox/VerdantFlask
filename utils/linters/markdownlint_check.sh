#!/usr/bin/env bash
# markdownlint: run MarkdownLint on all .md sources in the project

set -euo pipefail
# Change directory to project root.
cd "$(dirname "$0")/../.." || return

# Normal markdownlint package does not support options
# and we need to ignore some locations
docker run --rm \
    --mount "type=bind,source=$(pwd),target=/app" \
    node bash -c \
        "cd /app && npm install --global markdownlint-cli && \
            markdownlint . \
            -i '**/node_modules/**' -i '**/venv/**' -i '**.mypy_cache**'"
echo "MarkdownLint passed on all known '.md' sources."
