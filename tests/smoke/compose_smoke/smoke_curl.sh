#!/usr/bin/env bash
# Minimal smoke: requires `docker compose up` from repo root first.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT"
curl -sf "http://127.0.0.1:8001/api/health" | head -c 400
echo
curl -sf "http://127.0.0.1:8000/api/v1/health" | head -c 400
echo
echo "smoke_curl.sh: OK"
