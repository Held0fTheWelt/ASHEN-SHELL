"""Scaffold component UML packages (one-off migration helper)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "UML" / "Components"
PACKAGES = {
    "story-runtime-core": {
        "sad": "story-runtime-core",
        "seq": "story-runtime-core-shared-import-sequence",
        "mermaid_seq": """sequenceDiagram
  participant WE as world-engine
  participant SRC as story_runtime_core
  WE->>SRC: load builtin template / catalog
  SRC-->>WE: template data only
  Note over WE: commit stays in world-engine""",
        "ctx": """flowchart TD
  BE["backend tests"] --> SRC["story_runtime_core"]
  WE["world-engine"] --> SRC""",
        "container": """flowchart TD
  subgraph src["story_runtime_core"]
    BT["builtin templates"]
    BR["branching helpers"]
    LC["locale / recovery"]
  end""",
    },
    "frontend": {
        "sad": "frontend",
        "seq": "frontend-play-turn-sequence",
        "mermaid_seq": """sequenceDiagram
  participant P as Player
  participant F as frontend
  participant B as backend
  P->>F: submit input
  F->>B: REST turn API
  B-->>F: blocks + bootstrap
  F->>F: block renderer""",
        "ctx": """flowchart TD
  P["Player"] --> F["frontend"]
  F --> B["backend"]""",
        "container": """flowchart TD
  subgraph fe["frontend"]
    APP["app routes"]
    BR["block renderer"]
    PB["player_backend bridge"]
  end""",
    },
    "mcp-server": {
        "sad": "mcp-server",
        "seq": "mcp-server-tool-invoke-sequence",
        "mermaid_seq": """sequenceDiagram
  participant O as Operator IDE
  participant M as mcp-server
  participant B as backend
  O->>M: MCP tool call
  M->>B: read/diagnostic route
  B-->>M: bounded payload
  M-->>O: tool result""",
        "ctx": """flowchart TD
  Dev["Developer / operator"] --> MCP["tools/mcp_server"]
  MCP --> BE["backend read surfaces"]
  MCP --> CS["ai_stack canonical surface"]""",
        "container": """flowchart TD
  subgraph mcp["tools/mcp_server"]
    H["handlers"]
    SF["session factories"]
  end""",
    },
    "content-authority": {
        "sad": "content-authority",
        "seq": "content-publish-compile-sequence",
        "mermaid_seq": """sequenceDiagram
  participant A as Author YAML
  participant BE as backend compiler
  participant WE as world-engine
  A->>BE: module publish
  BE->>BE: compile projection
  BE-->>WE: load runtime projection""",
        "ctx": """flowchart TD
  YAML["content/modules"] --> BE["backend compile"]
  BE --> WE["world-engine load"]""",
        "container": """flowchart TD
  subgraph content["content/modules/god_of_carnage"]
    MY["module.yaml"]
    CP["canonical_path"]
  end""",
    },
    "administration-tool": {
        "sad": "administration-tool",
        "seq": "admin-governance-sequence",
        "mermaid_seq": """sequenceDiagram
  participant Op as Operator
  participant ADM as administration-tool
  participant BE as backend
  Op->>ADM: manage action
  ADM->>BE: governance API
  BE-->>ADM: diagnostics / status""",
        "ctx": """flowchart TD
  Op["Operator"] --> ADM["administration-tool"]
  ADM --> BE["backend governance"]""",
        "container": """flowchart TD
  subgraph adm["administration-tool"]
    RT["route registration"]
    MG["manage UI"]
  end""",
    },
}

for name, cfg in PACKAGES.items():
    base = ROOT / name
    for sub in ("components", "sequence"):
        (base / sub).mkdir(parents=True, exist_ok=True)
    sad = cfg["sad"]
    (base / "README.md").write_text(
        f"""# {name} UML

**SAD:** [{sad} architecture](../../../docs/architecture/components/{sad}/architecture.md)

## Reading order

1. [C4 context](components/c4-context.md)
2. [C4 container](components/c4-container.md)
3. [Primary sequence](sequence/{cfg['seq']}.md)
4. [TRACEABILITY](TRACEABILITY.md)
""",
        encoding="utf-8",
    )
    (base / "components" / "c4-context.md").write_text(
        f"# {name} — System Context\n\n```mermaid\n{cfg['ctx']}\n```\n",
        encoding="utf-8",
    )
    (base / "components" / "c4-container.md").write_text(
        f"# {name} — Containers\n\n```mermaid\n{cfg['container']}\n```\n",
        encoding="utf-8",
    )
    (base / "sequence" / f"{cfg['seq']}.md").write_text(
        f"# {name} primary sequence\n\n```mermaid\n{cfg['mermaid_seq']}\n```\n",
        encoding="utf-8",
    )
    (base / "TRACEABILITY.md").write_text(
        f"""# {name} TRACEABILITY

| Diagram | Claim | Source | Test / gate |
| --- | --- | --- | --- |
| c4-context | Scope per SAD | docs/architecture/components/{sad}/architecture.md | component tests |
| primary sequence | Runtime view §6 | SAD §6 | suite tests |
""",
        encoding="utf-8",
    )
print("scaffolded", len(PACKAGES), "component UML packages")
