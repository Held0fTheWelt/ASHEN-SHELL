# SPEC 03 — Consistency & Cross-Link Integrity Engine

Status: Proposed
Date: 2026-06-16
Depends on: SPEC_01 (ADRs), SPEC_02 (structured UML)

## 1. Purpose

The intelligence that makes co-authoring safe: detect incoherence as ADRs and UML change, and show
the blast radius of an edit **before** it lands. This is what turns the database from a place the
agent reads into a place the agent can edit without quietly breaking the knowledge graph. No Git
here — historical/staleness signals are SPEC_04.

## 2. Scope

In scope:

- A cross-link model over knowledge items (ADR↔ADR, ADR↔UML element/diagram, ADR↔source area,
  definition usage) built on the existing `knowledge_links` table.
- Consistency checks (all advisory, never destructive):
  - **Supersede integrity** (full, beyond SPEC_01's minimal): cycles; a `superseded` ADR still
    marked `Accepted`; two active ADRs both superseding the same target; dangling supersedes.
  - **Broken-link detection** across every `knowledge_links.target_ref` and ADR↔UML reference.
  - **ADR↔UML coherence:** an ADR references a UML element/diagram that no longer exists; a UML
    element linked to a superseded/rejected ADR.
  - **Overlap/contradiction (heuristic):** ADRs/rules whose governed scope (`applies_to` /
    source-area mapping) overlaps and whose decisions conflict; plus author-asserted
    `conflicts_with` links. Semantic (LLM) contradiction detection is an optional later hook, not
    part of this spec.
  - **Orphans:** an ADR with no links; a UML element referenced by nothing.
- **Impact-of-change:** given a target (ADR/element), traverse the link graph to report what
  references it and what it governs — the edit blast radius.
- Authority-aware output: findings respect the authority order (hard guardrail > accepted ADR >
  active rule > canonical definition > current UML > source-area > explicit link > inferred).

Out of scope: Git provenance/staleness (SPEC_04), LLM semantic contradiction, auto-repair.

## 3. Success criteria

1. Each finding type fires on a seeded fixture and stays silent on a clean fixture.
2. `akdb_impact_of(target)` returns the correct transitive set of referencing and governed items.
3. Findings are ordered by authority and severity and never block an edit (advisory only).
4. Editing an ADR/element through MCP returns the relevant impact summary alongside the result.

## 4. Data model

- Reuse `knowledge_links` (source_item_uid, target_ref, link_type, authority_level, confidence,
  evidence).
- Add `consistency_findings` (mirrors the `staleness_reports` shape): `finding_uid, project_id,
  finding_type, target_ref, severity, message, evidence_json, created_at`. Acts as a cache of the
  last check run; recomputed on demand.

## 5. Module layout

```
architectural_knowledge_db/consistency/
  graph.py        # build the link graph for a project
  checks/         # one module per finding type
    supersede.py
    broken_links.py
    adr_uml.py
    overlap.py
    orphans.py
  impact.py       # blast-radius traversal
  engine.py       # run checks, persist findings, order by authority/severity
```

One module per check keeps each finding's logic isolated and independently testable.

## 6. MCP tools

- `akdb_check_consistency(project_id, scope?, types?)` → ordered findings
- `akdb_impact_of(project_id, target)` → referencing + governed items
- `akdb_link(project_id, source, target, link_type, evidence?)` → create explicit link
- `akdb_get_links(project_id, target, direction?)` → inbound/outbound links

The authoring tools from SPEC_01/02 call `impact.py` so that every edit response carries its impact
summary.

## 7. Testing

- Per-check fixtures (positive + clean) for all finding types.
- Graph traversal tests for `impact_of` (transitive, cycle-safe).
- Authority-ordering tests on mixed findings.
- Integration: an MCP ADR edit returns the expected impact summary.

## 8. Open decisions

- How aggressive overlap/contradiction heuristics should be before they become noise — proposed
  default: only flag when governed scopes overlap **and** an explicit decision/rule conflicts;
  tune thresholds during planning.
