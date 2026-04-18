# Context Pack — docify

Query: `docstring`
Audience: `developer`
Evidence confidence: `high`

Found 8 indexed evidence hits for query "docstring" across suites ['docify']. Strongest source: tools/python_docstring_synthesize.py#chunk-1. Use the top-ranked items first and treat lower-confidence hits as hints.

## Priorities

- Start with tools/python_docstring_synthesize.py#chunk-1 because it currently has the strongest combined signal.
- Compare it with generated/context_packs/docify_context_pack.json#chunk-1 before deciding on outward action.

## Most-Recent-Next-Steps

- Open tools/python_docstring_synthesize.py#chunk-1 first.
- Use the top two hits to validate the next code or governance action.

## Uncertainty

- top_hits_close_together

## Artifact paths

- `documentation-docstring-synthesize-task.md#chunk-1`
- `generated/context_packs/docify_context_pack.json#chunk-1`
- `generated/context_packs/docify_context_pack.md#chunk-4`
- `superpowers/docify-orchestrate/SKILL.md#chunk-1`
- `superpowers/docify-synthesize/SKILL.md#chunk-1`
- `superpowers/docify-synthesize/SKILL.md#chunk-2`
- `tools/python_docstring_synthesize.py#chunk-1`
- `tools/python_docstring_synthesize.py#chunk-2`

## Cross-suite signals

- `securify`: Securify found security follow-up work: no discoverable security documentation, secret-related ignore rules are missing. Start with the most direct exposure and the missing guidance surfaces.
  - next: Use the strongest cross-suite signal as a second opinion before acting in isolation.
- `documentify`: Documentify generated the current documentation tracks and status pages.
  - next: Read the newly generated documentation and decide which tracks should be exported outward.
  - next: Open the generated output directory and review the new files in simple language first.
- `despaghettify`: No summary available.
  - next: Use the strongest cross-suite signal as a second opinion before acting in isolation.
- `contractify`: contractify is ready for inspection. Read the latest summary first and then only open detailed artifacts where you still need proof.
  - next: Read the summary first, then open the linked artifacts only where you still need detail.
  - next: Use the strongest cross-suite signal as a second opinion before acting in isolation.

## tools/python_docstring_synthesize.py#chunk-1

- suite: docify
- scope: suite
- lexical: 1.0
- semantic: 0.2973
- hybrid: 0.7614
- recency: 0.9805
- suite_affinity: 0.2
- confidence: high
- rationale: matched terms: docstring; recently indexed evidence

#!/usr/bin/env python3 """Docify hub CLI — PEP 8 inline ``#`` comments or a Google-style function docstring.  Two modes:  1. **Block comments** — for a 1-based line range (or ``--function`` body span),    insert indented ``#`` lines above intersecting statements. Prose wraps to  

## generated/context_packs/docify_context_pack.json#chunk-1

- suite: docify
- scope: suite
- lexical: 1.0
- semantic: 0.3022
- hybrid: 0.7514
- recency: 0.9725
- suite_affinity: 0.0
- confidence: high
- rationale: matched terms: docstring; recently indexed evidence

{   "pack_id": "25680ae9065348f3a8f9268d7b68bc1b",   "query": "docstring",   "suite_scope": [     "docify"   ],   "audience": "developer",   "summary": "Found 8 indexed evidence hits for query \"docstring\" across suites ['docify']. Strongest source: generated/context_packs/docif

## tools/python_docstring_synthesize.py#chunk-2

- suite: docify
- scope: suite
- lexical: 1.0
- semantic: 0.249
- hybrid: 0.7494
- recency: 0.9807
- suite_affinity: 0.2
- confidence: high
- rationale: matched terms: docstring; recently indexed evidence

python "./'fy'-suites/docify/tools/python_docstring_synthesize.py" \\         --file path/to/your_module.py \\         --function your_callable --apply  python "./'fy'-suites/docify/tools/python_docstring_synthesize.py" \\         --file path/to/your_module.py \\         --functi

## superpowers/docify-synthesize/SKILL.md#chunk-1

- suite: docify
- scope: suite
- lexical: 1.0
- semantic: 0.2794
- hybrid: 0.7462
- recency: 0.9758
- suite_affinity: 0.0
- confidence: high
- rationale: matched terms: docstring; recently indexed evidence

--- name: docify-synthesize description: Routes agents to docify/python_docstring_synthesize.py — PEP 8 # comments for a range (--apply) or Google-style docstring draft for one --function (--emit-google-docstring, --apply-docstring). Triggers on docify synthesize, explain source 

## generated/context_packs/docify_context_pack.md#chunk-4

- suite: docify
- scope: suite
- lexical: 1.0
- semantic: 0.2369
- hybrid: 0.7352
- recency: 0.9733
- suite_affinity: 0.0
- confidence: high
- rationale: matched terms: docstring; recently indexed evidence

- suite: docify - scope: suite - lexical: 1.0 - semantic: 0.3544 - hybrid: 0.7644 - recency: 0.9721 - suite_affinity: 0.0 - confidence: high - rationale: matched terms: docstring; recently indexed evidence  - suite: docify - scope: suite - lexical: 1.0 - semantic: 0.2973 - hybrid

## superpowers/docify-orchestrate/SKILL.md#chunk-1

- suite: docify
- scope: suite
- lexical: 1.0
- semantic: 0.1952
- hybrid: 0.7251
- recency: 0.9752
- suite_affinity: 0.0
- confidence: high
- rationale: matched terms: docstring; recently indexed evidence

--- name: docify-orchestrate description: Routes agents to Docify documentation tasks — governance check/solve tracks, Python docstring audit, drift hints, inline source explain (PEP 8 comments), slice-based fixes, JSON reports. Triggers on docify, docify orchestrate, documentati

## superpowers/docify-synthesize/SKILL.md#chunk-2

- suite: docify
- scope: suite
- lexical: 1.0
- semantic: 0.1796
- hybrid: 0.7213
- recency: 0.976
- suite_affinity: 0.0
- confidence: high
- rationale: matched terms: docstring; recently indexed evidence

**Docstring backlog (measurement + manual fixes):** [`documentation-audit-task.md`](../../documentation-audit-task.md) and ``'fy'-suites/docify/tools/python_documentation_audit.py``.  Hub orientation: [`README.md`](../../README.md).

## documentation-docstring-synthesize-task.md#chunk-1

- suite: docify
- scope: suite
- lexical: 1.0
- semantic: 0.1451
- hybrid: 0.7204
- recency: 0.9608
- suite_affinity: 0.2
- confidence: high
- rationale: matched terms: docstring; recently indexed evidence

# Docify — inline source explain task (PEP 8 comments)  **Language:** Same canonical policy as [`docs/dev/contributing.md`](../../docs/dev/contributing.md#repository-language) — generated **comments** are **English** only; this task adds **procedure** only.  ## Purpose  Use the *
