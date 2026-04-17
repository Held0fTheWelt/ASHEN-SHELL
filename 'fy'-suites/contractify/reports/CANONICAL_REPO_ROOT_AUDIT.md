# Contractify canonical repo-root audit snapshot

This file is the **tracked human-readable canonical evidence snapshot** for repo-root Contractify review.

## Canonical evidence policy

- Tracked canonical review evidence is markdown, not `reports/*.json` exports.
- Local machine JSON exports remain ephemeral under `reports/_local_contract_audit.json` and `reports/_local_contract_discovery.json`.
- `reports/committed/*.hermetic-fixture.json` remains the tracked fixture-only layer for stable shape regression, not the live repo-root audit backing artifact.

## Canonical execution profile

- Manifest anchor: `fy-manifest.yaml`
- OpenAPI anchor: `docs/api/openapi.yaml`
- Contractify max contracts: **60**
- Canonical repo-root commands:
  - `python -m contractify.tools discover --json --out "'fy'-suites/contractify/reports/_local_contract_discovery.json"`
  - `python -m contractify.tools audit --json --out "'fy'-suites/contractify/reports/_local_contract_audit.json"`

## Fresh canonical discover snapshot

 - Contracts discovered: **60**
 - Projections discovered: **25**
 - Relations discovered: **310**
 - Manual unresolved areas kept explicit: **3**

## Fresh canonical audit snapshot

 - Contracts discovered in audit: **60**
 - Projections discovered in audit: **25**
 - Relations discovered in audit: **310**
 - Drift findings in audit: **0**
 - Conflicts in audit: **5**
 - Manual unresolved areas kept explicit: **3**

## Runtime/MVP family visibility from the canonical run

- `evidence_baseline`: CTR-EVIDENCE-BASELINE-GOVERNANCE, VER-SMOKE-DOCUMENTED-PATHS
- `goc`: CTR-GOC-VERTICAL-SLICE, CTR-GOC-CANONICAL-TURN, CTR-GOC-GATE-SCORING, VER-GOC-EXPERIENCE-SCORE-CLI-TEST
- `input_turn`: CTR-PLAYER-INPUT-INTERPRETATION, OBS-CORE-INPUT-INTERPRETER, VER-CORE-INPUT-INTERPRETER-TEST
- `publish_rag`: CTR-WRITERS-ROOM-PUBLISHING-FLOW, CTR-RAG-GOVERNANCE, OBS-BE-WRITERS-ROOM-ROUTES, OBS-AI-RAG, VER-BE-WRITERS-ROOM-ROUTES-TEST, VER-AI-RETRIEVAL-GOVERNANCE-SUMMARY-TEST
- `routing_observability`: CTR-AI-STORY-ROUTING-OBSERVATION, OBS-BE-MODEL-ROUTING-CONTRACTS, OBS-BE-OPERATOR-AUDIT, VER-BE-CROSS-SURFACE-OPERATOR-AUDIT-TEST
- `runtime_authority`: CTR-ADR-0001-RUNTIME-AUTHORITY, CTR-ADR-0002-BACKEND-SESSION-QUARANTINE, CTR-RUNTIME-AUTHORITY-STATE-FLOW, CTR-BACKEND-RUNTIME-CLASSIFICATION, CTR-CANONICAL-RUNTIME-CONTRACT, CTR-WORLD-ENGINE-SYSTEM-INTERACTIONS, CTR-RUNTIME-NARRATIVE-COMMIT, OBS-WE-WS-API, OBS-WE-COMMIT-MODELS, VER-WE-WS-TEST, VER-WE-NARRATIVE-COMMIT-TEST
- `scene_identity`: CTR-ADR-0003-SCENE-IDENTITY, OBS-AI-GOC-SCENE-IDENTITY, OBS-AI-GOC-YAML-AUTHORITY, VER-AI-GOC-SCENE-IDENTITY-TEST
- `testing`: CTR-TESTING-ORCHESTRATION, VER-TEST-RUNNER-CLI, VER-SMOKE-DOCUMENTED-PATHS

## Review workflow

1. Read this file for the canonical tracked stats and execution profile.
2. Read `runtime_mvp_attachment_report.md` for the bounded runtime/MVP narrative summary.
3. Read `../state/RUNTIME_MVP_SPINE_ATTACHMENT.md` for restartable state and unresolved areas.
4. Generate fresh local JSON only when you need machine-level detail or want to confirm that the tracked markdown snapshot is still current.
