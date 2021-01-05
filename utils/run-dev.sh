#!/usr/bin/env bash

cd "$(dirname "$0")/.." || return
echo "Access site on localhost: http://localhost:5000/"
echo "Access site at ip address: http://$(hostname -I | awk '{print $1;}'):5000/"
python run.py
