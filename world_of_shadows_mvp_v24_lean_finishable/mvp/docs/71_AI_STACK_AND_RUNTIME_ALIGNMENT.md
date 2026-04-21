# AI Stack and Runtime Alignment

The AI stack is included here as a real implementation surface, not merely as a future concept.

## Why it matters for the MVP

The earlier MVP package documented strong target behavior for:

- reaction,
- layered reasoning,
- intent interpretation,
- player-state modelling,
- context synthesis,
- dramatic planning,
- and bounded recovery.

The AI stack provides an important part of the implementation-side landing zone for those capabilities.

## Package policy

The AI stack must not silently replace runtime authority.
It must remain subordinate to world-engine truth and contract-governed surfaces.

That means AI-stack changes should be checked with:

- Contractify for boundary and contract coherence,
- Despaghettify for structural slice discipline,
- Docify for code-adjacent documentation follow-up,
- and runtime or acceptance tests where applicable.
