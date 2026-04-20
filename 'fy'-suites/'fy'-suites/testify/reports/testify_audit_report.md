# Testify audit report

## Summary

- **workflow_count**: `0`
- **runner_suite_count**: `0`
- **hub_script_count**: `33`
- **finding_count**: `3`
- **warning_count**: `1`
- **analyze_mode_count**: `39`
- **canonical_schema_export_count**: `22`

## Runner coverage

- `tests/run_tests.py` suites: `[]`
- `--suite all` order: `[]`

## Workflow coverage


## Public modes

- mode keys: `['analyze.api', 'analyze.closure', 'analyze.code_docs', 'analyze.contract', 'analyze.docker', 'analyze.docs', 'analyze.observability', 'analyze.quality', 'analyze.readiness', 'analyze.security', 'analyze.structure', 'analyze.templates', 'analyze.usability', 'explain.code_docs', 'explain.contract', 'explain.docs', 'generate.closure_pack', 'generate.context_pack', 'generate.docs', 'generate.packaging_prep', 'generate.surface_aliases', 'govern.production', 'govern.release', 'import.mvp', 'inspect.api', 'inspect.closure', 'inspect.code_docs', 'inspect.contract', 'inspect.docker', 'inspect.docs', 'inspect.observability', 'inspect.quality', 'inspect.readiness', 'inspect.security', 'inspect.structure', 'inspect.templates', 'inspect.usability', 'metrics.governor_status', 'metrics.report']`
- missing analyze modes: `[]`

## Schema export

- canonical source complete: `True`
- canonical export complete: `True`
- export count: `22`

## Strengths

- Mode registry exposes the required public analyze modes for contract, quality, code_docs, and docs.
- Canonical schema source files and exported schema bundle are both complete for the current evolution slice.

## Warnings

- No standalone frontend-tests.yml workflow detected; frontend quality currently relies on broader gates or local runner usage.

## Findings

- `TESTIFY-MISSING-WORKFLOWS` (high): Missing workflows: backend-tests.yml, admin-tests.yml, engine-tests.yml, ai-stack-tests.yml, quality-gate.yml, pre-deployment.yml, compose-smoke.yml
- `TESTIFY-MISSING-HUB-SCRIPTS` (high): Missing root pyproject suite scripts: wos-despag
- `TESTIFY-RUNNER-DRIFT` (medium): tests/run_tests.py no longer exposes the expected multi-suite targets.
