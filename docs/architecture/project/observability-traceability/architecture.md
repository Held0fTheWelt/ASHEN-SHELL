---
id: SAD-PROJECT-OBSERVABILITY-TRACEABILITY
status: accepted
type: project-sad
owns-adrs: []
uml-package: UML/Project/mvp-live-runtime-completion
---
# Observability & Traceability — Software Architecture (arc42, project-wide)

**Last reconciled:** `2026-06-23`

## 1. Introduction & Goals

Langfuse tracing, diagnostics snapshots, redaction policy, and MVP4 observability gates prove what the
live runtime actually did—not merely that code ran.

Observability answers operator questions: was the adapter real or mock, did visible output exist, which
decisions were trace-linked. Redaction rules prevent leaking secrets into traces while keeping enough
structure for narrative gov panels and post-turn audits.

## 2. Constraints

Redaction policy: [observability SAD D7](#d7-observability-redaction-and-trace-correlation-policy), [observability SAD D6](#d6-langfuse-as-canonical-airuntime-observability-provider).

## 3. Context & Scope

Spans world-engine middleware, backend routes, ai_stack adapters, frontend readiness (partial).

## 4. Solution Strategy

- Trace turn execute with adapter kind and visible output signals (ADR-0033).
- MVP4 operational evidence in `tests/reports/MVP_Live_Runtime_Completion/`.

## 5. Building Block View

| Block | Path |
| --- | --- |
| Trace middleware | `world-engine/app/middleware/trace_middleware.py` |
| Langfuse adapters | `ai_stack/langfuse/` |
| Evaluator catalog | `ai_stack/quality_lab/` |

## 6. Runtime View

`world-engine.turn.execute` span → scores at observation and trace level.

## 7. Deployment View

Langfuse optional via env; deterministic export paths for CI.

## 8. Crosscutting Concepts

Langfuse is the canonical AI/runtime observability provider when enabled; redaction policy applies before trace export.

**Langfuse policy (ex-LANGFUSE_OBSERVABILITY).** # ADR: Langfuse as Canonical AI/Runtime Observability Provider

**Status**: APPROVED

**Date**: 2026-04-24

**Decision Makers**: Runtime Architecture, DevOps, Observability Engineering

---

## Context

World of Shadows executes complex multi-turn AI narratives with:
- Dynamic actor selection and responder nomination
- Conditional generation paths (fallback, degradation, retry)
- Real-time validation with field-level guards
- Structured output parsing with recovery branches
- Story window packaging with visibility markers
- Vitality telemetry and passivity detection

Current diagnostics are:
- Session audit logs (after-the-fact, not correlated)
- Runtime turn contracts (in-memory, not persisted)
- Administration Tool readiness views (static config only)
- No unified trace correlation across services

Operators need to answer:
- Which AI model was actually invoked for this turn?
- What context was retrieved and sent?
- Why was the generated output rejected/degraded?
- Which service made which decision?
- What was the full execution trace for session X?

---

## Decision

**Implement Langfuse as the canonical observability provider for:**
- AI invocation tracing (provider, model, prompt, completion, latency, tokens)
- Retrieval tracing (query, context window, document count, failures)
- Validation/commit tracing (status, rejection reasons, guard outcomes)
- Runtime diagnostics correlation (session_id → trace_id → operator inspection)
- Administration Tool operator surfaces (enabled/disabled status, trace links)
- Release-readiness gates (Langfuse configured or explicitly disabled)

**Requirements:**
- Optional and disabled by default (no credentials required for local dev)
- One canonical adapter layer (no scattered direct Langfuse calls)
- Safe: graceful degradation if disabled or credentials missing
- Secure: redact secrets before tracing
- Correlated: all traces link to session/run/turn/module/scene

---

**Redaction policy (ex-OBSERVABILITY_REDACTION_POLICY).** # ADR: Observability Redaction and Trace Correlation Policy

**Status**: APPROVED

**Date**: 2026-04-24

---

Player input observability fields on spans (ADR-0033 §13.6).

## 9. Architecture Decisions

| ID | Title | Migrated from |
| --- | --- | --- |
| D1 | Observability diagnostics MVP4 | MVP4-001 |
| D2 | Langfuse integration | MVP4-002 |
| D3 | Traceable decisions | MVP4-009 |
| D4 | Diagnostics degradation semantics | MVP4-008 |
| D5 | Quality lab MCP diagnostics | ADR-0040 |

### D1: Observability diagnostics MVP4

**Status:** Accepted · **Migrated from:** MVP4-001

**Context.** MVP4 live runtime required operator-visible diagnostics beyond pytest green; turn failures needed structured evidence for support, regression triage, and narrative governance review without raw log diving.

**Decision.** MVP4 requires operational diagnostics evidence beyond unit test pass/fail.

**Consequences.** MVP4 gates and operator surfaces must expose diagnostics envelopes on live turns.

**Evidence.** [`tests/gates/test_goc_mvp04_observability_diagnostics_gate.py`](../../../../tests/gates/test_goc_mvp04_observability_diagnostics_gate.py).

### D2: Langfuse integration

**Status:** Accepted · **Migrated from:** MVP4-002

**Context.** Without correlated traces, AI/runtime failures could not be tied to a single turn, adapter stage, or visible player output during live sessions or Langfuse-backed quality reviews.

**Decision.** Langfuse spans correlate turns, adapters, and visible output signals when configured.

**Consequences.** Trace middleware and adapters must propagate trace ids without claiming success when Langfuse is disabled.

**Evidence.** [`world-engine/app/middleware/trace_middleware.py`](../../../../world-engine/app/middleware/trace_middleware.py).

### D3: Traceable decisions

**Status:** Accepted · **Migrated from:** MVP4-009

**Context.** Operators auditing narrative governance need links from runtime decisions to traces and logs without reconstructing context from raw engine state dumps or ad-hoc spreadsheet exports.

**Decision.** Decision logs and traces must be linkable for operator audit.

**Consequences.** Narrative governance APIs must return stable correlation ids for the last committed turn.

**Evidence.** MVP4 ADR evidence under `tests/reports/MVP_Live_Runtime_Completion/`.

### D4: Diagnostics degradation semantics

**Status:** Accepted · **Migrated from:** MVP4-008

**Context.** Degraded adapter paths previously looked like success to clients; explicit diagnostics must surface partial failure without claiming live_success or hiding blocked-turn semantics from operators.

**Decision.** Degraded adapter paths expose explicit diagnostics without false live_success.

**Consequences.** Clients and operators must see degradation reasons in diagnostics envelopes and UML degraded sequences.

**Evidence.** [world-engine degraded sequence](../../../../UML/Components/world-engine/sequence/world-engine-degraded-turn-sequence.md).

### D5: Quality lab MCP diagnostics

**Status:** Accepted · **Migrated from:** ADR-0040

**Context.** Quality Lab MCP must expose judge-guided diagnostics within the same redaction and trace policy as production Langfuse spans so local experiments do not leak PII or bypass governance.

**Decision.** Quality Lab MCP exposes bounded judge-guided diagnostics aligned with trace policy.

**Consequences.** MCP diagnostic tools must not bypass redaction rules defined in observability D7.

**Evidence.** [ai-stack SAD D2](../../components/ai-stack/architecture.md#d2-quality-lab-mcp-runtime-diagnostics-and-judge-guided-improvement).

### D6: Langfuse as Canonical AI/Runtime Observability Provider

**Status:** APPROVED
**Origin:** LANGFUSE-OBSERVABILITY (retired 2026-06-23)

**Context.** World of Shadows executes complex multi-turn AI narratives with:
- Dynamic actor selection and responder nomination
- Conditional generation paths (fallback, degradation, retry)
- Real-time validation with field-level guards
- Structured output parsing with recovery branches
- Story window packaging with visibility markers
- Vitality telemetry and passivity detection

Current diagnostics are:
- Session audit logs (after-the-fact, not correlated)
- Runtime turn contracts (in-memory, not persisted)
- Administration Tool readiness views (static config only)
- No unified trace correlation across services

Operators need to answer:
- Which AI model was actually invoked for this turn?
- What context was retrieved and sent?
- Why was the generated output rejected/degraded?
- Which service made which decision?
- What was the full execution trace for session X?

---

**Decision.** **Implement Langfuse as the canonical observability provider for:**
- AI invocation tracing (provider, model, prompt, completion, latency, tokens)
- Retrieval tracing (query, context window, document count, failures)
- Validation/commit tracing (status, rejection reasons, guard outcomes)
- Runtime diagnostics correlation (session_id → trace_id → operator inspection)
- Administration Tool operator surfaces (enabled/disabled status, trace links)
- Release-readiness gates (Langfuse configured or explicitly disabled)

**Requirements:**
- Optional and disabled by default (no credentials required for local dev)
- One canonical adapter layer (no scattered direct Langfuse calls)
- Safe: graceful degradation if disabled or credentials missing
- Secure: redact secrets before tracing
- Correlated: all traces link to session/run/turn/module/scene

---

**Consequences.** ### Benefits
- **Observability**: Complete trace of AI decision-making and runtime behavior
- **Correlation**: Single trace_id links session → turn → provider → rejection → operator inspection
- **Privacy**: Redaction layer prevents secrets from being exposed
- **Optional**: Langfuse disabled is valid; no credentials required for development
- **Operator-friendly**: Administration Tool shows status and trace links

### Risks
- Langfuse client adds ~50KB to dependencies
- Network latency if Langfuse is slow (mitigated by sample_rate and async flush)
- Trace storage costs if enabled in production (offset by diagnostic value)
- Requires careful redaction to avoid leaking player data

### Mitigation
- Langfuse disabled by default; must be explicitly enabled
- No credentials required if disabled
- Redaction in strict mode by default (sanitizes prompts/outputs)
- Tests validate no-op mode doesn't break runtime
- Sample rate configurable

---

**Affected services.** 1. **backend**
   - config.py: Add LangfuseConfig
   - observability/langfuse_adapter.py: Canonical adapter
   - factory_app.py: Initialize Langfuse on startup
   - api/v1/game_routes.py: Trace player session creation
   - api/v1/play_qa_diagnostics_routes.py: Include trace IDs in diagnostics

2. **world-engine/play-service**
   - config.py: Add Langfuse settings
   - app/story_runtime/manager.py: Trace turn execution, AI invocation, commit
   - app/story_runtime/commit_models.py: Trace validation outcomes

3. **ai_stack**
   - langgraph_runtime_executor.py: Trace model invocation, fallback paths
   - runtime_quality_semantics.py: Trace quality assessment
   - telemetry/actor_survival_telemetry.py: Include trace_id in vitality telemetry

4. **frontend** (optional)
   - routes_play.py: Include trace_id in diagnostics view (operator-facing)

5. **administration-tool**
   - observability/langfuse_status.py: Readiness checks, current config
   - templates/diagnostics.html: Show trace links for recent turns

6. **.env.example** and Docker Compose
   - Add all Langfuse env vars with defaults

---

**Evidence.** `docs/architecture/project/observability-traceability/architecture.md#d6-langfuse-as-canonical-airuntime-observability-provider` (archived — see `docs/archive/adr-retired-2026/`)

### D7: Observability Redaction and Trace Correlation Policy

**Status:** APPROVED
**Origin:** OBSERVABILITY-REDACTION-POLICY (retired 2026-06-23)

**Context.** Langfuse traces will contain:
- Prompts sent to AI models (may contain context about players/world)
- Retrieved documents (context from database)
- Validation decisions (field-level changes)
- Runtime metadata (session IDs, turn numbers, module IDs)
- Generated outputs (AI-produced narrative)

**Privacy concern**: Traces could expose:
- Player names or identifying information
- Plot details not yet revealed
- Session-specific context that should remain private
- Internal system details (database queries, row IDs)

---

**Decision.** ### What IS Captured

With LANGFUSE_CAPTURE_PROMPTS=true:
- Prompts sent to LLM (includes context summary, not raw unstructured data)
- Model name, provider name
- Token counts
- Latency metrics
- Validation status and reasons

With LANGFUSE_CAPTURE_OUTPUTS=true:
- LLM completion text (AI-generated narrative)
- Structured output (parsed spoken_lines, action_lines with actor IDs)
- Parsing errors if any

With LANGFUSE_CAPTURE_RETRIEVAL=true (default false):
- Retrieval query (what was asked)
- Document count retrieved
- First 5 documents only (metadata, not full text)
- Retrieval failures

### What is NEVER Captured

- Player real names (use player_id instead)
- Authentication tokens, cookies, session secrets
- Database passwords or service credentials
- API keys or bearer tokens
- Private user metadata beyond pseudonymized IDs
- Raw unredacted passwords or PII

### Redaction Behavior

**Strict Mode** (default):
- All values matching key patterns like "password", "token", "secret", "auth", "apikey", "bearer", "cookie" are redacted to "***" or partially masked
- Prompts/outputs are captured but NOT stored unencrypted
- All metadata keys are checked; any with sensitive names are masked

**Relaxed Mode**:
- Same as strict but allows full prompts/outputs if explicitly enabled
- Redacts only explicitly marked secrets (env vars, creds)

**None Mode**:
- No redaction (only for fully disconnected local/test environments)
- Not recommended for production

---

**Evidence.** `docs/architecture/project/observability-traceability/architecture.md#d7-observability-redaction-and-trace-correlation-policy` (archived — see `docs/archive/adr-retired-2026/`)
## 10. Quality Requirements

`tests/gates/test_goc_mvp04_observability_diagnostics_gate.py`, `world-engine/tests/test_trace_middleware.py`.

## 11. Risks & Technical Debt

Not all diagnostic fields on every adapter path.

## 12. Glossary

| Term | Meaning |
| --- | --- |
| live_success | Gate flag for real visible story output |
