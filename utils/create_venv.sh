#!/usr/bin/env bash
# Meant to be run from Unix based system

set -euo pipefail
cd "$(dirname "$0")/.." || return

rm -rf venv

python3.9 -m venv venv

# shellcheck disable=SC1091
source venv/bin/activate
pip install --upgrade pip
pip install -U -r requirements.txt
