from __future__ import annotations

from pathlib import Path
import hashlib
import json

REPO = Path(__file__).resolve().parents[2]


def test_api_projection_governance_artifacts_exist() -> None:
    required = [
        'docs/api/openapi.yaml',
        'docs/api/README.md',
        'docs/api/REFERENCE.md',
        'docs/api/POSTMAN_COLLECTION.md',
        'docs/dev/api/openapi-and-api-explorer-strategy.md',
        'postman/README.md',
        'postman/postmanify-manifest.json',
        'governance/V24_API_PROJECTION_GOVERNANCE_LEDGER.md',
    ]
    for rel in required:
        assert (REPO / rel).is_file(), f'missing API projection artifact: {rel}'


def test_postman_manifest_matches_packaged_openapi_sha() -> None:
    manifest = json.loads((REPO / 'postman/postmanify-manifest.json').read_text(encoding='utf-8'))
    openapi_bytes = (REPO / 'docs/api/openapi.yaml').read_bytes()
    assert manifest['openapi_path'] == 'docs/api/openapi.yaml'
    assert manifest['openapi_sha256'] == hashlib.sha256(openapi_bytes).hexdigest()
