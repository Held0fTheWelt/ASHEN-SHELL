# V24 Writers’ Room ↔ RAG overlap ledger

## Scope

This ledger records the **bounded overlap boundary** between Writers’ Room workflow and RAG governance in the current MVP package.

The purpose is **not** to claim the overlap is solved away.
The purpose is to keep the overlap:

- intentional where it is real,
- explicitly separated where authority must remain separate, and
- reviewable for future re-audits.

## Classified overlap seam

The current overlap is intentional only in these roles:

- `retrieval_context_provider`
- `context_pack_assembly`
- `recommendation_support`

The current package keeps these roles separate from:

- `publish_authority`
- `canonical_truth_boundary`
- `runtime_context_consumer`

## Why the overlap is currently allowed

The overlap is allowed because Writers’ Room review work needs repository-owned retrieval/context support in order to:

- inspect relevant authored and review-support material,
- assemble reviewable context packs,
- ground issue/comment/patch/variant recommendations in cited evidence, and
- keep recommendation artifacts auditable instead of purely free-form.

That support function improves review quality, but it is **not** a shortcut to canon.

## What must remain separate

### Writers’ Room

Allowed today:

- request retrieval/context support for review tasks;
- consume `wos.context_pack.build` output in `writers_room` mode;
- generate recommendation artifacts and review bundles.

Forbidden today:

- direct publish of retrieved or generated content;
- direct mutation of authored canon;
- direct mutation of world-engine committed truth;
- re-labeling retrieval output as canonical truth without publish governance.

### RAG

Allowed today:

- provide retrieval hits, snippets, ranking notes, governance lanes, and visibility metadata;
- support context-pack assembly for Writers’ Room and runtime callers under existing policy gates;
- remain a support/context subsystem.

Forbidden today:

- acting as publish authority;
- acting as canonical content authority;
- treating context-pack output as self-authorizing canon;
- treating retrieval output as runtime committed truth.

## Drift signals a future re-audit must treat as regression

Future drift is present if any of the following appears:

1. Writers’ Room endpoints start returning material described as already canonical or already published by virtue of retrieval/model output alone.
2. Retrieval/context-pack output is described as sufficient for publish approval without backend/admin review.
3. `ai_stack/rag.py` or linked retrieval flows begin to write directly into canonical publish surfaces.
4. Runtime documentation or diagnostics start describing retrieval output as authoritative committed truth.
5. New wording collapses Writers’ Room + RAG into one blended AI authority lane.

## What a future re-audit must verify before calling this overlap closed or stable

A future re-audit must verify all of the following before claiming the overlap is fully closed or permanently stabilized:

1. the overlap seam is still limited to `retrieval_context_provider` and `context_pack_assembly` (with recommendation support as a subordinate consumer role);
2. publish decisions still require explicit backend/admin and human review authority;
3. canonical content promotion still requires publish governance rather than retrieval presence;
4. runtime committed truth still remains in world-engine committed state rather than retrieval artifacts;
5. tests and Contractify attachments still reflect the same boundary language; and
6. any new write-back or authoring-assist feature is separately governed before it is treated as part of this overlap seam.

## Current status

This overlap remains **intentionally unresolved but narrowed**.

The correct current reading is:

- overlap at retrieval/context-pack support is allowed;
- authority fusion is not allowed; and
- the boundary should remain visible in Contractify manual-unresolved reporting until stronger evidence proves it no longer needs special review.
