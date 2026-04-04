#!/usr/bin/env bash
# BaGuaLu - Build package
set -e
cd "$(dirname "${BASH_SOURCE[0]}")"

PYTHON="${PYTHON:-python3}"

echo "=== BaGuaLu Build ==="

echo "[1/3] Cleaning old builds..."
rm -rf dist/ build/ *.egg-info bagualu.egg-info

echo "[2/3] Installing build tools..."
"$PYTHON" -m pip install --upgrade build -q

echo "[3/3] Building package..."
"$PYTHON" -m build

echo "=== Done! ==="
echo "Install with: pip install -e ."