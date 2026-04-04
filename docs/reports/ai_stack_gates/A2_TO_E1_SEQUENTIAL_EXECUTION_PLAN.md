# A2 to E1 Sequential Execution Plan

Date: 2026-04-04

## Execution contract

- Work strictly in order: `A2 -> B1 -> B2 -> C1 -> C2 -> D1 -> D2 -> E1`.
- Do not start the next milestone before the current milestone receives a `Pass` verdict.
- For each milestone run this fixed loop:
  1. Implement required behavior.
  2. Add or update tests.
  3. Run the most relevant tests.
  4. Write gate report in `docs/reports/ai_stack_gates/<MILESTONE>_GATE_REPORT.md`.
  5. Commit only when verdict is `Pass`, with the required commit message.
- If verdict is `Partial` or `Fail`, run a focused repair loop for the same milestone and re-run the full gate loop.
- If blocked by environment or dependency reality, report the blocker honestly and stop.

## Milestone gate checklist template

Use this checklist for each milestone before assigning `Pass`:

- Scope is implemented in live paths, not only scaffolds or docs.
- Tests cover required acceptance outcomes.
- Test commands and results are captured exactly in the gate report.
- Runtime behavior is traceable enough for the milestone scope.
- Limitations and non-goals are listed explicitly.

## Planned progression and likely focus

## A2 — World-Engine authoritative narrative host

- Ensure backend consumers read authoritative state/diagnostics from world-engine-hosted story sessions.
- Keep backend in policy/review/governance role for story runtime.
- Strengthen tests for committed progression coherence through backend-facing consumers.

## B1 — Real LangChain integration

- Confirm LangChain integration modules are used in live runtime-adjacent paths.
- Add/adjust tests for structured parsing and active invocation path assertions.

## B2 — Real LangGraph runtime execution

- Verify graph execution is active and hardened under healthy and degraded conditions.
- Ensure dependency behavior is explicit and test-stable.

## C1 — Real semantic persistent RAG

- Verify persistent corpus ingestion and semantically meaningful retrieval behavior.
- Validate runtime and authoring profiles in active paths.

## C2 — Capability workflow layer

- Verify tool invocation is real in workflows and governed by scope/permission checks.
- Confirm audit and failure semantics in tests and runtime outputs.

## D1 — Writers-Room structured HITL workflow

- Validate staged workflow state, artifact generation, retrieval use, and decision lifecycle.

## D2 — Improvement mutation/evaluation loop

- Validate baseline vs variant lineage, evaluation execution, evidence linkage, and recommendations.

## E1 — Observability, governance, evidence, release readiness

- Validate trace propagation and repaired-layer evidence signals end-to-end.
- Ensure governance/readiness outputs remain honest about `Pass` vs `Partial`.

## Stop conditions

- Stop immediately after any milestone that cannot honestly pass.
- Write the corresponding gate report with `Partial` or `Fail`, explicit reasons, and blocker details.
