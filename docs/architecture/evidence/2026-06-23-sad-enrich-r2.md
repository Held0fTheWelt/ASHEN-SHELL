# SAD enrichment wave R2 — 2026-06-23

**Scope:** frontend, mcp-server, content-authority, administration-tool, story-runtime-core.

## Changes

| SAD | Decisions enriched / added |
| --- | --- |
| frontend | D1–D3 full blocks (ADR-0034, 0046, MVP5-001) |
| mcp-server | D1–D4 full blocks (ADR-0026–0028, 0048) |
| content-authority | D1–D2 expanded; **D3** added (ADR-0037 content locale) |
| administration-tool | D1–D2 expanded (ADR-0020, 0052) |
| story-runtime-core | D1 expanded; **D2** language adapter compat (ADR-0037) |

## Verification

```bash
python scripts/bootstrap_decision_registry.py
python scripts/architecture_link_audit.py --check
python -m pytest tests/gates/test_architecture_documentation_gate.py -q
```

## Next wave

R3: governance (remaining), security-governance, observability, quality-gates, ecosystem-topology (+ Langfuse/redaction absorption).
