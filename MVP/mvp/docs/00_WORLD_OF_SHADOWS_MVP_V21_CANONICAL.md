# World of Shadows — MVP v21 Canonical Complete Package

Status: Canonical
Audience: Architecture, Runtime, Backend, Frontend, Administration Tool, QA, Release Engineering, Operations
Intent: This package closes the repeated audit gaps at MVP level **and** restores the missing implementation content that disappeared after v13.

---

## 0. Why v21 exists

v21 exists because later iterations improved the runtime-closure contract but regressed on package completeness.
The package must again contain:
- a canonical MVP definition
- modular supporting docs
- executable reference scaffold code
- executable reference tests
- UI mockups
- examples
- maps and explanatory material

This package therefore combines:
1. the stronger runtime-reife closure laws from the late audits, and
2. the fuller content shape from the earlier complete MVP packages.

---

## 1. Product definition

World of Shadows is a governed narrative runtime for interactive storytelling.

The player submits free-form input.
The engine may use AI to interpret, retrieve, plan, and generate candidate continuations.
Only the engine may commit canonical truth.
Only committed and rule-conformant story material may appear on the ordinary player route.

A complete MVP requires both:
- a strong constitutional contract, and
- a content-complete package with executable reference material.

---

## 2. Constitutional laws

### Law 1 — One truth boundary
The world-engine story runtime is the only canonical story authority.

### Law 2 — Commit is truth
Only committed output may count as canonical story state.

### Law 3 — Turn 0 is canonical
Authoritative story-session birth must either produce and commit an opening turn or fail explicitly.

### Law 4 — Ordinary player route purity
The ordinary player route may show only committed story output, transcript progression, and player-safe status.
It must not show operator JSON, privileged diagnostics, preview fields, alternate technical runtime panels, or privileged copy/export controls.

### Law 5 — Publish-bound authoritative birth
Ordinary player sessions must be born from a review-approved published artifact bundle, not from runtime-local compile fallback.

### Law 6 — Fail closed on authority seams
In hardened profiles, missing or invalid authority configuration must block authoritative birth or turn execution.
No silent default registry or default adapter fallback is allowed.

### Law 7 — Fail closed on internal auth
In hardened profiles, missing internal auth configuration must block protected internal routes.

### Law 8 — Degraded-safe stays explicit
`ACCEPT_DEGRADED_SAFE` may never be normalized into generic approval.

### Law 9 — Story persistence must be incident-visible
Corrupt story-session state may not be silently skipped in hardened profiles.

### Law 10 — Non-graph seams must remain testable
Storage, birth, restore, provenance, payload-contract, auth, and non-graph API seams must remain testable without heavy graph dependencies when those tests do not logically need them.

### Law 11 — Payloads must self-classify
Every exposed payload family must identify version, path class, audience, truth status, and generation metadata where applicable.

### Law 12 — Release honesty over closure theater
No PASS may be claimed if ordinary-player purity, publish-bound birth, fail-closed seams, story durability, or test/package credibility remain materially open.

---

## 3. Required package shape

A complete MVP package must contain all of the following:
- `docs/`
- `docs/easy/`
- `reference_scaffold/wos_mvp/`
- `reference_scaffold/tests/`
- `ui_mockups/`
- `examples/`

The package is incomplete if any of these are missing.

---

## 4. Runtime closure minimum

The MVP is only closure-ready when all of the following are true:
- world-engine is the only truth host
- ordinary player route renders committed reveal and transcript
- ordinary player route contains no privileged operator material
- story-session birth is publish-bound and provenance-complete
- Turn 0 is canonical and committed
- degraded-safe remains explicit
- story persistence is incident-visible
- payloads self-classify
- non-graph seams are executable without heavy graph imports

---

## 5. Memory live minimum

The live minimum that counts as real runtime maturity is:
- bounded continuity context
- narrative threads
- embedding-backed advisory retrieval
- post-commit continuity updates under governance
- partition-aware retrieval request discipline

The following remain preserved future capabilities and are not counted as live maturity unless executable in the runtime path:
- generic memory core across all domains
- alias / identity resolution
- same-slot discipline
- conflict records and supersession lifecycle
- advanced memory domains such as rumor, suppression, sacred, ontological
- full domain/carrier/threshold/effect machinery

---

## 6. Deliverable intent of the reference scaffold

The scaffold in `reference_scaffold/wos_mvp/` is not decorative.
It must provide executable reference code for the most important closure seams:
- publish-bound session birth
- payload classification
- player-route purity
- explicit degraded-safe semantics
- incident-visible persistence
- fail-closed profile logic
- non-graph seam testability

---

## 7. Acceptance rule

A package can only claim "complete MVP" if it is both:
- **contract-complete**, and
- **content-complete**.

v21 is the first post-v13 package whose explicit job is to restore both at once.
