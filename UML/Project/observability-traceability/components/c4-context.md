# observability-traceability — System Context

```mermaid
flowchart LR
  WE["world-engine turns"] --> LF["Langfuse"]
  AI["ai_stack adapters"] --> LF
  BE["backend routes"] --> LF
  LF --> Ops["Operators / quality lab"]
```
