#!/usr/bin/env bash
# Inicia o MacroWing a partir do código-fonte.
set -euo pipefail

cd "$(dirname "$0")"
exec python3 main.py "$@"