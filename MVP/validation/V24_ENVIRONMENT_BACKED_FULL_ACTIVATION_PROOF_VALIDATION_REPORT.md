# V24 Environment-Backed Full Activation Proof Validation Report

## Summary

This wave closed the remaining reproducibility gap around the backend ↔ world-engine publish-to-runtime activation proof in the current package validation environment.

The previously strengthened activation semantics were not changed. The remaining work in this wave was limited to making the proof path reproducibly executable here and recording exact evidence.

## Targeted blocker

The remaining blocker was not the activation semantics themselves.
It was proof reproducibility in the actual audit/container environment.

Two concrete sub-blockers remained:

1. The backend integration proof path still depended on a locally reconstructed package environment that was not codified in the package.
2. `uvicorn` was a real dependency of the backend live play-service integration tests, but it was not declared in the backend test extras, making package-level reproduction weaker than the already-hardened runtime path.

## Package changes

### 1. Backend test dependency declaration

`backend/pyproject.toml`
- added `uvicorn>=0.30,<1` to the `test` and `dev` optional dependency groups

This does not change runtime semantics. It only makes the live play-service integration proof path more honestly declared from the backend test surface that actually launches the world-engine process.

### 2. Reproducible proof runner

`scripts/run_live_activation_proof_validation.py`
- added a narrow validation runner that:
  - reads the package's existing `pyproject.toml` files,
  - installs only the third-party dependencies needed for the live activation proof path,
  - runs the authoritative runtime-manager proof,
  - runs the backend live play-service integration proof.

The runner intentionally avoids editable-installing both backend and world-engine because both projects expose a top-level `app` package and the tests already rely on project-local `PYTHONPATH`/working-directory behavior.

## Validation commands executed in this wave

### Direct validation before packaging the runner

```bash
cd /mnt/data/wos_work/world-engine
python -m pytest -q tests/test_runtime_manager.py -q

cd /mnt/data/wos_work/backend
python -m pytest -q tests/test_backend_playservice_integration.py -q
```

Results:
- `world-engine/tests/test_runtime_manager.py`: PASS (`12 passed`)
- `backend/tests/test_backend_playservice_integration.py`: PASS (`3 passed`)

### Reproducibility validation through the new runner

```bash
cd /mnt/data/wos_work
python scripts/run_live_activation_proof_validation.py
```

The runner performed:

```bash
python -m pip install \
  flask>=3.0.6,<4 \
  flask-cors>=4.0.0,<5 \
  flask-sqlalchemy>=3.1.0,<4 \
  flask-jwt-extended>=4.6.0,<5 \
  flask-limiter>=3.5.0,<4 \
  flask-migrate>=4.0.0,<5 \
  flask-wtf>=1.2.1,<2 \
  flask-mail>=0.10.0,<1 \
  werkzeug>=3.1.5,<4 \
  alembic>=1.18.0,<2 \
  python-dotenv>=1.0.0,<2 \
  markdown>=3.5.0,<4 \
  bleach>=6.0.0,<7 \
  httpx>=0.27.0,<1 \
  email-validator>=2.0.0,<3 \
  pydantic>=2.0.0,<3 \
  fastapi>=0.115.0,<1 \
  requests>=2.31.0,<3 \
  pyyaml>=6.0,<7 \
  marshmallow>=3.20.0,<4 \
  cryptography>=45.0.7,<47 \
  pyOpenSSL>=25.3.0,<27 \
  pytest>=7.0,<9 \
  pytest-asyncio>=0.21,<1 \
  pytest-cov>=4.0,<6 \
  pytest-timeout>=2.1 \
  anyio>=4.0,<5 \
  uvicorn>=0.30,<1

cd world-engine && python -m pytest -q tests/test_runtime_manager.py -q
cd backend && python -m pytest -q tests/test_backend_playservice_integration.py -q
```

Result:
- runner completed successfully
- runtime-manager proof: PASS
- live backend ↔ play-service activation proof: PASS

## What now counts as environment-backed proof

The following proof now ran in this environment:

1. world-engine runtime manager proof for published override activation, fallback reversion, and activation-time provenance
2. backend live play-service integration proof that:
   - starts the real world-engine process via `uvicorn`
   - reads canonical published content from the backend feed path
   - activates published content through the bridge path
   - preserves activation provenance for existing runs after unpublish/removal
   - falls back explicitly for new runs after removal

## Remaining bounded residue

No remaining blocker in this wave prevents the targeted activation proof from being reproduced in this environment anymore.

Bounded residue that still exists, but no longer blocks this wave:
- optional story-runtime graph availability remains separate from this proof path
- broader full-stack story-runtime validation is still outside the scope of this activation-proof wave

## Closure judgment

Closed.

Why:
- the strongest backend ↔ world-engine activation proof now executes in this environment,
- the package contains a reproducible proof runner for that path,
- the missing declaration around `uvicorn` was narrowed and fixed on the backend test surface,
- and no publish/runtime semantics or authority boundaries were changed.
