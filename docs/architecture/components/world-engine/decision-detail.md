# world-engine Decision Detail (SAD §9 supplement)

**Owner:** [world-engine SAD](architecture.md) · [Mechanism catalog](mechanism-catalog.md)

Normative decisions live in [architecture.md §9](architecture.md#9-architecture-decisions). This file holds tables, trace examples, and rollout checklists that are too long for §9 but useful for operators and implementers. Full retired ADR prose: [`docs/archive/adr-retired-2026/`](../../../archive/adr-retired-2026/).

---

## D4 — Director thin path (ADR-0062)

### Capability vocabulary (semantic names)

| Capability | Use |
| --- | --- |
| `narrator.location_transition.describe` | Movement to known location |
| `narrator.perception.describe` | In-world perception question |
| `narrator.clarification.describe` | Resolver uncertain / unknown target |
| `narrator.kanon_break_refusal.describe` | `kanon_break=true` |
| `actor_line.speech` | Player speech act |

### Operator diagnostics

`GET /api/story/sessions/{session_id}/thin-path-summary` plus administration-tool proxy `admin/world-engine/story/sessions/{id}/thin-path-summary`.

### Test matrix

| Layer | File |
| --- | --- |
| Composer | `ai_stack/tests/test_runtime_authority_aspects.py` |
| Graph shape | `ai_stack/tests/test_langgraph_runtime.py` |
| HTTP API | `world-engine/tests/test_thin_path_summary_api.py` |
| Live smoke (opt-in) | `tests/smoke/test_thin_path_pr_a_live_smoke.py` (`WOS_THIN_PATH_LIVE_SMOKE=1`) |

Per ADR-0039: assert path properties and contract fields, not fixture input strings.

---

## D3 — Live runtime commit semantics (ADR-0033)

### Observed false-green trace pattern

```text
world-engine.turn.execute → adapter=mock, fallback_used=True, quality=degraded
story.phase.model_invoke → success=True, adapter=mock, totalUsage=0
story.phase.commit → commit_applied=True, quality=degraded
```

Trace presence, routing, mock success, fallback completion, validation approval, or commit alone do **not** prove a live turn.

### Live-success checklist (all required)

1. Valid runtime profile + human role binding  
2. Real non-mock adapter  
3. Non-empty structured generation  
4. Validator approval + engine commit  
5. Non-empty frontend-visible story output  
6. Diagnostics distinguish live / mock / fallback / degraded / empty  

### Implementation pointers

| Area | Location |
| --- | --- |
| Gate | `ai_stack/story_runtime/live_runtime_commit_semantics.py` |
| Tests | `tests/gates/test_adr_live_runtime_commit_semantics_gate.py` |
| Traces | `world-engine/world_engine/middleware/trace_middleware.py` |

Related: [frontend D1](../frontend/architecture.md#d1-player-facing-narrative-shell-contract-mvp5) (shell readiness), [SAD D5](#d5-canonical-turn-lifecycle-adr-0038) (envelope join key).

---

## D5 — Canonical turn lifecycle (ADR-0038)

### TurnLifecycle states (ordered)

```text
received → interpreted → planned → generated_or_resolved → validated →
committed → persisted → projected → observed
```

Rules: no `projected`/`observed` without `committed` on the canonical player path; opening (turn 0) uses the same chain; short paths still persist one canonical row.

### Phased rollout (fixed order)

| Phase | Scope | Status |
| --- | --- | --- |
| A — Counter/projection parity | `/state`, backend `shell_state_view` | Implemented |
| B — `lifecycle_state` on envelope | `canonical_turn_lifecycle.py`, manager finalize | Implemented |
| C — Short-path convergence | recoverable + graph-rescue share persist helpers | Implemented |

Observed deviation: `canonical_turn_lifecycle.py` and the manager currently build projection before
the durable write (`projected → persisted`). The store result is now explicit and `persisted` is no
longer marked before the call returns, but sidecar effects still run too early. This is tracked as
[AR-V012](../../violations/README.md#ar-v012--persistence-and-lifecycle-order-diverge), not accepted
as an alternative lifecycle.

Evidence: `world-engine/tests/test_canonical_turn_lifecycle.py`, `tests/gates/test_canonical_turn_lifecycle_gate.py`, [UML d5](../../../../UML/Components/world-engine/decisions/d5-canonical-turn-lifecycle.md).

---

## D10 — Player session output language (ADR-0036)

| Topic | Rule |
| --- | --- |
| Field | `session_output_language` on `StorySession` (`de` \| `en` v1) |
| Launch | Selected at session create with template/role; stored on resume |
| Propagation | frontend → backend validate → world-engine → prompts/graph |
| Content | Character/place names may stay in-world language; narrative frame follows session language |
| No-op | When output language equals module authoring language, `translation_required=false` |

Error codes: `invalid_output_language`, `unsupported_language` (backend).

Open: turn-prompt language directive in `langgraph_runtime_executor.py` (opening path wired).

---

## D13 — Opening economy (ADR-0035)

| Part | Job |
| --- | --- |
| Background / premise | Off-stage fact pattern without mid-conflict dialogue dump |
| Into the scene | Room, ritual, social temperature; invitation to play |

Narrator adds staging imagination at hinges — does not repeat visible dialogue. Deterministic openings must not violate early-phase civility unless diagnostics label a stress scenario. GoC narrator-path: mechanical projection from `canonical_path`; no runtime-authored replacement prose.

Reference dramaturgy: `resources/carnage-2011.pdf` (maintainer reference, not shipped verbatim).

---

## D14 — Semantic input ingress (ADR-0055)

Graph ingress: `translate_player_input` **before** interpret/retrieve/action/model/validate/commit.

Produces `input_translation` record (languages, hashes, adapter status, optional `semantic_action` / `semantic_move`). Raw keyword guards are structural only (commands/meta), not semantic maps. Downstream consumers prefer normalized internal-language evidence when translation was required.

Authority: World-Engine turn graph output — backend previews are diagnostic only.

Evidence: [UML d14](../../../../UML/Components/world-engine/decisions/d14-semantic-input-ingress.md), `tests/gates/test_adr0055_semantic_ingress_gate.py`.
