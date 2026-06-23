#!/usr/bin/env python3
"""Emit runtime contract table rows for normative-contracts-index."""
from pathlib import Path

RUNTIME = Path(__file__).resolve().parents[1] / "docs" / "architecture" / "contracts" / "runtime"
OWNING = {
    "runtime-authority-and-state-flow.md": "world-engine + backend",
    "world_engine_authoritative_runtime_and_system_interactions.md": "world-engine",
    "world_engine_authoritative_narrative_commit.md": "world-engine",
    "a1_free_input_primary_runtime_path.md": "frontend + world-engine",
    "player_input_interpretation_contract.md": "ai-stack",
    "director_realization_thin_path_contract.md": "world-engine + ai-stack",
    "story_runtime_complete_playable_mvp.md": "world-engine",
    "runtime_diagnostic_snapshot_v1_contract.md": "observability project SAD",
}
DEFAULT_OWNER = "ai-stack + world-engine"

files = sorted(p.name for p in RUNTIME.glob("*.md") if p.name != "README.md")
print("| Document | Owning SAD | Binding scope |")
print("| --- | --- | --- |")
for name in files:
    owner = OWNING.get(name, DEFAULT_OWNER)
    scope = name.replace("_", " ").replace(".md", "").replace("-", " ")
    print(f"| [`{name}`](../../architecture/contracts/runtime/{name}) | {owner} | Pi-scoped runtime aspect: {scope} |")
