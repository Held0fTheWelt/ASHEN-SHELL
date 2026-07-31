"""Wave 8: out_of_scope reasons must carry a closed category."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.architecture_assurance.out_of_scope_policy import (
    OUT_OF_SCOPE_CATEGORIES,
    OUT_OF_SCOPE_MAX_SHARE,
    format_out_of_scope_reason,
    out_of_scope_share,
    parse_out_of_scope_reason,
)
from tools.architecture_assurance.schemas import SchemaValidationError, validate_manifest

REPO_ROOT = Path(__file__).resolve().parents[2]
BINDINGS = list((REPO_ROOT / "docs" / "architecture").rglob("architecture.bindings.json"))
SHARE_BASELINE = (
    REPO_ROOT / "docs" / "superpowers" / "plans" / "baselines" / "W8-out-of-scope-share.json"
)


def test_out_of_scope_requires_reason_category() -> None:
    category, detail = parse_out_of_scope_reason("archived: leftover scan unit")
    assert category == "archived"
    assert detail.startswith("leftover")
    with pytest.raises(ValueError):
        parse_out_of_scope_reason("no category here")
    with pytest.raises(ValueError):
        parse_out_of_scope_reason("generated:")


def test_out_of_scope_categories_are_closed() -> None:
    assert OUT_OF_SCOPE_CATEGORIES == frozenset(
        {"generated", "vendored", "test-fixture", "archived"}
    )
    assert format_out_of_scope_reason("test-fixture", "synth").startswith("test-fixture:")


def test_validate_manifest_rejects_uncategorized_out_of_scope() -> None:
    manifest = {
        "schema_version": "bt.architecture_bindings.v1",
        "generator": "test",
        "subsystem": "demo",
        "scope": ["demo"],
        "critical": False,
        "sad_path": "docs/architecture/components/backend/architecture.md",
        "lanes": ["product"],
        "building_blocks": [],
        "decisions": [],
        "discovered_units": [
            {
                "id": "u1",
                "anchor": {
                    "schema_version": "bt.source_anchor.v1",
                    "kind": "file",
                    "file": "x.py",
                    "line": 1,
                },
            }
        ],
        "representation_map": {},
        "out_of_scope": {"u1": "missing category"},
        "required_views": [],
    }
    with pytest.raises(SchemaValidationError, match="category"):
        validate_manifest(manifest)


def test_committed_bindings_out_of_scope_are_categorized() -> None:
    assert BINDINGS, "expected architecture.bindings.json files"
    for path in BINDINGS:
        data = json.loads(path.read_text(encoding="utf-8"))
        oos = data.get("out_of_scope") or {}
        for unit_id, reason in oos.items():
            category, _detail = parse_out_of_scope_reason(str(reason))
            assert category in OUT_OF_SCOPE_CATEGORIES, f"{path}:{unit_id}"


def test_out_of_scope_share_does_not_regress_baseline() -> None:
    """Cap + baseline: shares may not worsen beyond recorded Wave-8 baseline."""
    assert SHARE_BASELINE.is_file(), f"missing baseline {SHARE_BASELINE}"
    baseline = json.loads(SHARE_BASELINE.read_text(encoding="utf-8"))
    assert baseline.get("max_share_cap") == OUT_OF_SCOPE_MAX_SHARE
    current: dict[str, float] = {}
    for path in BINDINGS:
        rel = path.relative_to(REPO_ROOT).as_posix()
        data = json.loads(path.read_text(encoding="utf-8"))
        discovered = len(data.get("discovered_units") or [])
        oos = len(data.get("out_of_scope") or {})
        share = out_of_scope_share(discovered, oos)
        current[rel] = round(share, 6)
        assert share <= OUT_OF_SCOPE_MAX_SHARE + 1e-9
        prior = baseline["shares"].get(rel)
        if prior is not None:
            assert share <= float(prior) + 1e-6, (
                f"out_of_scope share regressed for {rel}: {share} > {prior}"
            )
    # Baseline must list every current bindings file (no silent drops).
    missing = sorted(set(current) - set(baseline["shares"]))
    assert not missing, f"baseline missing shares for: {missing}"
