#!/usr/bin/env bash
#
# MYPYP validates type hints in python files
# Looks for mypy.ini file in the present working directory

set -euo pipefail
cd "$(dirname "$0")/../.." || return

mypy
echo "mypy passes all sources listed in mypy.ini"
