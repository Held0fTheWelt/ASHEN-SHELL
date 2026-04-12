# Run world-engine pytest from world-engine/ (correct app package).
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $root "world-engine")
python -m pytest tests/ -q --tb=short @args
