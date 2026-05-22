from __future__ import annotations

import ast
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCOPED_HELPER_ROOTS = (
    REPO_ROOT / "ai_stack" / "contracts",
    REPO_ROOT / "story_runtime_core",
)


def test_duplicate_serialization_helpers_are_not_redeclared_in_contract_scopes() -> None:
    offenders: list[str] = []
    for root in SCOPED_HELPER_ROOTS:
        for path in root.rglob("*.py"):
            if path.name == "serialization.py":
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name in {"_json_safe", "_as_list"}:
                    offenders.append(str(path.relative_to(REPO_ROOT)))

    assert offenders == []


def test_ai_stack_contract_serialization_preserves_contract_shapes() -> None:
    from ai_stack.contracts.authority_contracts import NarratorAuthorityContract
    from ai_stack.contracts.serialization import as_list, json_safe, strict_list

    assert as_list(("a", "b")) == ["a", "b"]
    assert as_list("solo") == ["solo"]
    assert strict_list(("a", "b")) == []
    assert json_safe({"x": {1, 2}})["x"] in ([1, 2], [2, 1])

    payload = NarratorAuthorityContract(evidence_blocks=[{"raw": object()}]).to_dict()
    assert payload["evidence_blocks"][0]["raw"].startswith("<")


def test_story_runtime_core_serialization_keeps_deterministic_sets_and_strict_sequences() -> None:
    from story_runtime_core.serialization import json_safe, sequence_list

    assert json_safe({"x": {2, 1}}) == {"x": [1, 2]}
    assert sequence_list(("a", "b")) == ["a", "b"]
    assert sequence_list("solo") == []
