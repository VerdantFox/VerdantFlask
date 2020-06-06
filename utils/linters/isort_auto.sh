#!/usr/bin/env bash

cd "$(dirname "$0")/../.." || return

echo "Autoformatting with isort"
isort -rc root "$@"
