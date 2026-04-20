# V24 Writers’ Room ↔ RAG overlap clarification report

## Scope

This report records the **bounded overlap-boundary clarification pass** for the Writers’ Room ↔ RAG seam in the current MVP package.
The goal of this cycle was **not** to redesign Writers’ Room, **not** to redesign retrieval, and **not** to fuse authority.
The goal was to make the current intentional overlap narrower, more explicit, and more reviewable.

## Classified overlap seam

The overlap seam is now classified with a small bounded vocabulary:

- `retrieval_context_provider`
- `context_pack_assembly`
- `recommendation_support`
- `publish_authority`
- `canonical_truth_boundary`
- `runtime_context_consumer`

### Assigned roles

| Role | Writers’ Room | RAG |
|---|---|---|
| `retrieval_context_provider` | consumes support | provides support |
| `context_pack_assembly` | requests/consumes pack | supports pack assembly |
| `recommendation_support` | produces issue/comment/patch/variant recommendations | supplies evidence/context only |
| `publish_authority` | no direct authority | no authority |
| `canonical_truth_boundary` | cannot cross directly | cannot cross directly |
| `runtime_context_consumer` | no live runtime ownership | may support runtime retrieval, but not commit truth |

## What each side is allowed to do today

### Writers’ Room

Allowed:

- request bounded retrieval/context support for review work;
- consume `wos.context_pack.build` output in `writers_room` mode;
- generate recommendation artifacts and review bundles grounded in retrieved context.

### RAG

Allowed:

- provide retrieval hits, snippets, ranking notes, governance lanes, and visibility metadata;
- support Writers’ Room context-pack assembly;
- remain a context/support subsystem for Writers’ Room and runtime callers under existing policy gates.

## What each side is forbidden to do today

### Writers’ Room

Forbidden:

- auto-publish retrieved or generated material;
- treat retrieval output as authored canon by itself;
- mutate runtime committed truth directly;
- bypass backend/admin review for canonical promotion.

### RAG

Forbidden:

- act as publish authority;
- act as canonical content authority;
- treat context-pack output as self-authorizing canon;
- treat retrieval output as runtime committed truth.

## Where authority remains separate

Authority remains explicitly separate at three points:

1. **publish authority** remains backend/admin + human review;
2. **canonical content promotion** remains publish-governed rather than retrieval-derived; and
3. **runtime committed truth** remains in world-engine committed state rather than retrieval/context artifacts.

## What changed in package wording

### Writers’ Room governance clarification

Updated: `docs/technical/content/writers-room-and-publishing-flow.md`

Now explicit:

- what Writers’ Room may consume from retrieval;
- that Writers’ Room outputs remain recommendation-only and non-canonical;
- that publish authority remains separate; and
- that Writers’ Room must never mutate runtime truth directly.

### RAG governance clarification

Updated: `docs/technical/ai/RAG.md`

Now explicit:

- which Writers’ Room support lane is legitimate today;
- that retrieval/context-pack output is context/support rather than canon;
- that context-pack assembly does not equal publish authority; and
- that runtime committed truth remains separate from retrieval results.

### Bounded overlap ledger

Added: `governance/V24_WRITERS_ROOM_RAG_OVERLAP_LEDGER.md`

The ledger records:

- which overlap is intentional;
- why it is allowed today;
- what must remain separate;
- what drift looks like; and
- what a future re-audit must verify before calling the overlap closed or stable.

## Contractify / unresolved-area before vs after

### Before

The manual unresolved area was broad:

- **summary:** Writers’ Room workflow and RAG governance intentionally overlap at retrieval/context-pack assembly, but publishing authority and runtime truth remain distinct and should stay explicitly reviewed.
- **classification:** intentional_overlap_boundary

### After

The manual unresolved area remains visible, but is narrower and more explicit:

- **summary:** Writers’ Room workflow and RAG governance intentionally overlap only at retrieval_context_provider and context_pack_assembly support; publish_authority, canonical promotion, and runtime truth remain separate and must stay explicitly reviewed.
- **classification:** intentional_overlap_boundary_narrowed_to_context_support
- **normative sources now include:** `governance/V24_WRITERS_ROOM_RAG_OVERLAP_LEDGER.md`

The correct current reading is still **not resolved/hidden**; it is **bounded and reviewable**.

## Focused validation evidence

- updated Contractify audit: `validation/fy_reports/contractify_audit.json`
- touched governance/doc link check: `validation/V24_WRITERS_ROOM_RAG_OVERLAP_LINK_CHECK.md`
- focused Contractify test: PASS (`'fy'-suites/contractify/tools/tests/test_runtime_mvp_spine.py`)
- focused RAG tests: PASS (`ai_stack/tests/test_rag.py` selected cases)
- focused backend Writers’ Room pytest: blocked in this environment because `flask` is not installed

## Re-audit checks that must now hold

The next re-audit should confirm that:

- the overlap seam is explicitly named;
- retrieval/context support remains separate from publish authority;
- retrieval/context support remains separate from runtime committed truth;
- Writers’ Room remains non-canonical until publish governance acts;
- RAG remains support/context rather than canon authority; and
- the overlap remains visible in manual-unresolved reporting unless stronger evidence truly closes it.
