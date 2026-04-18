# Context Pack — docify

Query: `docstring`
Audience: `developer`
Evidence confidence: `high`

Found 8 indexed evidence hits for query "docstring" across suites ['docify']. Strongest source: tools/python_docstring_synthesize.py#chunk-1. Use the top-ranked items first and treat lower-confidence hits as hints.

## Priorities

- Start with tools/python_docstring_synthesize.py#chunk-1 because it currently has the strongest combined signal.
- Compare it with tools/strip_ai_stack_docstring_placeholders.py#chunk-1 before deciding on outward action.

## Most-Recent-Next-Steps

- Open tools/python_docstring_synthesize.py#chunk-1 first.
- Use the top two hits to validate the next code or governance action.

## Uncertainty

- top_hits_close_together

## Artifact paths

- `generated/context_packs/docify_context_pack.json#chunk-1`
- `superpowers/docify-orchestrate/SKILL.md#chunk-1`
- `superpowers/docify-synthesize/SKILL.md#chunk-1`
- `tools/python_docstring_synthesize.py#chunk-1`
- `tools/python_docstring_synthesize.py#chunk-2`
- `tools/python_documentation_audit.py#chunk-1`
- `tools/python_documentation_audit.py#chunk-3`
- `tools/strip_ai_stack_docstring_placeholders.py#chunk-1`

## Cross-suite signals

- `securify`: Securify found security follow-up work: no discoverable security documentation, secret-related ignore rules are missing. Start with the most direct exposure and the missing guidance surfaces.
  - next: Use the strongest cross-suite signal as a second opinion before acting in isolation.
- `documentify`: Documentify generated the current documentation tracks and status pages.
  - next: Read the newly generated documentation and decide which tracks should be exported outward.
  - next: Open the generated output directory and review the new files in simple language first.
- `despaghettify`: No summary available.
  - next: Use the strongest cross-suite signal as a second opinion before acting in isolation.
- `contractify`: contractify is initialized and bound for outward work. Internal state stays in the fy workspace.
  - next: Use the strongest cross-suite signal as a second opinion before acting in isolation.

## tools/python_docstring_synthesize.py#chunk-1

- suite: docify
- scope: suite
- lexical: 1.0
- semantic: 0.2973
- hybrid: 0.6965
- recency: 0.5475
- suite_affinity: 0.2
- confidence: high
- rationale: matched terms: docstring

#!/usr/bin/env python3 """Docify hub CLI — PEP 8 inline ``#`` comments or a Google-style function docstring.  Two modes:  1. **Block comments** — for a 1-based line range (or ``--function`` body span),    insert indented ``#`` lines above intersecting statements. Prose wraps to  

## tools/strip_ai_stack_docstring_placeholders.py#chunk-1

- suite: docify
- scope: suite
- lexical: 1.0
- semantic: 0.0714
- hybrid: 0.6895
- recency: 0.8778
- suite_affinity: 0.2
- confidence: high
- rationale: matched terms: docstring; recently indexed evidence

#!/usr/bin/env python3 """Remove bulk-docstring placeholder prose from ``ai_stack`` (excluding ``tests/``).  Rewrites only string literals that are the leading docstring of ``Module``, ``ClassDef``, ``FunctionDef``, or ``AsyncFunctionDef`` nodes. Does **not** change ``# TODO`` co

## tools/python_docstring_synthesize.py#chunk-2

- suite: docify
- scope: suite
- lexical: 1.0
- semantic: 0.249
- hybrid: 0.6851
- recency: 0.552
- suite_affinity: 0.2
- confidence: high
- rationale: matched terms: docstring

python "./'fy'-suites/docify/tools/python_docstring_synthesize.py" \\         --file path/to/your_module.py \\         --function your_callable --apply  python "./'fy'-suites/docify/tools/python_docstring_synthesize.py" \\         --file path/to/your_module.py \\         --functi

## generated/context_packs/docify_context_pack.json#chunk-1

- suite: docify
- scope: suite
- lexical: 1.0
- semantic: 0.3307
- hybrid: 0.667
- recency: 0.362
- suite_affinity: 0.0
- confidence: high
- rationale: matched terms: docstring

{   "pack_id": "aa7e52c3a6bd4a988b1d15e83aef436a",   "query": "docstring",   "suite_scope": [     "docify"   ],   "audience": "developer",   "summary": "Found 8 indexed evidence hits for query \"docstring\" across suites ['docify']. Strongest source: generated/context_packs/docif

## superpowers/docify-synthesize/SKILL.md#chunk-1

- suite: docify
- scope: suite
- lexical: 1.0
- semantic: 0.2794
- hybrid: 0.6657
- recency: 0.4389
- suite_affinity: 0.0
- confidence: high
- rationale: matched terms: docstring

--- name: docify-synthesize description: Routes agents to docify/python_docstring_synthesize.py — PEP 8 # comments for a range (--apply) or Google-style docstring draft for one --function (--emit-google-docstring, --apply-docstring). Triggers on docify synthesize, explain source 

## tools/python_documentation_audit.py#chunk-3

- suite: docify
- scope: suite
- lexical: 1.0
- semantic: 0.0962
- hybrid: 0.6633
- recency: 0.7285
- suite_affinity: 0.0
- confidence: high
- rationale: matched terms: docstring

# Default docstring scan: all major Python systems (application + entrypoints). # Use ``--include-tests`` to add ``**/tests/**`` trees. Subpaths are avoided so each # file is visited once (no overlapping roots). DEFAULT_RELATIVE_ROOTS: tuple[str, ...] = (     "backend",     "worl

## tools/python_documentation_audit.py#chunk-1

- suite: docify
- scope: suite
- lexical: 1.0
- semantic: 0.0693
- hybrid: 0.6553
- recency: 0.7195
- suite_affinity: 0.0
- confidence: high
- rationale: matched terms: docstring

#!/usr/bin/env python3 """Docify hub CLI — static audit for Python documentation hygiene across the monorepo.  Scans selected source trees with the ``ast`` module and reports module, class, and function/method definitions that lack a usable docstring. Intended for humans and codi

## superpowers/docify-orchestrate/SKILL.md#chunk-1

- suite: docify
- scope: suite
- lexical: 1.0
- semantic: 0.1952
- hybrid: 0.6426
- recency: 0.4253
- suite_affinity: 0.0
- confidence: high
- rationale: matched terms: docstring

--- name: docify-orchestrate description: Routes agents to Docify documentation tasks — governance check/solve tracks, Python docstring audit, drift hints, inline source explain (PEP 8 comments), slice-based fixes, JSON reports. Triggers on docify, docify orchestrate, documentati
