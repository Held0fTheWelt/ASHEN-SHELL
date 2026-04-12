#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${ROOT}/world-engine"
exec python -m pytest tests/ -q --tb=short "$@"
