#!/usr/bin/env bash

cd "$(dirname "$0")/../.."

npx prettier --write --list-different . "$@"
