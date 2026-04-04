@echo off
REM BaGuaLu - Build package (Windows)
setlocal enabledelayedexpansion

echo === BaGuaLu Build ===

echo [1/3] Cleaning old builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist bagualu.egg-info rmdir /s /q bagualu.egg-info

echo [2/3] Installing build tools...
python -m pip install --upgrade build -q

echo [3/3] Building package...
python -m build

echo === Done! ===
echo Install with: pip install -e .