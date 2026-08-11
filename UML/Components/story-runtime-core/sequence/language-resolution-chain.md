# Language resolution chain (story-runtime-core ↔ ai_stack ↔ LangGraph)

Normative session language: [world-engine session language](../../../../docs/architecture/components/world-engine/architecture.md#session-language), [D14 ingress](../../../../docs/architecture/components/world-engine/architecture.md#d14-semantic-player-input-enters-once).

```mermaid
sequenceDiagram
  participant FE as frontend/backend
  participant WE as world-engine session
  participant LG as LangGraph executor
  participant SRC as story_runtime_core
  participant LA as ai_stack.language_io
  participant LLM as model adapter

  FE->>WE: session_output_language, session_input_language
  WE->>LG: RuntimeTurnState language fields

  Note over LG,LA: translate_player_input (graph entry)
  LG->>LA: prepare_player_input_semantic_resolution()
  LA->>LA: build_interaction_surface() [lru_cache]
  LA-->>LG: shell + semantic_resolution_contract
  alt input_lang == en
    LG-->>LG: skip translation (normalized = raw)
  else input_lang != en
    LG->>LLM: thin JSON translate prompt (no catalog)
    LLM-->>LG: normalized_english_text / semantic_action
  end

  Note over LG,SRC: interpret_input
  LG->>SRC: interpret_player_input(raw)
  opt normalized_english_text present
    LG->>SRC: interpret_player_input(english) again
  end
  LG-->>LG: merge translation shell + structural kind

  Note over LG,LA: resolve_player_action
  LG->>LA: build_interaction_surface() again via player_action_resolution
  alt no ai_semantic_resolution payload
    LG-->>LG: semantic_ai_resolution_required envelope
  end

  LG->>LLM: invoke_model (narrative / capability prompt)
  opt session_output_language != en
    LG->>LLM: translate_output (batch visible texts)
  end
```

## Multiplication points (audit notes)

| Step | What repeats | Owner |
| --- | --- | --- |
| Catalog surface | `build_interaction_surface` in translate shell, resolver, cached YAML scan | `ai_stack.language_io` |
| Structural interpret | `interpret_player_input` up to twice per turn | `story_runtime_core.input_interpreter` |
| LLM ingress | Thin translate vs unused `_semantic_translation_prompt` (full catalog) | `ai_stack.langgraph` |
| LLM egress | `translate_output` after narrator render | `ai_stack.langgraph` |
| Default language | `"de"` at ingress vs `"en"` at `translate_output` if state field missing | executor nodes |
