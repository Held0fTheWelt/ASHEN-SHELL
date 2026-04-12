# Run ai_stack tests from repo root (PYTHONPATH = repo). Installs editable deps like CI.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
python tools/verify_goc_scene_identity_single_source.py
python -m pip install -q -e "./story_runtime_core" -e "./ai_stack[test]"
$env:PYTHONPATH = $root
python -m pytest ai_stack/tests -q --tb=short @args
