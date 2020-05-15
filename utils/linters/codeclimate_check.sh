#!/usr/bin/env bash
# codeclimate: a helper script to run the CodeClimate CLI
set -euo pipefail

docker run \
    --interactive --tty --rm \
    --env CODECLIMATE_CODE="/$PWD" \
    --volume "/$PWD":/code \
    --volume //var/run/docker.sock:/var/run/docker.sock \
    --volume /tmp/cc:/tmp/cc \
    codeclimate/codeclimate "$@"
