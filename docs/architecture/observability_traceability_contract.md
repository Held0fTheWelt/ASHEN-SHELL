# Observability and Traceability — Contract

**Status:** Active contract — 2026-04-26

---

## Required Trace Behavior

### Trace ID Propagation
- A trace_id is generated at session/turn start.
- The trace_id propagates across the relevant service boundary (backend → world-engine → ai_stack).
- The trace_id must appear in diagnostics envelope responses.

### Langfuse Trace Emission
- The configured trace adapter must **emit** actual trace/span payloads to Langfuse (or a configured sink).
- A local `trace_id` field in a response envelope is **not** sufficient proof of trace emission.
- Tests must use a fake Langfuse sink adapter that captures the actual emitted payload.
- The emitted payload must contain the trace_id, span data, and decision context.

### Disabled/Unavailable Sink
- If Langfuse is disabled or unavailable, the absence must be **diagnosed and reported**.
- Degraded tracing is not acceptable as silent success.
- The diagnostics endpoint must expose trace sink status.

---

## Diagnostics Contract

The administration-tool diagnostics page must expose:

| Field | Required |
|-------|----------|
| Guard outcome | YES |
| Rejected reasons | YES |
| Trace IDs | YES |
| Runtime state snapshot | YES |
| Fallback/degraded markers | YES |
| Backend availability status | YES |

### Anti-patterns

| Pattern | Status |
|---------|--------|
| Local trace_id alone claimed as Langfuse proof | FORBIDDEN |
| Mocked Langfuse sink claimed as observability proof | FORBIDDEN |
| Missing backend produces silent 200 | FORBIDDEN |
| Diagnostics endpoint returns empty/fake data | FORBIDDEN |

---

## Test Requirements for Observability

1. Use a **fake sink adapter** that captures real emitted trace payloads.
2. Assert the emitted payload contains the correct trace_id and span content.
3. Assert the diagnostics endpoint exposes guard outcomes, rejection reasons, and trace IDs.
4. Assert that unavailable Langfuse is diagnosed (not silently swallowed).

---

## ADR References

- ADR-mvp4-009: Langfuse traceable decisions
- ADR-mvp4-008: Diagnostics degradation semantics
- docs/ADR/LANGFUSE_OBSERVABILITY.md
- docs/ADR/OBSERVABILITY_REDACTION_POLICY.md
