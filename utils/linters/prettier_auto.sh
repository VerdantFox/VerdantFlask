#!/usr/bin/env bash

cd "$(dirname "$0")/../.." || return

echo "Autoformatting with prettier"
docker run --rm -v "$PWD:/work" tmknom/prettier --write --list-different . "$@"
