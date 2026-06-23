---
id: SAD-PROJECT-QUALITY-GATES
status: accepted
type: project-sad
owns-adrs: [ADR-0039]
uml-package: UML/Project/mvp-live-runtime-completion
links:
  - tests/run_tests.py
  - tests/gates/
---
# Quality Gates & Validation — Software Architecture (arc42, project-wide)

**System:** Quality Gates · **Last reconciled:** `2026-06-23`

## 1. Introduction & Goals

Maps automated gates to architecture contracts and MVP evidence so "green CI" means enforced boundaries,
not cosmetic tests.

### 1.1 Quality goals

| Goal | Scenario |
| --- | --- |
| Oracle integrity | Gates read shared fixtures/constants, not story-specific hardcoding |
| MVP traceability | MVP operational evidence links from SAD to `tests/reports/` |
| Single runner | All suites invoked via `tests/run_tests.py` |

## 2. Constraints

- Canonical runner: `python tests/run_tests.py` ([CLAUDE.md](../../../../CLAUDE.md)).
- Architecture gates: `python -m pytest tests/gates/`.
- Integration tests must not mock live stack for observability features (project rule).

## 3. Context & Scope

Covers `tests/gates/`, suite flags, GitHub `architecture-gates` jobs, and MVP locator/evidence artifacts.

## 4. Solution Strategy

- Each gate file names the contract/ADR it protects.
- New SAD decisions that are testable must add or extend a gate row in this SAD §10.
- Documentation gate validates SAD/UML rollout ([`test_architecture_documentation_gate.py`](../../../tests/gates/test_architecture_documentation_gate.py)).

## 5. Building Block View

| Gate module | Protects |
| --- | --- |
| `test_goc_mvp01_mvp02_foundation_gate.py` | Runtime authority foundation |
| `test_adr_live_runtime_commit_semantics_gate.py` | ADR-0033 semantics |
| `test_goc_mvp03_live_dramatic_scene_simulator_gate.py` | LDSS path |
| `test_goc_mvp04_observability_diagnostics_gate.py` | MVP4 observability |
| `test_adr0039_*` | Oracle governance |
| `test_architecture_documentation_gate.py` | SAD/UML completeness |

## 6. Runtime View

CI workflow invokes `pytest tests/gates` on engine/pre-deployment paths ([gate oracle inventory](../../../governance/gate_oracle_tightness_inventory.md)).

## 7. Deployment View

Gates run in GitHub Actions and locally from repo root with venv + deps installed.

## 8. Crosscutting Concepts

MVP reports: `tests/reports/MVP_Live_Runtime_Completion/MVP*_OPERATIONAL_EVIDENCE.md`.

## 9. Architecture Decisions

### D1: Gate Tests Must Not Use Hardcoded Oracles (No “Example-Shaped” Bypasses)

**Status:** ** Accepted
**Origin:** ADR-0039 (retired 2026-06-23)

**Context.** We repeatedly observe an anti-pattern when fixing failing gates or tightening checks:

1. A gate or regression test fails for a **legitimate semantic reason** (contract drift, missing integration, wrong authority surface, incomplete pipeline).
2. Instead of fixing the **system under test** (or the **contract**), a contributor “fixes green” by **hardcoding the expected outcome** that makes the test pass: literal strings, magic IDs, fixed counts, brittle substrings, or one-off payloads copied from a single local run.
3. The test then encodes **the symptom description** (what the ticket said) rather than the **invariant** (what must always be true). Semantically equivalent correct behavior can still fail; slightly wrong behavior can pass if it matches the hardcoded needle.

This produces **false confidence**: CI is green while the product regresses, because the test is a mirror of a workaround, not a guardrail. It also **ossifies accidents**: the hardcoded value becomes undeclared product truth that diverges from canonical modules, OpenAPI, ADRs, or runtime authority.

Gates exist to prove that **promotion criteria** hold under change. If a gate test’s oracle is arbitrary hardcoded material, the gate becomes a **lint rule for the patch author’s memory**, not a proof of system behavior.

### Tight coupling to ADR-0008 and ADR-0009

- **[ADR-0008](../../../archive/adr-retired-2026/adr-0008-validation-strategy-explicit-configurable.md)** defines *how strongly* runtime output is validated. Tests that claim to protect that behavior must not substitute hardcoded example text for real contract checks—otherwise the strategy toggle becomes theatre: CI can stay green while semantics drift.
- **[ADR-0009](../../../archive/adr-retired-2026/adr-0009-evaluation-is-a-promotion-gate.md)** defines that promotion is not automatic from artifact existence; evaluation evidence matters. When evaluation gate tests land, they are especially vulnerable to “assert this exact score text” shortcuts; this ADR forbids that pattern so evaluation remains a **genuine promotion signal**.

---

**Decision.** **Normative rule — binding for gate tests and promotion-style regression tests:**

> **Gate tests MUST NOT treat hardcoded literals as the primary oracle of correctness.**  
> Assertions must be derived from a **declared, shared source of truth** (contract, schema, canonical authored content, public API response shape, documented invariants) or from **computed baselines** that are themselves justified by such a source.

**Hardcoded values are forbidden when they function as:**

- A **bypass** for a missing semantic fix (“just assert this exact `consequence_text` substring”).
- A **single-example oracle** that only matches one narrative phrasing, one model run, or one author’s wording.
- A **duplicate truth surface** that contradicts or silently diverges from canonical YAML, runtime projection, or published contracts.

**Allowed patterns (non-exhaustive):**

- **Load the oracle** from canonical content (e.g. `content/modules/…`, compiled projections, fixtures generated from the same pipeline that production uses).
- **Assert structure and invariants** (types, keys, bounds, monotonicity, presence of required fields, forbidden classes absent) without pinning prose.
- **Compare against a stable artifact** only when that artifact is **versioned and reviewable** (e.g. golden JSON under `tests/fixtures/` with a documented generator, or snapshot tests under explicit team review policy — not ad-hoc copy-paste).
- **Use regex or semantic checks** sparingly and only when tied to a **named invariant** documented in an ADR or contract (not “this one German clause”).

**Pull requests that add or extend gate tests must be rejected if:**

- The primary assertion is a **long literal** or **opaque magic constant** with no pointer to the contract or content that defines it.
- The test would **pass** if the implementation returned **wrong behavior** that still matched the hardcoded string.
- The test would **fail** if the implementation improved while preserving all **documented** semantics (e.g. rephrased narrator text that still satisfies the same content keys and policies).

### Capability Matrix and Pi / Π vocabulary

For Capability Matrix work, Pi / Π labels are historical cross-reference vocabulary only. They must not become runtime IDs, score names, schema keys, routing keys, or control-flow branches. Production code must use stable semantic names such as `silence_negative_space`, `environment_state`, `dramatic_irony`, `callback_web`, `subtext`, `information_disclosure`, `social_pressure`, `sensory_context`, and `improvisational_coherence`.

Semantic names are allowed in production when they are contract-backed. Tests must distinguish forbidden Pi-number usage from valid semantic runtime surfaces. When a new Capability Matrix row gains implementation code, update `tests/gates/test_table_b_anti_hardcoding_gate.py` with the legacy label and any reviewed semantic runtime-aspect surface, or document why the row is out of scope.

ADR-0041 adds the Runtime Capability Authority boundary. Selector manifests, selector outputs, activation modes, scoped co-authority decision payloads, RuntimeAspectLedger evidence, MCP payloads, and Langfuse score names must follow the same semantic-name rule. A selector decision can explain why `narrator_authority`, `scene_energy`, or `npc_agency` was selected or excluded for a turn, but it must not use Pi / Π labels as active keys and must not be treated as implementation, promotion, or live/staging proof by itself.

ADR-0039 applies to every test file that references a Pi / Π capability label, including tests that use Table-B metadata only as fixture data. Those tests must be covered by `tests/gates/test_adr_0039_pi_scope.py`, and any new Pi-labeled test must either join that coverage manifest or remove the legacy label. A Pi-labeled test is not evidence by name alone; it must assert contract fields, validators, policy-derived values, runtime wiring, ledger projection, MCP extraction, or Langfuse/staging evidence.

Capability promotion evidence belongs in:

- `docs/MVPs/capability_matrix_status_and_adr_relations.md` for current truth, ADR relation, semantic name, and maturity.
- `docs/MVPs/capability_matrix_verification_log.md` for dated verification runs.
- `docs/MVPs/capability_matrix_live_claim_gates.md` for live/staging/Langfuse/MCP promotion rules.

### MCP, Langfuse, portability, and evidence quality

MCP and Langfuse verification tools are ADR-0039 gate surfaces when their output is used for Capability Matrix claims. They must derive repository paths from `Config.repo_root`, `REPO_ROOT`, or another repository-root discovery mechanism; production verification code must not embed machine-local roots such as a developer's drive, home directory, or mount path. Dated verification logs may preserve historical absolute commands only when they are explicitly marked as local environment transcripts and not reusable proof instructions.

Local pytest, mocked provider checks, fixture traces, and degraded/fallback paths prove local implementation behavior only. They must not be described as staging/live/Langfuse/MCP success unless the evidence includes the actual provider or environment metadata, reproducible trace/query identifiers where applicable, semantic score names, and the command or query used to retrieve it.

False-green prevention for MCP/Langfuse gates requires structured result fields: return codes, command/cwd or query metadata, environment scope, evidence scope, score names, and normalized runtime metadata. A PASS label, test name, trace id string, comment, or documentation statement is not proof unless the structured output supports the claim.

### Runtime surface governance (expanded scope)

ADR-0039 governs **runtime behavior and decision surfaces**, not only tests and documentation. Any path that can distort **runtime truth, readiness, player/session/turn flow, beat progression, or decision-tree behavior** is in scope, including:

- **`ai_stack`** — LangGraph executor, `run_validation_seam`, `runtime_aspect_ledger` / `runtime_aspect_ledger/runtime_intelligence_projection/`, ADR-0041 sidecar and flags (fail-closed defaults; projection must not impersonate seam or commit).
- **`world-engine`** — `StoryRuntimeManager`, commit/readiness models, narrative commit seam.
- **`backend`** — player-session bundle and readiness derivation (`evaluate_session_opening_readiness`, ADR-0041 veto-only consumer).
- **`frontend` Play Shell** — must **not manufacture** readiness, live, or healthy semantics; display only fields the backend/runtime bundle proves.
- **`administration-tool`** — operator UI and proxy to backend/world-engine; **display and approved control actions only**; must **not** treat local dashboard or proxy payload as canonical runtime, commit, or live health without the same fields from authoritative services.
- **`story_runtime_core`** — first-class: `interpret_player_input` / semantic language adapter (**preview** shaping only), **`recovery/no_dead_end`** (**diagnostic** evidence contract only), branching / callback / consequence helpers (**diagnostic** unless explicitly wired through world-engine commit). This package must **not** bypass canonical validation or commit authority.

**Normative inventory:** [`docs/MVPs/adr0039_runtime_surface_governance_inventory.md`](../../../MVPs/adr0039_runtime_surface_governance_inventory.md) (YAML front matter, gate-enforced). Code is authoritative over prose; update the inventory when surfaces change.

**Interaction with ADR-0041:** Scoped co-authority and readiness aggregation remain **bounded, explicit, and testable**; they must **not** silently mutate `validation_outcome`, commit, or seam-canonical readiness. `plan_enforced` without the LangGraph graph sidecar must remain **dry-run** on the ledger projection path.

---

**Consequences.** **Positive**

- Gates measure **whether the system honors contracts**, not whether it repeats yesterday’s wording.
- Canonical content and ADRs remain **single sources of truth**; tests stop inventing parallel truth.
- Refactors and localization (e.g. session output language) become **possible without whack-a-mole** string updates across gate tests.

**Negative / risks**

- Tests may require **more setup** (loaders, small harnesses) instead of a one-line `assert output == "..."`.
- Some genuinely brittle domains (timestamps, nonces) still need **controlled fixtures**; those fixtures must be **documented** and minimal, not full narrative oracles.

**Follow-ups**

- During code review, treat unexplained string literals in `tests/` and `**/test_*gate*` files as **blockers** unless referenced to contract or content.
- Prefer extending **canonical content** or **contract schemas** when a new invariant is needed, then binding tests to that extension.

---

**Evidence.** `docs/architecture/project/project/governance/architecture.md#d3-gate-tests-must-not-hardcode-oracle-bypasses` (archived — see `docs/archive/adr-retired-2026/`)

### D3: Unified Python 3.14 interpreter standard

**Status:** 
**Origin:** ADR-0064 (retired 2026-06-23)

**Context.** The monorepo previously mixed **Python 3.10** (CI merge bar), **3.11–3.13** (per-service Dockerfiles), and ad hoc host interpreters (including **3.14** on developer machines). That drift caused:

- Different `pip`/wheel resolution and editable-install behaviour between laptop, Actions, and Compose.
- Tooling failures on newer interpreters (for example `argparse` help strings containing `%` under 3.14 before `hub_cli` was escaped).
- False confidence when “tests pass locally” on an interpreter version CI and containers never used.

The team chose **one** minor version for host, CI, Dev Container, and all first-party service images.

**Decision.** 1. **Canonical interpreter:** **Python 3.14.x** everywhere for World of Shadows development and delivery.
2. **Packaging constraint:** every in-repo `pyproject.toml` declares `requires-python = ">=3.14,<3.15"`.
3. **Repo pin:** root **`.python-version`** contains `3.14` (pyenv / IDE discovery).
4. **Docker:** all service Dockerfiles and `docker/Dockerfile.ai-stack-test` use official **`python:3.14-slim`** or **`python:3.14-bookworm`** base images; backend multi-stage builds copy **`python3.14/site-packages`**.
5. **CI:** GitHub Actions workflows under `.github/workflows/` and `'fy'-suites/.github/workflows/` set **`python-version: '3.14'`** (or `['3.14']` matrix).
6. **Dev Container:** `.devcontainer/devcontainer.json` uses **`mcr.microsoft.com/devcontainers/python:1-3.14-bookworm`**.
7. **Documentation:** [README.md](../../README.md), [docs/testing-setup.md](../../../testing-setup.md), and [docs/dev/contributing.md](../../../dev/contributing.md) are the human-facing summaries; this ADR is the architectural record.

**Out of scope:** forcing Python 3.14 inside third-party base images (Langfuse, ClickHouse, etc.) bundled only as non-Python services in Compose overrides.

**Consequences.** **Positive:** One merge bar; host matches CI matches containers; fewer “works on my machine” disputes; aligns with the interpreter already used on primary dev workstations.

**Negative / risks:** Some PyPI wheels may lag 3.14; a dependency pin failure blocks the whole tree until upgraded or replaced. Upgrading the minor version requires a deliberate ADR amendment and synchronized Dockerfile/CI/`requires-python` edits.

**Follow-ups:** Rebuild Compose images after pulling (`python docker-up.py build`). Recreate local venvs with `py -3.14 -m venv .venv`.

**Testing.** - **Verify interpreter pin:** `python --version` → `3.14.x` on host; `docker compose exec backend python --version` and `docker compose exec play-service python --version` after rebuild.
- **Verify packaging:** `pip install -e .` at repo root succeeds under 3.14; no `requires-python` resolver errors on in-repo packages.
- **Verify gates:** `python tests/run_tests.py --suite backend_runtime --quick` (or broader suites per change scope).
- **Verify tooling:** `python -m despaghettify.tools check` (or `python "./'fy'-suites/despaghettify/tools/hub_cli.py" check`) exits 0 when `fy_platform` is on `PYTHONPATH`.

Gate tests remain subject to [ADR-0039](../../../archive/adr-retired-2026/adr-0039-gate-tests-no-hardcoded-oracle-bypass.md).

**Evidence.** `docs/architecture/project/project/quality-gates/architecture.md#d3-python-314-unified-interpreter-standard` (archived — see `docs/archive/adr-retired-2026/`)

### MVP4-TEST-GATE-PLAN: MVP4 Test Gate Plan — 5 Core Contracts

**Status:** Accepted
**Origin:** MVP4-TEST-GATE-PLAN (retired 2026-06-23)

**Evidence.** `docs/ADR/MVP4_TEST_GATE_PLAN.md` (archived — see `docs/archive/adr-retired-2026/`)
## 10. Quality Requirements

| Command | Purpose |
| --- | --- |
| `python tests/run_tests.py --suite engine` | Engine tests |
| `python -m pytest tests/gates/ -v --tb=short --no-cov` | Architecture gates |
| `python -m pytest tests/gates/test_architecture_documentation_gate.py -v` | Doc migration gate |

## 11. Risks & Technical Debt

Some ADRs marked Not Finished lack dedicated gates—listed as open in owning SADs.

## 12. Glossary

| Term | Meaning |
| --- | --- |
| Oracle | Canonical fixture or constant a gate compares against |
