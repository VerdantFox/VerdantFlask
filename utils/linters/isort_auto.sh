#!/usr/bin/env bash

cd "$(dirname "$0")/../.."

isort -rc root "$@"