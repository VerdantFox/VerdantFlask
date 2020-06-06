#!/usr/bin/env bash

cd "$(dirname "$0")/../.." || return

echo "Autoformatting with prettier"
npx prettier --write --list-different . "$@"
