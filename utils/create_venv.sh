#!/usr/bin/env bash
# Meant to be run from Unix based system

set -euo pipefail
cd "$(dirname "$0")/.."

rm -rf venv

python3.8 -m venv venv

source venv/bin/activate
pip install --upgrade pip
pip install -U -r requirements.txt
