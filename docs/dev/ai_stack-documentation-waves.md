# ai_stack documentation (wave plan)

Goal: **accurate, concise English docstrings** (module, class, public callables) without placeholder noise. Work is split into **waves** so each PR stays reviewable.

## Principles

- Read the implementation (and any contract types) before writing; docstrings state **what is true today**, not aspirations.
- Keep **Google-style** sections where the audit expects them (`Args:`, `Returns:` when annotated).
- After each wave: `python "./'fy'-suites/docify/tools/python_documentation_audit.py" --root ai_stack --google-docstring-audit` and targeted `pytest` for touched areas.

## Wave size

- Target **roughly 6–12 modules per wave** (or one cohesive subsystem, e.g. “RAG retrieval only”), whichever is smaller.
- Prefer one **logical PR** per wave; avoid mixing unrelated subsystems.

## Suggested wave order

Waves follow dependency and reviewer mental load (adjust as needed):

1. **Contracts and types** — `*_contract.py`, core DTOs and literals used everywhere.
2. **Research store and contracts** — `research_contract.py`, `research_store.py`, ingestion boundaries.
3. **RAG core** — corpus, retriever, governance, bootstrap; then context pack assembly.
4. **LangGraph runtime** — executor, state, package output (split across multiple waves if large).
5. **GoC / scene / semantic planner** — scene director, semantic moves, gates.
6. **MCP and capabilities** — surfaces and registries.
7. **Remaining leaf modules** — catch stragglers; nested helpers only when part of the public story.

## Definition of done (per module in a wave)

- Module docstring: **one short paragraph** on role and main exports (if `__all__` or obvious entrypoints).
- Public classes: **purpose + invariants** the type actually enforces (or “data container for …” when accurate).
- Public functions/methods: **verb-led summary**, `Args`/`Returns` lines that name **semantic constraints** (not type repetition only), and raises only when the code raises.

## Tooling (support only)

Docify synthesizers under `'fy'-suites/docify/tools/` may emit **neutral scaffolding**; they do **not** replace reading the code. Regenerate or repair only when you intend to normalise layout; then **edit prose in the same wave**.

See also: [`docs/dev/architecture/ai-stack-rag-langgraph-and-goc-seams.md`](architecture/ai-stack-rag-langgraph-and-goc-seams.md) for subsystem boundaries.
