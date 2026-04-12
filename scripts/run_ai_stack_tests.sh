#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}"
python tools/verify_goc_scene_identity_single_source.py
python -m pip install -q -e "./story_runtime_core" -e "./ai_stack[test]"
export PYTHONPATH="${ROOT}"
exec python -m pytest ai_stack/tests -q --tb=short "$@"
