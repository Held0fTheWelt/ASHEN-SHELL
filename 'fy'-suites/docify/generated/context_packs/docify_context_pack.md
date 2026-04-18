# Context Pack — docify

Query: `docstring`
Audience: `developer`
Evidence confidence: `high`

Found 8 indexed evidence hits for query "docstring" across suites ['docify']. Strongest source: generated/context_packs/docify_context_pack.json#chunk-1. Use the top-ranked items first and treat lower-confidence hits as hints.

## Priorities

- Start with generated/context_packs/docify_context_pack.json#chunk-1 because it currently has the strongest combined signal.
- Compare it with superpowers/docify-synthesize/SKILL.md#chunk-1 before deciding on outward action.

## Most-Recent-Next-Steps

- Open generated/context_packs/docify_context_pack.json#chunk-1 first.
- Use the top two hits to validate the next code or governance action.

## Uncertainty

- top_hits_close_together

## Artifact paths

- `generated/context_packs/docify_context_pack.json#chunk-1`
- `generated/context_packs/docify_context_pack.md#chunk-1`
- `generated/context_packs/docify_context_pack.md#chunk-3`
- `superpowers/docify-orchestrate/SKILL.md#chunk-1`
- `superpowers/docify-synthesize/SKILL.md#chunk-1`
- `superpowers/docify-synthesize/SKILL.md#chunk-2`
- `tools/python_docstring_synthesize.py#chunk-1`
- `tools/strip_ai_stack_docstring_placeholders.py#chunk-1`

## Cross-suite signals

- `securify`: Securify found security follow-up work: no discoverable security documentation, secret-related ignore rules are missing. Start with the most direct exposure and the missing guidance surfaces.
  - next: Use the strongest cross-suite signal as a second opinion before acting in isolation.
- `documentify`: Documentify generated the current documentation tracks and status pages.
  - next: Read the newly generated documentation and decide which tracks should be exported outward.
  - next: Open the generated output directory and review the new files in simple language first.
- `despaghettify`: No summary available.
  - next: Use the strongest cross-suite signal as a second opinion before acting in isolation.
- `contractify`: No summary available.
  - next: Review the 4 finding(s) and decide which one should be fixed first.

## generated/context_packs/docify_context_pack.json#chunk-1

- suite: docify
- scope: suite
- lexical: 1.0
- semantic: 0.3302
- hybrid: 0.7462
- recency: 0.8914
- suite_affinity: 0.0
- confidence: high
- rationale: matched terms: docstring; recently indexed evidence

{   "pack_id": "9b58770d7c30475ab95bba74e0a1ee49",   "query": "docstring",   "suite_scope": [     "docify"   ],   "audience": "developer",   "summary": "Found 8 indexed evidence hits for query \"docstring\" across suites ['docify']. Strongest source: generated/context_packs/docif

## superpowers/docify-synthesize/SKILL.md#chunk-1

- suite: docify
- scope: suite
- lexical: 1.0
- semantic: 0.2794
- hybrid: 0.7458
- recency: 0.9729
- suite_affinity: 0.0
- confidence: high
- rationale: matched terms: docstring; recently indexed evidence

--- name: docify-synthesize description: Routes agents to docify/python_docstring_synthesize.py — PEP 8 # comments for a range (--apply) or Google-style docstring draft for one --function (--emit-google-docstring, --apply-docstring). Triggers on docify synthesize, explain source 

## superpowers/docify-orchestrate/SKILL.md#chunk-1

- suite: docify
- scope: suite
- lexical: 1.0
- semantic: 0.1952
- hybrid: 0.7227
- recency: 0.9593
- suite_affinity: 0.0
- confidence: high
- rationale: matched terms: docstring; recently indexed evidence

--- name: docify-orchestrate description: Routes agents to Docify documentation tasks — governance check/solve tracks, Python docstring audit, drift hints, inline source explain (PEP 8 comments), slice-based fixes, JSON reports. Triggers on docify, docify orchestrate, documentati

## superpowers/docify-synthesize/SKILL.md#chunk-2

- suite: docify
- scope: suite
- lexical: 1.0
- semantic: 0.1796
- hybrid: 0.7215
- recency: 0.9774
- suite_affinity: 0.0
- confidence: high
- rationale: matched terms: docstring; recently indexed evidence

**Docstring backlog (measurement + manual fixes):** [`documentation-audit-task.md`](../../documentation-audit-task.md) and ``'fy'-suites/docify/tools/python_documentation_audit.py``.  Hub orientation: [`README.md`](../../README.md).

## generated/context_packs/docify_context_pack.md#chunk-1

- suite: docify
- scope: suite
- lexical: 1.0
- semantic: 0.1655
- hybrid: 0.7058
- recency: 0.8959
- suite_affinity: 0.0
- confidence: high
- rationale: matched terms: docstring; recently indexed evidence

# Context Pack — docify  Query: `docstring` Audience: `developer` Evidence confidence: `high`  Found 8 indexed evidence hits for query "docstring" across suites ['docify']. Strongest source: generated/context_packs/docify_context_pack.json#chunk-1. Use the top-ranked items first 

## generated/context_packs/docify_context_pack.md#chunk-3

- suite: docify
- scope: suite
- lexical: 1.0
- semantic: 0.056
- hybrid: 0.6797
- recency: 0.905
- suite_affinity: 0.0
- confidence: high
- rationale: matched terms: docstring; recently indexed evidence

- `securify`: Securify found security follow-up work: no discoverable security documentation, secret-related ignore rules are missing. Start with the most direct exposure and the missing guidance surfaces.   - next: Use the strongest cross-suite signal as a second opinion before 

## tools/python_docstring_synthesize.py#chunk-1

- suite: docify
- scope: suite
- lexical: 1.0
- semantic: 0.2973
- hybrid: 0.6605
- recency: 0.3077
- suite_affinity: 0.2
- confidence: high
- rationale: matched terms: docstring

#!/usr/bin/env python3 """Docify hub CLI — PEP 8 inline ``#`` comments or a Google-style function docstring.  Two modes:  1. **Block comments** — for a 1-based line range (or ``--function`` body span),    insert indented ``#`` lines above intersecting statements. Prose wraps to  

## tools/strip_ai_stack_docstring_placeholders.py#chunk-1

- suite: docify
- scope: suite
- lexical: 1.0
- semantic: 0.0714
- hybrid: 0.6502
- recency: 0.6154
- suite_affinity: 0.2
- confidence: high
- rationale: matched terms: docstring

#!/usr/bin/env python3 """Remove bulk-docstring placeholder prose from ``ai_stack`` (excluding ``tests/``).  Rewrites only string literals that are the leading docstring of ``Module``, ``ClassDef``, ``FunctionDef``, or ``AsyncFunctionDef`` nodes. Does **not** change ``# TODO`` co
