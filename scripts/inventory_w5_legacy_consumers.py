"""W5 Phase 6A — non-failing inventory reporter for legacy localization consumers.

Scans the working tree for the legacy localization / current-room surfaces
listed in ``docs/MVPs/w5_legacy_consumer_removal_inventory.md`` and prints a
summary by surface. **Always exits 0** — this is a planning aid, not a gate.

Usage:

    python scripts/inventory_w5_legacy_consumers.py
    python scripts/inventory_w5_legacy_consumers.py --json
    python scripts/inventory_w5_legacy_consumers.py --root D:/WorldOfShadows

The script is intentionally minimal: it greps the working tree for known
substrings, deduplicates by ``(path, line_number)``, and groups by surface.
It deliberately does not classify findings — classification belongs in the
inventory doc, which is the authoritative artifact.

Excluded directories: ``.git``, ``__pycache__``, ``node_modules``,
``'fy'-suites/delagecy``, ``'fy'-suites/docify``, and every ``audit_*.json``
or ``*.log`` artifact at the repository root.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


# Each entry: (key, regex pattern). Regexes use word boundaries where useful.
LEGACY_SURFACES: list[tuple[str, str]] = [
    ("current_room", r"\bcurrent_room\b"),
    ("current_room_id", r"\bcurrent_room_id\b"),
    ("current_area", r"\bcurrent_area\b"),
    ("previous_room_id", r"\bprevious_room_id\b"),
    ("actor_locations", r"\bactor_locations\b"),
    ("visible_room_ids", r"\bvisible_room_ids\b"),
    ("visible_occupants", r"\bvisible_occupants\b"),
    ("RuntimeVisibilityPolicy", r"\bRuntimeVisibilityPolicy\b"),
    ("complete_actor_locations_for_gathering", r"complete_actor_locations_for_gathering"),
    ("gathering_scene_id", r"\bgathering_scene_id\b"),
    ("derived_gathering_room_id", r"derived_gathering_room_id"),
    ("transition_from_previous", r"\btransition_from_previous\b"),
    ("location_changed", r"\blocation_changed\b"),
    ("forbidden_ai_stack_actor_situation", r"ai_stack[\\/]actor_situation\b"),
    ("forbidden_ai_stack_w5_actor_situation", r"ai_stack[\\/]w5_actor_situation\b"),
    ("w5_actor_situation_term", r"w5_actor_situation"),
    # Phase 6B-0 rename items. These should now be present (R1/R2) — they are
    # the new names — and the old names (validate_w5_actor_situation,
    # "w5_actor_situation_validation") should only appear in inventory/audit
    # artifacts after the rename lands. The scanner reports both so future
    # audits can confirm the rename did not regress.
    ("validate_w5_actor_situation_old", r"\bvalidate_w5_actor_situation\b"),
    ("validate_w5_actor_tracking_new", r"\bvalidate_w5_actor_tracking\b"),
    ("w5_actor_situation_validation_old", r"\bw5_actor_situation_validation\b"),
    ("w5_actor_tracking_validation_new", r"\bw5_actor_tracking_validation\b"),
    # Phase 6B-6A — diagnostics flag retirement surface.
    # These symbols are slated for removal in Phase 6B-6B (ADR-0066).
    # The scanner reports all occurrences so the retirement audit can verify
    # that every reference is addressed before Phase 6B-6B begins.
    ("narrator_legacy_compat_diag_flag", r"W5_AST_NARRATOR_LEGACY_COMPAT_DIAGNOSTICS_ENABLED"),
    ("narrator_legacy_compat_diag_fn", r"\bw5_ast_narrator_legacy_compat_diagnostics_enabled\b"),
    ("narrator_legacy_compat_diag_key", r"\bnarrator_legacy_compat_diagnostics\b"),
    ("legacy_compat_transition_write", r'_legacy_compat\[.transition_from_previous.\]'),
    ("demoted_to_legacy_compat", r"\bdemoted_to_legacy_compat\b"),
    ("removed_by_6b5e_policy", r"\bremoved_by_6b5e_policy\b"),
    ("legacy_transition_parity", r"\blegacy_transition_parity\b"),
    # Phase 6B-9 — public payload alias migration surfaces (ADR-0069).
    # viewer_room_id is a public WS RuntimeSnapshot compat alias slated for
    # Phase 6B-11 deprecation once Phase 6B-10 wires w5_player_view into WS.
    # w5_player_view is the W5 player-shell projection surface (current authority).
    ("viewer_room_id", r"\bviewer_room_id\b"),
    ("w5_player_view", r"\bw5_player_view\b"),
]


# Phase 6B-2 classification labels per surface. Informational only — the
# authoritative classification lives in the inventory doc's per-branch table.
# This map exists so the human-readable scan output can hint which surfaces
# fire under explicit opt-out (`O`), missing/malformed W5 (`M`), substrate
# reads (`S`), compatibility aliases for legacy clients (`L`), or are pure
# documentation/comment mentions (`D`).
PHASE_6B2_CLASSIFICATION: dict[str, str] = {
    "current_room": "L/S — compatibility alias on player-shell + WS payloads; also substrate read in runtime_world/environment_state",
    "current_room_id": "L/S — compatibility alias + Participant dataclass substrate field",
    "current_area": "S/L — substrate field; read by C5/C8 affordance + sensory engines (migrate_to_w5_first_before_removal)",
    "previous_room_id": "S — substrate field on environment_state",
    "actor_locations": "S — substrate field on environment_state; read by W5 extractor + Director baseline completion",
    "visible_room_ids": "S — substrate field on environment_state.visible_room_ids",
    "visible_occupants": "S — RuntimeVisibilityPolicy substrate field",
    "RuntimeVisibilityPolicy": "S — engine-level visibility substrate",
    "complete_actor_locations_for_gathering": "S — Director baseline completion algorithm; called by F1/F4/F5",
    "gathering_scene_id": "S — derived from actor_locations by F5; consumed by ADR-0061 pause predicate",
    "derived_gathering_room_id": "S — Director alias (also produced by F5)",
    "transition_from_previous": "removed_by_adr_0068 (Phase 6B-8) — strict-off rollback path removed; transition_from_previous no longer emitted by narrator source_facts; any remaining hits are doc/test/historical references only",
    "location_changed": "S — W5 where_summary location-shift signal; not a narrator strict-off rollback surface",
    "forbidden_ai_stack_actor_situation": "FORBIDDEN — must be zero outside inventory docs/scripts",
    "forbidden_ai_stack_w5_actor_situation": "FORBIDDEN — must be zero outside inventory docs/scripts",
    "w5_actor_situation_term": "D/historical — only inventory/audit artifacts may mention this term",
    "validate_w5_actor_situation_old": "D/historical — old function name; only inventory/audit artifacts may reference it (R1 in 6B-0)",
    "validate_w5_actor_tracking_new": "current — Phase 6B-0 R1 rename target",
    "w5_actor_situation_validation_old": "D/historical — old failure_class string (R2 in 6B-0)",
    "w5_actor_tracking_validation_new": "current — Phase 6B-0 R2 rename target",
    # Phase 6B-6A diagnostics flag retirement surfaces
    "narrator_legacy_compat_diag_flag": "retired_phase_6b6b — env-var name; historical/docs only after ADR-0066.",
    "narrator_legacy_compat_diag_fn": "retired_phase_6b6b — Python function + public export removed by ADR-0066.",
    "narrator_legacy_compat_diag_key": "retired_phase_6b6b — flag-states/admin metadata key removed by ADR-0066.",
    "legacy_compat_transition_write": "retired_phase_6b6b — _legacy_compat insertion branch removed by ADR-0066.",
    "demoted_to_legacy_compat": "retired_phase_6b6b — former w5.legacy_transition_parity diagnostics value; historical/docs only after ADR-0066.",
    "removed_by_6b5e_policy": "removed_by_adr_0068_admin_metadata — former w5.legacy_transition_parity value; historical/docs/tests only.",
    "legacy_transition_parity": "removed_by_adr_0068_admin_metadata — admin metadata key removed; historical/docs/tests only.",
    # Phase 6B-9 surfaces
    "viewer_room_id": "L — deprecated public WS RuntimeSnapshot compat alias; keep during ADR-0069 Phase 6B-11 compatibility window; needs_dedicated_adr_before_removal",
    "w5_player_view": "current — W5 player-shell projection surface; w5_first_already_migrated in Phase 6B-1",
}


# Phase 6B-4 — Fresh post-migration classification taxonomy after F1/F21/F22/
# F8/F18/F19/F20/F11 were migrated. The labels below describe the *reachability
# class* a surface still falls into under the Phase 6B-3A/B/C migration state:
#
#   - still_needed_explicit_opt_out      — branch fires only under W5_AST_*=0/false/no/off
#   - still_needed_malformed_w5_safety   — branch fires only on missing/malformed W5 snapshot
#   - still_needed_old_payload_compat    — branch fires only on legacy sessions without W5 wire-in
#   - still_needed_public_client_compat  — branch fires because WS/frontend payload contract requires it
#   - substrate_keep_future_adr          — substrate writer/reader; consolidation deferred to a later ADR
#   - w5_first_migrated_keep_temporarily — Phase 6B-3A/B/C migrated this; helper/legacy code retained
#                                          as the malformed-W5 / opt-out / old-payload safety net
#   - newly_dead_candidate_for_6b5       — Phase 6B-4 candidate for targeted Phase 6B-5 removal
#                                          (default-on does not execute the branch AND O/M/L are
#                                          covered by a *different* branch AND removal does not
#                                          touch a public payload contract). Phase 6B-4 finds none.
#   - needs_dedicated_adr_before_removal — branch fires under D but is part of a public payload
#                                          contract that requires a separately-scoped ADR + client
#                                          upgrade before removal (e.g., player-shell current_room_id,
#                                          WS viewer_room_id, narrator_consequence area metadata).
#   - test_only_update                   — test fixture / assertion; updates in lockstep with producer
#   - doc_only_update                    — docstring/comment/prompt-text-only legacy reference
#   - unknown_needs_runtime_trace        — coverage cannot be proven statically; needs a live trace
#
# Every label below is informational only. The authoritative per-branch table
# lives in docs/MVPs/w5_legacy_consumer_removal_inventory.md §"Phase 6B-4".
PHASE_6B4_CLASSIFICATION: dict[str, str] = {
    "current_room": (
        "substrate_keep_future_adr + needs_dedicated_adr_before_removal — "
        "substrate read in runtime_world/environment_state AND public "
        "player-shell + WS payload alias; frontend/WS clients still read it"
    ),
    "current_room_id": (
        "substrate_keep_future_adr + needs_dedicated_adr_before_removal — "
        "Participant dataclass substrate field AND public player-shell + WS "
        "payload alias"
    ),
    "current_area": (
        "substrate_keep_future_adr — C5 player_action_resolution / C7 "
        "narrator_consequence_contracts / C8 sensory_context_engine reads "
        "still primary; needs_dedicated_adr_before_removal for the W5-first "
        "movement-framing / stage-area builder"
    ),
    "previous_room_id": (
        "substrate_keep_future_adr — environment_state substrate field only"
    ),
    "actor_locations": (
        "substrate_keep_future_adr — environment_state substrate field; "
        "W5 extractor input; F1 / F4 / F5 / F21 / F22 still call it on O/M/L"
    ),
    "visible_room_ids": (
        "substrate_keep_future_adr — environment_state visibility substrate"
    ),
    "visible_occupants": (
        "substrate_keep_future_adr — RuntimeVisibilityPolicy substrate field"
    ),
    "RuntimeVisibilityPolicy": (
        "substrate_keep_future_adr — engine-level visibility substrate"
    ),
    "complete_actor_locations_for_gathering": (
        "substrate_keep_future_adr + w5_first_migrated_keep_temporarily — "
        "Director baseline completion algorithm called by F1 (opt-out + "
        "malformed-W5 branches) and F4 (W5-success branch over W5-derived "
        "actor_locations); single source of truth for NPC fallback voting + "
        "gathering_scene_id derivation"
    ),
    "gathering_scene_id": (
        "substrate_keep_future_adr — derived inside complete_actor_locations_"
        "for_gathering; consumed by ADR-0061 pause predicate"
    ),
    "derived_gathering_room_id": (
        "substrate_keep_future_adr — Director alias produced by F5"
    ),
    "transition_from_previous": (
        "removed_by_adr_0068 (Phase 6B-8) — strict-off rollback path removed; "
        "transition_from_previous is no longer emitted by the narrator path. "
        "Any remaining hits are doc/test-historical or the location_changed "
        "W5 mirror (which is a separate substrate keep). "
        "W5 where_summary.location_changed is the sole location-shift authority."
    ),
    "location_changed": (
        "substrate_keep_future_adr — W5 where_summary location-shift signal; "
        "admin diagnostics read W5 history and do not consult "
        "transition_from_previous"
    ),
    "forbidden_ai_stack_actor_situation": (
        "FORBIDDEN — must be zero outside inventory docs/scripts/tests"
    ),
    "forbidden_ai_stack_w5_actor_situation": (
        "FORBIDDEN — must be zero outside inventory docs/scripts/tests"
    ),
    "w5_actor_situation_term": (
        "doc_only_update / historical — only inventory/audit artifacts may "
        "mention this term"
    ),
    "validate_w5_actor_situation_old": (
        "doc_only_update / historical — old function name; only inventory/"
        "audit artifacts may reference it (R1 done in 6B-0)"
    ),
    "validate_w5_actor_tracking_new": "current — Phase 6B-0 R1 rename target",
    "w5_actor_situation_validation_old": (
        "doc_only_update / historical — old failure_class string (R2 done "
        "in 6B-0)"
    ),
    "w5_actor_tracking_validation_new": "current — Phase 6B-0 R2 rename target",
    # Phase 6B-6B diagnostics flag retirement surfaces — classified for completeness.
    # Authoritative removal record: ADR-0066.
    "narrator_legacy_compat_diag_flag": (
        "retired_phase_6b6b — runtime_flag_resolver removed by ADR-0066."
    ),
    "narrator_legacy_compat_diag_fn": (
        "retired_phase_6b6b — runtime_flag_resolver + public export removed "
        "by ADR-0066."
    ),
    "narrator_legacy_compat_diag_key": (
        "retired_phase_6b6b — diagnostics_metadata key removed from "
        "w5_projection_flag_states() by ADR-0066."
    ),
    "legacy_compat_transition_write": (
        "retired_phase_6b6b — runtime_branch in "
        "god_of_carnage_narrator_path._block() removed by ADR-0066."
    ),
    "demoted_to_legacy_compat": (
        "retired_phase_6b6b — former admin_view parity label value; "
        "historical/docs only after ADR-0066."
    ),
    "removed_by_6b5e_policy": (
        "removed_by_adr_0068_admin_metadata — former admin_view parity label; "
        "historical/docs/tests only."
    ),
    "legacy_transition_parity": (
        "removed_by_adr_0068_admin_metadata — admin metadata key removed by "
        "ADR-0068; historical/docs/tests only."
    ),
    # Phase 6B-9 surfaces (ADR-0069)
    "viewer_room_id": (
        "still_needed_public_client_compatibility + needs_dedicated_adr_before_removal — "
        "deprecated public WS RuntimeSnapshot field; Phase 6B-11 starts the "
        "client compatibility window while preserving the alias. Removal "
        "requires Phase 6B-12+ ADR + proven client migration (ADR-0069)"
    ),
    "w5_player_view": (
        "w5_first_already_migrated — W5 player-shell projection surface; "
        "wired in Phase 6B-1; current authority for player-facing location (ADR-0069)"
    ),
}


# Phase 6B-4 — closed taxonomy enum. The script lists this so downstream tests
# can cross-check the labels in ``PHASE_6B4_CLASSIFICATION`` against the
# canonical inventory taxonomy. Phase 6B-4 introduces no new failure modes —
# the script remains non-failing. Phase 6B-5 may promote a candidate from
# ``newly_dead_candidate_for_6b5`` into the deletion plan, but only after a
# dedicated ADR records the safety contract.
PHASE_6B4_TAXONOMY: tuple[str, ...] = (
    "still_needed_explicit_opt_out",
    "still_needed_malformed_w5_safety",
    "still_needed_old_payload_compatibility",
    "still_needed_public_client_compatibility",
    "substrate_keep_future_adr",
    "w5_first_migrated_keep_temporarily",
    "newly_dead_candidate_for_6b5",
    "needs_dedicated_adr_before_removal",
    "test_only_update",
    "doc_only_update",
    "unknown_needs_runtime_trace",
    # Phase 6B-8 additions
    "removed_by_adr_0068",
    "retired_phase_6b6b",
    "removed_by_adr_0068_admin_metadata",
    # Phase 6B-9 additions
    "w5_first_already_migrated",
)


EXCLUDED_DIR_NAMES: set[str] = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    ".pytest_cache",
    ".mypy_cache",
    ".idea",
    ".vscode",
}

# Directory path fragments to exclude (matched against POSIX-style path)
EXCLUDED_PATH_FRAGMENTS: tuple[str, ...] = (
    "'fy'-suites/delagecy/",
    "'fy'-suites/docify/",
    "'fy'-suites/observifyfy/",
    "'fy'-suites/despaghettify/",
    "tests/reports/",
    "world-engine/app/story_runtime/manager/_legacy_sources/",
    # Stale git worktrees are auxiliary workspaces, not active source.
    # Their content may reference historical symbols removed in the main tree.
    ".worktrees/",
    ".claude/worktrees/",
    ".state_tmp/",
)

# Filename patterns to exclude
EXCLUDED_FILENAME_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^audit_.*\.json$"),
    re.compile(r"^.*\.log$"),
    re.compile(r"^engine_run_last\.txt$"),
    re.compile(r"^failing-tests\.txt$"),
)

INCLUDED_EXTENSIONS: set[str] = {
    ".py",
    ".md",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".html",
    ".yaml",
    ".yml",
    ".json",
    ".txt",
    ".bak",
}


@dataclass(frozen=True)
class Finding:
    surface: str
    path: str
    line: int
    text: str

    def to_dict(self) -> dict[str, object]:
        return {
            "surface": self.surface,
            "path": self.path,
            "line": self.line,
            "text": self.text[:240],
        }


@dataclass
class ScanReport:
    root: str
    findings: list[Finding] = field(default_factory=list)
    files_scanned: int = 0
    files_skipped: int = 0

    def by_surface(self) -> dict[str, int]:
        counts: dict[str, int] = {key: 0 for key, _ in LEGACY_SURFACES}
        for f in self.findings:
            counts[f.surface] = counts.get(f.surface, 0) + 1
        return counts

    def files_with_findings(self) -> int:
        return len({f.path for f in self.findings})


def _is_excluded_path(path: Path, root: Path) -> bool:
    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        return True
    for fragment in EXCLUDED_PATH_FRAGMENTS:
        if fragment in rel:
            return True
    for pat in EXCLUDED_FILENAME_PATTERNS:
        if pat.match(path.name):
            return True
    return False


def _iter_candidate_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for current_dir, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIR_NAMES]
        for name in files:
            p = Path(current_dir) / name
            if p.suffix.lower() not in INCLUDED_EXTENSIONS:
                continue
            if _is_excluded_path(p, root):
                continue
            out.append(p)
    return out


def scan(root: Path) -> ScanReport:
    report = ScanReport(root=str(root))
    compiled = [(key, re.compile(pattern)) for key, pattern in LEGACY_SURFACES]
    for path in _iter_candidate_files(root):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            report.files_skipped += 1
            continue
        report.files_scanned += 1
        for line_no, line in enumerate(text.splitlines(), start=1):
            for key, regex in compiled:
                if regex.search(line):
                    rel_path = path.relative_to(root).as_posix()
                    report.findings.append(
                        Finding(surface=key, path=rel_path, line=line_no, text=line.strip())
                    )
    return report


def _format_human(report: ScanReport) -> str:
    out: list[str] = []
    out.append("W5 Phase 6A — legacy localization surface scan")
    out.append("=" * 50)
    out.append(f"root: {report.root}")
    out.append(f"files scanned: {report.files_scanned}")
    out.append(f"files skipped: {report.files_skipped}")
    out.append(f"files with findings: {report.files_with_findings()}")
    out.append(f"total findings: {len(report.findings)}")
    out.append("")
    out.append("Count by surface:")
    for key, count in report.by_surface().items():
        out.append(f"  {key:48s} {count:5d}")
    out.append("")
    out.append("Phase 6B-2 classification (informational; authoritative table in")
    out.append("docs/MVPs/w5_legacy_consumer_removal_inventory.md §'Phase 6B-2'):")
    out.append("  S = substrate_keep  O = opt-out fallback  M = malformed-W5 safety")
    out.append("  L = compatibility alias  D = doc/comment only")
    for key, _ in LEGACY_SURFACES:
        label = PHASE_6B2_CLASSIFICATION.get(key, "—")
        out.append(f"  {key:48s} {label}")
    out.append("")
    out.append("Phase 6B-4 classification (informational; authoritative table in")
    out.append("docs/MVPs/w5_legacy_consumer_removal_inventory.md §'Phase 6B-4'):")
    out.append(
        "  closed taxonomy: " + ", ".join(PHASE_6B4_TAXONOMY)
    )
    for key, _ in LEGACY_SURFACES:
        label = PHASE_6B4_CLASSIFICATION.get(key, "—")
        out.append(f"  {key:48s} {label}")
    out.append("")
    out.append(
        "Phase 6B-4 conclusion: no surface is a newly_dead_candidate_for_6b5; every"
    )
    out.append(
        "branch still fires under at least one of D / O / M / L. See the per-branch"
    )
    out.append(
        "matrix in the inventory doc for the full reachability proof."
    )
    out.append("")
    out.append("Phase 6B-6A diagnostics flag retirement surface (informational; authoritative")
    out.append("removal plan in docs/ADR/adr-0066-retire-narrator-legacy-compat-diagnostics-flag.md):")
    _6b6a_keys = (
        "narrator_legacy_compat_diag_flag",
        "narrator_legacy_compat_diag_fn",
        "narrator_legacy_compat_diag_key",
        "legacy_compat_transition_write",
        "demoted_to_legacy_compat",
        "removed_by_6b5e_policy",
        "legacy_transition_parity",
    )
    for key in _6b6a_keys:
        count = sum(1 for f in report.findings if f.surface == key)
        label = PHASE_6B4_CLASSIFICATION.get(key, "—")
        out.append(f"  {key:48s} {count:3d}  {label[:60]}")
    out.append("")
    out.append("Phase 6B-8 — ADR-0068 EXECUTED (operator waiver, 2026-05-28):")
    out.append("  transition_from_previous strict-off rollback path REMOVED.")
    out.append("  w5_ast_narrator_strict_enabled() API REMOVED.")
    out.append("  NarratorStrictOffDeprecationWarning REMOVED; no tombstone retained.")
    out.append("  w5.legacy_transition_parity admin metadata REMOVED.")
    _6b7_keys = ("transition_from_previous", "location_changed")
    for key in _6b7_keys:
        count = sum(1 for f in report.findings if f.surface == key)
        label = PHASE_6B4_CLASSIFICATION.get(key, "—")
        out.append(f"  {key:48s} {count:3d}  {label[:70]}")
    out.append("")
    out.append("ADR-0068 execution checklist (Phase 6B-8, 2026-05-28):")
    tfp_count = sum(1 for f in report.findings if f.surface == "transition_from_previous")
    lc_count = sum(1 for f in report.findings if f.surface == "location_changed")
    out.append(
        "  1. Runtime removal: COMPLETE — _transition_facts() removed, strict-off branch removed."
    )
    out.append(
        "  2. Operator waiver: GRANTED — repo-local config clean; release-cycle waived."
    )
    out.append(
        "  3. Parity tests: COMPLETE — all strict-off test functions rewritten or removed."
    )
    out.append(
        f"  4. Inventory: COMPLETE — transition_from_previous ({tfp_count} refs) reclassified"
        " as removed_by_adr_0068."
    )
    out.append(
        "  5. ADR-0068: ACCEPTED — see docs/ADR/adr-0068-remove-narrator-strict-off-transition-rollback.md."
    )
    out.append("")
    out.append("  OVERALL ADR-0068 STATUS: EXECUTED AND ACCEPTED.")
    out.append("  transition_from_previous remaining hits are doc/test-historical or")
    out.append("  location_changed W5 mirror (separate substrate keep, unrelated to rollback).")
    out.append("")
    forbidden_keys = (
        "forbidden_ai_stack_actor_situation",
        "forbidden_ai_stack_w5_actor_situation",
    )
    allowed_forbidden_reference_paths = {
        "docs/MVPs/w5_legacy_consumer_removal_inventory.md",
        "docs/MVPs/w5_actor_tracking_migration.md",
        "scripts/inventory_w5_legacy_consumers.py",
        "tests/test_inventory_w5_legacy_consumers.py",
    }
    forbidden = [
        f
        for f in report.findings
        if f.surface in forbidden_keys and f.path not in allowed_forbidden_reference_paths
    ]
    if forbidden:
        out.append("WARNING — forbidden package references detected:")
        for f in forbidden:
            out.append(f"  {f.path}:{f.line}: {f.text[:200]}")
    else:
        out.append("OK — no active forbidden package references detected.")
    out.append("")
    out.append("Phase 6B-9/6B-10/6B-11 — ADR-0069 ACCEPTED (2026-05-29):")
    out.append("  viewer_room_id: deprecated public WS RuntimeSnapshot compat alias; kept for the client migration window.")
    out.append("  w5_player_view: current W5 player-shell projection; migrated in Phase 6B-1.")
    out.append("  world-engine/app/web/static/app.js currentRoom(): upgraded to W5-first.")
    out.append("  WS RuntimeSnapshot w5_player_view gap: CLOSED in Phase 6B-10.")
    out.append("  Production WS w5_player_view population: COMPLETE in Phase 6B-11.")
    out.append("  RuntimeSnapshot.viewer_room_id + .current_room: compat alias comments added.")
    _6b9_keys = ("viewer_room_id", "w5_player_view")
    for key in _6b9_keys:
        count = sum(1 for f in report.findings if f.surface == key)
        label = PHASE_6B4_CLASSIFICATION.get(key, "—")
        out.append(f"  {key:48s} {count:3d}  {label[:70]}")
    out.append("")
    out.append("This report is informational; the authoritative inventory and")
    out.append("classification live in docs/MVPs/w5_legacy_consumer_removal_inventory.md.")
    return "\n".join(out)


def _reconfigure_stdout_utf8() -> None:
    """Best-effort: force stdout to UTF-8 so non-ASCII findings can be printed
    on Windows consoles whose default code page is cp1252."""
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


def main(argv: list[str] | None = None) -> int:
    _reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=str(Path(__file__).resolve().parents[1]),
        help="Repository root to scan (default: repository root inferred from this script).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a JSON report instead of a human-readable summary.",
    )
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    report = scan(root)
    if args.json:
        payload = {
            "root": report.root,
            "files_scanned": report.files_scanned,
            "files_skipped": report.files_skipped,
            "files_with_findings": report.files_with_findings(),
            "total_findings": len(report.findings),
            "counts_by_surface": report.by_surface(),
            "findings": [f.to_dict() for f in report.findings],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(_format_human(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
