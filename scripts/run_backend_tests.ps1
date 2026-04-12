# Run backend pytest from backend/ (correct app package). Pass extra args to pytest after '--'.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $root "backend")
python -m pytest tests/ -q --tb=short @args
