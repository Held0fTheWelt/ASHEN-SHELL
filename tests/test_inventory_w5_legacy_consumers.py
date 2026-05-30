"""Smoke tests for ``scripts/inventory_w5_legacy_consumers.py``.

The inventory script is intentionally non-failing — these tests verify that
the script runs to completion, finds the expected substrate keywords, and
flags no forbidden package references in the working tree.
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "inventory_w5_legacy_consumers.py"


def _load_module():
    name = "inventory_w5_legacy_consumers"
    spec = importlib.util.spec_from_file_location(name, SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Register before execution so @dataclass can resolve ``cls.__module__``.
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def inventory_module():
    return _load_module()


@pytest.fixture(scope="module")
def inventory_report(inventory_module):
    return inventory_module.scan(REPO_ROOT)


def test_script_exists() -> None:
    assert SCRIPT_PATH.is_file(), f"missing script at {SCRIPT_PATH}"


def test_legacy_surfaces_are_declared(inventory_module) -> None:
    keys = {key for key, _ in inventory_module.LEGACY_SURFACES}
    # The Phase 6A inventory requires every surface listed in the migration
    # plan to be scanned for.
    required = {
        "current_room",
        "current_room_id",
        "current_area",
        "previous_room_id",
        "actor_locations",
        "visible_room_ids",
        "visible_occupants",
        "complete_actor_locations_for_gathering",
        "gathering_scene_id",
        "transition_from_previous",
        "location_changed",
        "forbidden_ai_stack_actor_situation",
        "forbidden_ai_stack_w5_actor_situation",
    }
    missing = required - keys
    assert not missing, f"inventory script is missing surfaces: {sorted(missing)}"


def test_scan_completes_and_finds_substrate_consumers(inventory_report) -> None:
    assert inventory_report.files_scanned > 0
    counts = inventory_report.by_surface()
    # The substrate writer + dataclass + tests guarantee these are present.
    assert counts["current_room_id"] > 0
    assert counts["actor_locations"] > 0


def test_no_forbidden_package_references(inventory_report) -> None:
    """Phase 6A guarantees: no active import of ``ai_stack/actor_situation``
    or ``ai_stack/w5_actor_situation`` exists."""
    forbidden = [
        f
        for f in inventory_report.findings
        if f.surface
        in {
            "forbidden_ai_stack_actor_situation",
            "forbidden_ai_stack_w5_actor_situation",
        }
    ]
    # Permit the term to appear inside the inventory documents themselves
    # (they discuss the forbidden packages by name) and inside this script.
    allowed_paths = {
        "docs/MVPs/w5_legacy_consumer_removal_inventory.md",
        "docs/MVPs/w5_actor_tracking_migration.md",
        "scripts/inventory_w5_legacy_consumers.py",
        "tests/test_inventory_w5_legacy_consumers.py",
    }
    unexpected = [f for f in forbidden if f.path not in allowed_paths]
    assert not unexpected, (
        "Forbidden package references found outside allowed documentation: "
        + ", ".join(f"{f.path}:{f.line}" for f in unexpected)
    )


def test_stale_worktrees_excluded_from_scan(inventory_report) -> None:
    """Phase 6B-6A.5: .worktrees/ and .claude/worktrees/ are auxiliary git
    workspaces, not active source. The scanner must exclude them so stale
    historical symbols in those directories do not trigger forbidden-import or
    old-name violations against the active tree."""
    worktree_findings = [
        f for f in inventory_report.findings
        if f.path.startswith(".worktrees/") or f.path.startswith(".claude/worktrees/")
    ]
    assert not worktree_findings, (
        "Stale worktree paths must be excluded from the active-source scan: "
        + ", ".join(f"{f.path}:{f.line}" for f in worktree_findings[:5])
    )


def test_state_tmp_excluded_from_scan(inventory_report) -> None:
    """Phase 6B-6A.5: .state_tmp/ is a scratch/backup workspace, not active
    source. Excluding it prevents stale manager snapshots from triggering
    violations."""
    state_tmp_findings = [
        f for f in inventory_report.findings
        if f.path.startswith(".state_tmp/")
    ]
    assert not state_tmp_findings, (
        ".state_tmp/ must be excluded from the active-source scan: "
        + ", ".join(f"{f.path}:{f.line}" for f in state_tmp_findings[:5])
    )


def test_main_returns_zero_and_emits_json(inventory_module) -> None:
    buffer = io.StringIO()
    saved_argv = sys.argv[:]
    try:
        sys.argv = ["inventory_w5_legacy_consumers.py", "--root", str(REPO_ROOT), "--json"]
        with redirect_stdout(buffer):
            rc = inventory_module.main(["--root", str(REPO_ROOT), "--json"])
    finally:
        sys.argv = saved_argv
    assert rc == 0
    payload = json.loads(buffer.getvalue())
    assert payload["root"]
    assert payload["files_scanned"] > 0
    assert "counts_by_surface" in payload


# ---------------------------------------------------------------------------
# Phase 6B-0 rename guarantees (R1–R5)
# ---------------------------------------------------------------------------


def test_renamed_validation_function_is_importable() -> None:
    """R1: ``validate_w5_actor_tracking`` is the live name and reachable from
    the package public API."""

    from ai_stack.actor_tracking import validate_w5_actor_tracking
    from ai_stack.actor_tracking.validation import (
        validate_w5_actor_tracking as direct,
    )

    assert callable(validate_w5_actor_tracking)
    assert validate_w5_actor_tracking is direct


def test_old_validation_function_is_absent() -> None:
    """R1: the deprecated ``validate_w5_actor_situation`` symbol must no
    longer exist as an importable name. We deliberately do not retain a
    backward alias — the call graph is enumerated and small."""

    import ai_stack.actor_tracking as pkg
    import ai_stack.actor_tracking.validation as validation_module

    assert not hasattr(pkg, "validate_w5_actor_situation")
    assert not hasattr(validation_module, "validate_w5_actor_situation")
    assert "validate_w5_actor_situation" not in pkg.__all__
    assert "validate_w5_actor_situation" not in validation_module.__all__


def test_no_production_callsite_references_old_validation_name(inventory_report) -> None:
    """R1: no production (non-test, non-doc, non-inventory) code references
    the old function name. The historical sentence in
    ``ai_stack/actor_tracking/__init__.py`` does not name the function."""

    findings = [
        f for f in inventory_report.findings if f.surface == "validate_w5_actor_situation_old"
    ]
    allowed_paths = {
        # Inventory + planning surfaces are allowed to reference the old name.
        "docs/MVPs/w5_legacy_consumer_removal_inventory.md",
        "docs/MVPs/w5_actor_tracking_migration.md",
        "scripts/inventory_w5_legacy_consumers.py",
        "tests/test_inventory_w5_legacy_consumers.py",
    }
    unexpected = [
        f
        for f in findings
        if f.path not in allowed_paths and not f.path.startswith("'fy'-suites/")
    ]
    assert not unexpected, (
        "Old function name still referenced outside allowed inventory surfaces: "
        + ", ".join(f"{f.path}:{f.line}" for f in unexpected)
    )


def test_new_validation_failure_class_string_is_in_use() -> None:
    """R2: production code emits the new failure_class string."""

    from ai_stack.story_runtime.turn import god_of_carnage_turn_seams_validation as mod

    src = Path(mod.__file__).read_text(encoding="utf-8")
    assert '"w5_actor_tracking_validation"' in src
    assert '"w5_actor_situation_validation"' not in src


def test_no_production_callsite_references_old_failure_class_string(inventory_report) -> None:
    """R2: the old failure_class literal must not appear in production code.
    Inventory docs and the script may reference the historical name."""

    findings = [
        f
        for f in inventory_report.findings
        if f.surface == "w5_actor_situation_validation_old"
    ]
    allowed_paths = {
        "docs/MVPs/w5_legacy_consumer_removal_inventory.md",
        "docs/MVPs/w5_actor_tracking_migration.md",
        "scripts/inventory_w5_legacy_consumers.py",
        "tests/test_inventory_w5_legacy_consumers.py",
    }
    unexpected = [
        f
        for f in findings
        if f.path not in allowed_paths and not f.path.startswith("'fy'-suites/")
    ]
    assert not unexpected, (
        "Old failure_class string still present outside allowed inventory surfaces: "
        + ", ".join(f"{f.path}:{f.line}" for f in unexpected)
    )


def test_renamed_docstring_paths_point_at_current_files() -> None:
    """R3, R4, R5: docstrings must reference the current ADR + migration
    doc filenames, not the renamed-away historical filenames."""

    import ai_stack.actor_tracking as pkg
    import ai_stack.actor_tracking.models as models
    import ai_stack.actor_tracking.extractor as extractor
    import ai_stack.actor_tracking.projection as projection

    # Current names are present.
    assert "adr-0063-w5-actor-tracking.md" in (models.__doc__ or "")
    assert "w5_actor_tracking_migration.md" in (pkg.__doc__ or "")
    assert "w5_actor_tracking_migration.md" in (extractor.__doc__ or "")
    assert "w5_actor_tracking_migration.md" in (projection.__doc__ or "")

    # Renamed-away historical filenames must not appear as current refs.
    for mod_doc in (
        models.__doc__,
        extractor.__doc__,
        projection.__doc__,
    ):
        assert "adr-0063-w5-actor-situation-tracker.md" not in (mod_doc or "")
        assert "w5_actor_situation_migration.md" not in (mod_doc or "")


def test_current_code_uses_actor_tracking_package() -> None:
    """The production validation seam imports from ``ai_stack.actor_tracking``
    only — never from any of the forbidden historical packages."""

    from ai_stack.story_runtime.turn import god_of_carnage_turn_seams_validation as mod

    src = Path(mod.__file__).read_text(encoding="utf-8")
    assert "from ai_stack.actor_tracking" in src
    assert "from ai_stack.actor_situation" not in src
    assert "from ai_stack.w5_actor_situation" not in src
    assert "import ai_stack.actor_situation" not in src
    assert "import ai_stack.w5_actor_situation" not in src


# ---------------------------------------------------------------------------
# Phase 6B-9 — ADR-0069 surface coverage guarantees
# ---------------------------------------------------------------------------


def test_phase_6b9_surfaces_are_declared(inventory_module) -> None:
    """Phase 6B-9: viewer_room_id and w5_player_view must be in the scanner."""
    keys = {key for key, _ in inventory_module.LEGACY_SURFACES}
    assert "viewer_room_id" in keys, "viewer_room_id surface missing from LEGACY_SURFACES"
    assert "w5_player_view" in keys, "w5_player_view surface missing from LEGACY_SURFACES"


def test_phase_6b9_taxonomy_extended(inventory_module) -> None:
    """Phase 6B-9 taxonomy must include w5_first_already_migrated."""
    assert "w5_first_already_migrated" in inventory_module.PHASE_6B4_TAXONOMY, (
        "PHASE_6B4_TAXONOMY must include w5_first_already_migrated for Phase 6B-9 (ADR-0069)"
    )
    assert "still_needed_public_client_compatibility" in inventory_module.PHASE_6B4_TAXONOMY
    assert "deprecated_public_client_alias_keep" in inventory_module.PHASE_6B4_TAXONOMY
    assert "public_authority" in inventory_module.PHASE_6B4_TAXONOMY


def test_scan_finds_viewer_room_id(inventory_report) -> None:
    """viewer_room_id appears in both RuntimeSnapshot definitions."""
    counts = inventory_report.by_surface()
    assert counts.get("viewer_room_id", 0) > 0, (
        "viewer_room_id must appear in scan results (present in RuntimeSnapshot model fields)"
    )


def test_scan_finds_w5_player_view(inventory_report) -> None:
    """w5_player_view appears in the player-shell projection and session state view."""
    counts = inventory_report.by_surface()
    assert counts.get("w5_player_view", 0) > 0, (
        "w5_player_view must appear in scan results (present in player_shell_state_projection.py "
        "and session_state_w5_view.py)"
    )


def test_phase_6b9_classification_entries_present(inventory_module) -> None:
    """Phase 6B-9 classification entries must be present for new surfaces."""
    assert "viewer_room_id" in inventory_module.PHASE_6B4_CLASSIFICATION, (
        "viewer_room_id must have a PHASE_6B4_CLASSIFICATION entry"
    )
    assert "w5_player_view" in inventory_module.PHASE_6B4_CLASSIFICATION, (
        "w5_player_view must have a PHASE_6B4_CLASSIFICATION entry"
    )
    assert "needs_dedicated_adr_before_removal" in inventory_module.PHASE_6B4_CLASSIFICATION["viewer_room_id"]
    assert "w5_first_already_migrated" in inventory_module.PHASE_6B4_CLASSIFICATION["w5_player_view"]


def test_phase_6b12_public_alias_classifications(inventory_module) -> None:
    """Phase 6B-12 marks public room aliases as deprecated keeps, not legacy to retain."""

    for key in ("viewer_room_id", "current_room", "current_room_id"):
        label = inventory_module.PHASE_6B4_CLASSIFICATION[key]
        assert "deprecated_public_client_alias_keep" in label
        assert "needs_dedicated_adr_before_removal" in label

    assert "public_authority" in inventory_module.PHASE_6B4_CLASSIFICATION["w5_player_view"]
    assert "runtime_world.current_room_id" in inventory_module.PHASE_6B4_CLASSIFICATION["current_room_id"]
    assert "environment_state.current_room_id" in inventory_module.PHASE_6B4_CLASSIFICATION["current_room_id"]
    assert "substrate_keep_future_adr" in inventory_module.PHASE_6B4_CLASSIFICATION["actor_locations"]
    assert (
        "substrate_keep_future_adr"
        in inventory_module.PHASE_6B4_CLASSIFICATION["complete_actor_locations_for_gathering"]
    )


def test_phase_6b13_readiness_report_blocks_alias_removal(inventory_module) -> None:
    """Phase 6B-13 gate is non-failing but explicitly not removal-ready."""

    report = inventory_module.phase_6b13_readiness_report()

    assert report["phase"] == "6B-13"
    assert report["public_aliases_still_emitted"] is True
    assert report["w5_player_view_authority_present"] is True
    assert report["frontend_helpers_prefer_w5"] is True
    assert report["legacy_fallback_still_tested"] is True
    assert report["docs_describe_aliases_as_primary"] is False
    assert report["removal_ready"] is False
    assert report["reason"] == "client_readiness_window_active"
    assert "required_evidence_before_removal_adr" in report


def test_phase_6b13_readiness_report_is_in_json_output(inventory_module) -> None:
    buffer = io.StringIO()

    with redirect_stdout(buffer):
        rc = inventory_module.main(["--root", str(REPO_ROOT), "--json"])

    assert rc == 0
    payload = json.loads(buffer.getvalue())
    readiness = payload["phase_6b13_readiness"]
    assert readiness["public_aliases_still_emitted"] is True
    assert readiness["w5_player_view_authority_present"] is True
    assert readiness["removal_ready"] is False
    assert readiness["reason"] == "client_readiness_window_active"


# ---------------------------------------------------------------------------
# Phase 6C-0 — narrator consequence / sensory location-framing inventory
# ---------------------------------------------------------------------------


def test_phase_6c0_surfaces_are_declared(inventory_module) -> None:
    keys = {key for key, _ in inventory_module.LEGACY_SURFACES}
    for key in {
        "from_area",
        "to_area",
        "scene_changed",
        "narrator_consequence",
        "sensory_context",
        "language_adapter",
        "movement_framing",
        "transition_framing",
    }:
        assert key in keys


def test_phase_6c0_taxonomy_labels_are_available(inventory_module) -> None:
    taxonomy = set(inventory_module.PHASE_6B4_TAXONOMY)
    for label in {
        "w5_first_migration_candidate",
        "substrate_keep_future_adr",
        "public_compatibility_keep",
        "test_only_update",
        "doc_only_update",
        "unrelated_domain_use",
        "needs_dedicated_adr",
        "unknown_needs_runtime_trace",
    }:
        assert label in taxonomy


def test_phase_6c0_location_framing_inventory_is_complete(inventory_module) -> None:
    rows = inventory_module.phase_6c0_location_framing_inventory()
    assert rows
    required_keys = {
        "file_path",
        "line",
        "symbol",
        "classification",
        "surface_kind",
        "current_role",
        "legacy_fields",
        "w5_replacement_surface",
        "migration_risk",
        "tests_required",
    }
    for row in rows:
        assert required_keys <= row.keys()
        assert row["file_path"]
        assert row["symbol"]
        assert row["current_role"]
        assert row["w5_replacement_surface"]
        assert row["migration_risk"]
        assert isinstance(row["tests_required"], list)
        assert row["tests_required"]

    by_symbol = {str(row["symbol"]): row for row in rows}
    assert by_symbol["_current_context_area"]["classification"] == "w5_first_migration_candidate"
    assert by_symbol["_base_local_context_transition"]["classification"] == "w5_first_migration_candidate"
    assert by_symbol["_current_location_id"]["classification"] == "w5_first_migration_candidate"
    assert by_symbol["_interaction_surface_cached"]["classification"] == "w5_first_migration_candidate"
    assert (
        by_symbol["_apply_environment_movement / apply_action_to_environment_state"]["classification"]
        == "substrate_keep_future_adr"
    )
    assert by_symbol["RuntimeSnapshot.viewer_room_id/current_room"]["classification"] == "public_compatibility_keep"
    assert by_symbol["ShortTermContext.build"]["classification"] == "unrelated_domain_use"
    assert by_symbol["LocalContextTransition assertions"]["classification"] == "test_only_update"
    assert by_symbol["ADR-0069"]["classification"] == "doc_only_update"


def test_phase_6c0_inventory_mentions_required_runtime_files(inventory_module) -> None:
    paths = {row["file_path"] for row in inventory_module.phase_6c0_location_framing_inventory()}
    assert "ai_stack/contracts/narrator_consequence_contracts.py" in paths
    assert "ai_stack/story_runtime/narrative/sensory_context_engine.py" in paths
    assert "ai_stack/language_io/language_adapter.py" in paths
    assert "ai_stack/langgraph/runtime_executor/executor_action_resolution_commit.py" in paths
    assert "ai_stack/langgraph/runtime_executor/executor_symbolic_meta_genre_derivation.py" in paths
    assert "ai_stack/contracts/environment_state_contracts.py" in paths


def test_phase_6c0_implementation_plan_defers_runtime_migration(inventory_module) -> None:
    plan = inventory_module.phase_6c0_implementation_plan()
    assert plan["phase"] == "6C-0"
    assert plan["adr"] == "ADR-0070"
    assert plan["runtime_implementation_in_phase_6c0"] is False
    assert "LocalContextTransition" in plan["implementation_deferred_reason"]
    assert plan["proposed_helper_module"] == "ai_stack/actor_tracking/location_framing.py"
    assert "malformed-W5 safety fallback" in plan["fallback_posture"]
    assert "public aliases" in plan["fallback_posture"]


def test_phase_6c0_inventory_and_plan_are_in_json_output(inventory_module) -> None:
    buffer = io.StringIO()

    with redirect_stdout(buffer):
        rc = inventory_module.main(["--root", str(REPO_ROOT), "--json"])

    assert rc == 0
    payload = json.loads(buffer.getvalue())
    assert payload["phase_6c0_location_framing_inventory"]
    assert payload["phase_6c0_implementation_plan"]["adr"] == "ADR-0070"


def test_phase_6c1_location_framing_report_records_helper_status(inventory_module) -> None:
    report = inventory_module.phase_6c1_location_framing_report()

    assert report["phase"] == "6C-1"
    assert report["helper_module"] == "ai_stack/actor_tracking/location_framing.py"
    assert report["helper_schema_version"] == "w5_location_framing.v1"
    assert "build_w5_location_framing" in report["helper_functions"]
    assert "location_framing_to_local_context_transition" in report["helper_functions"]
    assert report["typed_coercion_required"] is True
    assert report["raw_w5_history_emitted"] is False
    assert report["how_first_class"] is True
    assert report["inferred_why_soft_truth"] is True
    assert report["legacy_fallback_retained"] is True
    assert report["public_aliases_removed"] is False
    assert report["substrate_fields_removed"] is False
    assert report["default_graph_synthesizes_w5_location_framing"] is False


def test_phase_6c1_location_framing_report_is_in_json_output(inventory_module) -> None:
    buffer = io.StringIO()

    with redirect_stdout(buffer):
        rc = inventory_module.main(["--root", str(REPO_ROOT), "--json"])

    assert rc == 0
    payload = json.loads(buffer.getvalue())
    report = payload["phase_6c1_location_framing"]
    assert report["phase"] == "6C-1"
    assert report["helper_module"] == "ai_stack/actor_tracking/location_framing.py"
    assert report["public_aliases_removed"] is False
    assert report["default_graph_synthesizes_w5_location_framing"] is False


def test_phase_6c2_location_framing_report_records_graph_synthesis(inventory_module) -> None:
    report = inventory_module.phase_6c2_location_framing_report()

    assert report["phase"] == "6C-2"
    assert report["graph_owned_synthesis"] is True
    assert report["synthesis_point"] == "ai_stack/langgraph/runtime_executor/executor_action_resolution_commit.py"
    assert report["synthesis_symbol"] == "_resolve_player_action SOURCE_LINES"
    assert report["state_field"] == "w5_location_framing"
    assert report["typed_coercion_required"] is True
    assert report["raw_w5_history_emitted"] is False
    assert report["committed_events_mutated"] is False
    assert report["legacy_fallback_retained"] is True
    assert report["current_area_from_area_to_area_removed"] is False
    assert report["public_aliases_removed"] is False
    assert report["substrate_fields_removed"] is False
    assert report["default_authority_switch_complete"] is False
    assert "w5_location_framing_used" in report["diagnostics"]
    assert "sensory context same-location resolution matches legacy current_area resolution" in report["parity_evidence"]


def test_phase_6c2_location_framing_report_is_in_json_output(inventory_module) -> None:
    buffer = io.StringIO()

    with redirect_stdout(buffer):
        rc = inventory_module.main(["--root", str(REPO_ROOT), "--json"])

    assert rc == 0
    payload = json.loads(buffer.getvalue())
    report = payload["phase_6c2_location_framing"]
    assert report["phase"] == "6C-2"
    assert report["graph_owned_synthesis"] is True
    assert report["synthesis_symbol"] == "_resolve_player_action SOURCE_LINES"
    assert report["default_authority_switch_complete"] is False
    assert report["committed_events_mutated"] is False


def test_phase_6c3_location_framing_authority_report_records_w5_first_switch(inventory_module) -> None:
    report = inventory_module.phase_6c3_location_framing_authority_report()

    assert report["phase"] == "6C-3"
    assert report["w5_first_authority_switch"] is True
    assert report["authority_surface"] == "ai_stack/actor_tracking/location_framing.py"
    assert report["legacy_fallback_retained"] is True
    assert report["current_area_from_area_to_area_removed"] is False
    assert report["public_aliases_removed"] is False
    assert report["substrate_fields_removed"] is False
    assert report["committed_events_mutated"] is False
    assert "location_framing_authority" in report["diagnostics"]
    assert "local_context_transition_source" in report["diagnostics"]
    assert "missing_w5" in report["legacy_fallback_conditions"]
    assert report["next_phase"] == "6C-4 fresh inventory and targeted cleanup planning only"


def test_phase_6c3_location_framing_authority_report_is_in_json_output(inventory_module) -> None:
    buffer = io.StringIO()

    with redirect_stdout(buffer):
        rc = inventory_module.main(["--root", str(REPO_ROOT), "--json"])

    assert rc == 0
    payload = json.loads(buffer.getvalue())
    report = payload["phase_6c3_location_framing_authority"]
    assert report["phase"] == "6C-3"
    assert report["w5_first_authority_switch"] is True
    assert report["legacy_fallback_retained"] is True
    assert report["current_area_from_area_to_area_removed"] is False


def test_phase_6c0_adr_exists_and_records_decision() -> None:
    adr_path = (
        REPO_ROOT
        / "docs"
        / "ADR"
        / "adr-0070-w5-actor-tracking-replaces-narrator-consequence-location-framing.md"
    )
    assert adr_path.is_file()
    text = adr_path.read_text(encoding="utf-8")
    for phrase in (
        "W5 Actor Tracking Replaces Narrator Consequence Location Framing",
        "How remains first-class",
        "inferred Why remains soft truth",
        "public current_room/current_room_id/viewer_room_id aliases",
        "build_w5_location_framing",
        "location_changed",
        "malformed-W5 safety fallback",
    ):
        assert phrase in text
