#!/usr/bin/env bash
# Simple runner script to execute the project with Python3
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${HERE}/.."
SRC_DIR="${ROOT}/源码"

python3 "${SRC_DIR}/main.py"
