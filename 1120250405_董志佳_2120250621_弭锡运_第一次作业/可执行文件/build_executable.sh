#!/usr/bin/env bash
# Build a standalone executable for macOS/Linux using PyInstaller.
# This script creates a temporary virtualenv, installs requirements, builds
# a one-file executable and moves it to this folder as `PageRank`.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${HERE}/.."
SRC_DIR="${ROOT}/源码"
MAIN="${SRC_DIR}/main.py"

if [ ! -f "$MAIN" ]; then
  echo "Error: $MAIN not found" >&2
  exit 1
fi

VENV_DIR="${HERE}/.build_env"
rm -rf "$VENV_DIR"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
python3 -m pip install --upgrade pip
pip install pyinstaller
if [ -f "${SRC_DIR}/requirements.txt" ]; then
  pip install -r "${SRC_DIR}/requirements.txt"
fi

# Build single-file executable
pyinstaller --onefile --name PageRank "$MAIN"


# Move final artifact to a safe output folder (do not remove it)
mkdir -p "$HERE/dist_bin"
if [ -f "dist/PageRank" ]; then
  mv dist/PageRank "$HERE/dist_bin/PageRank"
elif [ -f "dist/PageRank.exe" ]; then
  mv dist/PageRank.exe "$HERE/dist_bin/PageRank.exe"
fi

echo "Executable built at: ${HERE}/dist_bin/"
deactivate
rm -rf build __pycache__ "$VENV_DIR" PageRank.spec

exit 0
