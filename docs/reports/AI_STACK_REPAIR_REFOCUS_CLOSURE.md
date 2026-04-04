# AI Stack Repair Refocus Closure Report

Date: 2026-04-04
Program: World of Shadows AI Stack Repair Refocus

## Final gate outcomes

| Milestone | Verdict | What was deepened |
|---|---|---|
| A1 | Pass | Frontend form field renamed from `operator_input` to `player_input`, aligning UX terminology with the backend API contract and the design principle that natural language is the primary input path |
| A2 | Pass | Three new integration tests proving natural language input with scene-id token extraction commits, leaves unchanged, or safely rejects progression through the `_extract_scene_candidate` path in `StoryRuntimeManager` |
| B1 | Pass | New cross-path test proving all three LangChain bridge types (runtime adapter, retriever, capability tool) are functional in a single test run, closing the risk that per-path regressions would be invisible |
| B2 | Pass | Two new tests explicitly documenting and enforcing that `build_seed_writers_room_graph()` and `build_seed_improvement_graph()` are minimal stubs — asserting absence of real workflow stage keys to prevent silent promotion |
| C1 | Pass | New test proving semantic expansion (paraphrase → canonical term → retrieval boost) lifts recall for non-obvious phrasing; the RAG layer is now demonstrably more than lexical-match-only |
| C2 | Pass | `wos.transcript.read` capability documented as aspirational in source code and proven invocable via test; it is no longer silently registered without verification |
| D1 | Pass | `patch_candidates` deepened to include `preview_summary` (human-readable description) and `confidence` (severity-derived float), turning abstract hint dicts into reviewable artifacts |
| D2 | Pass | Sandbox turn semantic classification replaced keyword-based guard rejection with `interpret_player_input`, exposing `interpreted_kind`, `interpretation_confidence`, and semantic rate metrics in experiment evaluation |
| E1 | Pass | Sparse environment test added proving the release-readiness API does not falsely claim `ready` and correctly names which specific areas are partial when no artifacts are present |

## What was deepened in the Refocus pass (vs already present after Repair)

The REPAIR pass established the structural scaffolding:
- Runtime turn graph with trace, repro metadata, model routing, and retrieval signals
- Writers-room workflow with persisted review artifacts and human review-state transitions
- Improvement loop with mutation plans, sandbox evaluation, and recommendation packages
- Capability layer with audit, access control, and invocation tracking
- Governance evidence bundles and release-readiness API

The REFOCUS pass deepened truthfulness and test coverage in each area:

1. **A1**: Closed a terminology gap — the UX said `operator_input` but the system meant `player_input`. The rename was cosmetic but removed a silent inconsistency that would confuse contributors.

2. **A2**: The authoritative narrative commit path for natural language input was wired but untested for the token-extraction branch. Three new tests prove the existing logic handles tokens correctly rather than requiring trust that it "should work."

3. **B1**: LangChain bridges were independently verified but never jointly verified. The cross-path test proves that all three bridges coexist and are functional in the same environment, not just in isolation.

4. **B2**: Seed graphs were tested for operational return but not for their limited scope. The new stub-documentation tests prevent future accidental misrepresentation of these graphs as multi-stage workflows.

5. **C1**: Semantic expansion was implemented but not proven end-to-end. The new test ingests content with canonical terms and queries with paraphrases, proving the expansion pipeline provides meaningful recall improvement.

6. **C2**: `wos.transcript.read` existed as a registered capability with no workflow usage and no test proving invocability. The refocus added honest source documentation ("aspirational capability") and a test proving the handler executes and fails with a typed error.

7. **D1**: Patch candidates were structured hints (issue reference + source path). The refocus materialized them with `preview_summary` and `confidence`, giving human reviewers enough signal to assess candidates without reading the raw issue data.

8. **D2**: Guard rejection in the improvement sandbox was keyword-based, which meant the metric was fragile and arbitrary. The refocus replaced it with semantic classification, producing honest `guard_reject_rate` values and three new semantic rate metrics.

9. **E1**: Release readiness was already reporting `partial` correctly. The refocus added area-level sparse-environment assertions, proving the system names *which* areas are partial and *why*, rather than just surfacing a top-level status.

## What now truly works end-to-end

- **Natural language primary path**: Player input flows through the frontend form (now correctly named `player_input`) → backend API → runtime turn graph → progression commit with authoritative scene tracking.
- **Semantic retrieval**: RAG retrieval resolves paraphrased queries to canonical terms, improving recall over lexical matching. Results are attributed, profiled, and domain-separated.
- **Capability layer**: Capabilities are registered, access-controlled, audit-logged, and invocable with typed errors on failure. The runtime turn graph exercises capabilities during execution.
- **Writers-room workflow**: Reviews produce persisted JSON artifacts with issues, patch candidates (including preview summaries and confidence scores), variant candidates, and human-controlled review-state transitions.
- **Improvement loop**: Variants are created, sandbox experiments run with semantic turn classification, evaluation metrics are computed (including semantic rates), and recommendation packages are produced with evidence bundles.
- **Governance evidence**: Session evidence bundles aggregate runtime, diagnostic, writers-room, and improvement signals into a single inspectable payload. Release-readiness reports explicitly name areas and partiality reasons.
- **LangChain/LangGraph integration**: Runtime adapter, retriever bridge, and capability tool bridge are all functional. Runtime turn graph is the operational path; seed graphs for writers-room and improvement are verified stubs.
- **Observability**: Trace IDs are propagated through all major paths. Audit logs emit structured dicts for workflow runs and bridge calls. Degraded paths (fallback model, graph errors) are surfaced in evidence bundles.

## What remains partial

- **Evidence persistence**: Artifact stores are local JSON files and in-process diagnostics. There is no distributed, signed, or immutable audit ledger. Evidence bundles are opportunistic best-effort lookups.
- **Readiness scoring**: Release-readiness is heuristic (artifact presence + key field checks), not a policy engine evaluating against defined governance criteria.
- **Patch candidate materialization**: `patch_candidates` contain preview summaries and confidence scores but not concrete before/after text diffs. Full materialization would require invoking the narrative generation model on target content.
- **Improvement sandbox fidelity**: The sandbox simulates story turns rather than executing real engine turns. Evaluation metrics are heuristics, not ground-truth quality measurements. `guard_reject_rate` has low discriminating power for typical natural-language inputs.
- **`wos.transcript.read` workflow integration**: The capability is registered, documented as aspirational, and proven invocable, but it is not invoked in any active workflow. Its value is latent.
- **Seed graphs**: `build_seed_writers_room_graph()` and `build_seed_improvement_graph()` remain single-node stubs. They are explicitly documented and test-enforced as stubs, not promoted to operational multi-stage graphs.
- **`runtime_observability` area independence**: The release-readiness `runtime_observability` area derives its status from writers-room review artifacts, not from a live runtime health query. In sparse environments, the area is partial for indistinct reasons.

## What remains intentionally out of scope

- Enterprise-grade vector infrastructure, external embedding services, or semantic similarity models replacing the BM25-like term-weighted retrieval currently in place.
- Full autonomous authorship or publishing pipelines without human review at each stage.
- Distributed policy engines and signed audit infrastructure (cryptographic immutability, audit ledger, tamper-evident logs).
- End-to-end automated release gate orchestration beyond the current governance API endpoints and report documents.
- Real-time model quality measurement (as opposed to heuristic sandbox evaluation).
- Adversarial robustness hardening for input interpretation or capability invocation paths.
- Calibration of confidence scores in patch candidates against retrieval relevance or generation quality signals.

## Stabilization readiness assessment

The repository is **ready for broader stabilization** in the following constrained sense:

- All nine REFOCUS milestones passed with no regressions.
- Every major repaired path (natural language input, semantic retrieval, capabilities, writers-room, improvement, governance evidence, release readiness) is covered by tests that verify not just that the path runs but that it behaves correctly under specific conditions including adversarial and sparse cases.
- The REPAIR-era structural scaffolding has been deepened by the REFOCUS pass to remove false impressions: stub graphs are documented as stubs, aspirational capabilities are labeled aspirational, terminology is consistent, semantic metrics are semantically derived, and sparse states report honestly.
- Remaining partiality is explicitly documented in gate reports, in source code comments, and in `known_partiality` fields returned by the governance API itself.

The repository is **not ready** for production deployment without:
- Replacing local JSON artifact stores with a durable, distributed persistence layer.
- Replacing the heuristic improvement sandbox with real story engine execution.
- Full materialization of patch candidates into reviewable diffs.

## Closure verdict

The AI Stack Repair Refocus program is complete. All nine milestones (A1 through E1) passed.
The Refocus pass fulfilled its purpose: it did not add new features but deepened the honesty
and test-verifiability of the infrastructure established in the Repair pass. The system now
surfaces partiality explicitly, names limitations in code and in API responses, and enforces
correct behavior under sparse and edge-case conditions. The repository is ready to enter a
broader stabilization phase with the understanding that infrastructure gaps (persistence,
sandbox fidelity, patch materialization) are documented, not hidden.
