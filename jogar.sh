#!/bin/bash
set -eu
cd "$(dirname "$(readlink -f "$0")")"
mkdir -p logs
exec python3 source/run.py > logs/jogo.log 2>&1
