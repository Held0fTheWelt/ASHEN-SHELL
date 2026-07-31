"""Assemble backend SOURCE-segment modules into real Python (Wave 5)."""
from __future__ import annotations

import argparse
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def extract_source_constant(path: Path) -> str:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if (
                isinstance(target, ast.Name)
                and target.id == "SOURCE"
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                return node.value.value
    raise ValueError(f"{path}: no SOURCE string assignment found")


def assemble(
    *,
    segment_dir: Path,
    ordered_files: tuple[str, ...],
    out_path: Path,
    stamp: str,
) -> None:
    parts = [extract_source_constant(segment_dir / name) for name in ordered_files]
    body = "\n".join(parts)
    if body.startswith("\n"):
        body = body.lstrip("\n")
    marker = "from __future__ import annotations\n"
    if marker in body and stamp not in body:
        body = body.replace(marker, marker + "\n" + stamp + "\n", 1)
    if not body.endswith("\n"):
        body += "\n"
    compile(body, str(out_path), "exec")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(body, encoding="utf-8", newline="\n")
    print(f"wrote {out_path} bytes={out_path.stat().st_size} lines={body.count(chr(10))}")


STUB = '''"""Retired SOURCE segment — logic lives in the assembled impl module (Wave 5)."""
from __future__ import annotations

__all__: list[str] = []
'''


def stub_segments(segment_dir: Path, ordered_files: tuple[str, ...]) -> None:
    for name in ordered_files:
        path = segment_dir / name
        path.write_text(STUB, encoding="utf-8", newline="\n")
        print("stubbed", path.name)


GAME_FILES: tuple[str, ...] = (
    "imports_and_dependencies.py",
    "trace_identity_and_auth_helpers.py",
    "error_response_and_bootstrap_helpers.py",
    "session_slot_and_run_identity_helpers.py",
    "story_window_scene_block_helpers.py",
    "shell_turn_counter_helpers.py",
    "player_shell_state_projection.py",
    "session_loop_bundle_evidence.py",
    "player_session_bundle_visible_output.py",
    "player_session_bundle_response.py",
    "player_session_binding_persistence.py",
    "runtime_profile_handoff_validation.py",
    "runtime_profile_merge_and_compile.py",
    "ensure_player_session_resume.py",
    "ensure_player_session_create.py",
    "template_catalog_helpers.py",
    "bootstrap_template_and_run_list_routes.py",
    "run_creation_route.py",
    "player_session_create_route.py",
    "player_session_resume_and_opening_routes.py",
    "player_turn_trace_start.py",
    "player_turn_execution_and_flush.py",
    "ticket_routes.py",
    "character_routes.py",
    "save_slot_routes.py",
    "content_feed_and_editor_routes.py",
    "content_publication_routes.py",
    "content_governance_review_routes.py",
    "content_governance_publishable_and_ops_routes.py",
)

GOVERNANCE_FILES: tuple[str, ...] = (
    "01_imports_and_defaults.py",
    "02_provider_contracts_openai_ollama.py",
    "03_provider_contracts_remote_and_mock.py",
    "04_provider_secret_and_model_helpers.py",
    "05_provider_probe_http.py",
    "06_provider_probe_adapters.py",
    "07_runtime_rebind_and_audit.py",
    "08_bootstrap_status_and_baseline.py",
    "09_bootstrap_defaults_and_presets.py",
    "10_provider_listing_and_create.py",
    "11_provider_update_and_credentials.py",
    "12_provider_connection_health.py",
    "13_model_listing_and_create.py",
    "14_model_update_delete_rebind.py",
    "15_model_connection_health.py",
    "16_route_listing_and_readiness_helpers.py",
    "17_runtime_readiness_issues.py",
    "18_runtime_readiness_summary.py",
    "19_route_create_update.py",
    "20_runtime_modes.py",
    "21_runtime_route_resolution.py",
    "22_resolved_runtime_serializers.py",
    "23_resolved_runtime_snapshots.py",
    "24_default_provider_seed.py",
    "25_scope_settings.py",
    "26_usage_events_and_budgets.py",
    "27_rollups_audit_and_budget_guard.py",
    "28_operational_activity_and_runtime_secret.py",
    "29_runtime_mode_route_selection.py",
    "30_resolved_route_and_model_rows.py",
    "31_scope_settings_and_snapshot_persistence.py",
    "32_resolved_config_and_default_providers.py",
    "33_default_mock_and_scope_settings.py",
    "34_scope_delete_and_usage_ingest.py",
    "35_budget_policy_and_rollup_rebuild.py",
    "36_rollup_listing_and_budget_guard.py",
    "37_activity_and_provider_credentials.py",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "target",
        choices=("game", "governance", "all"),
        help="Which SOURCE assembly to build",
    )
    parser.add_argument("--stub", action="store_true", help="Replace segment files with stubs")
    args = parser.parse_args(argv)

    if args.target in {"game", "all"}:
        assemble(
            segment_dir=ROOT / "backend" / "app" / "api" / "v1" / "game",
            ordered_files=GAME_FILES,
            out_path=ROOT / "backend" / "app" / "api" / "v1" / "game_routes_impl.py",
            stamp="# Wave 5: assembled from api/v1/game SOURCE via assemble_backend_source_segments.py",
        )
        if args.stub:
            stub_segments(ROOT / "backend" / "app" / "api" / "v1" / "game", GAME_FILES)

    if args.target in {"governance", "all"}:
        assemble(
            segment_dir=ROOT
            / "backend"
            / "app"
            / "services"
            / "governance"
            / "governance_runtime",
            ordered_files=GOVERNANCE_FILES,
            out_path=ROOT
            / "backend"
            / "app"
            / "services"
            / "governance"
            / "governance_runtime_service_impl.py",
            stamp="# Wave 5: assembled from governance_runtime SOURCE via assemble_backend_source_segments.py",
        )
        if args.stub:
            stub_segments(
                ROOT / "backend" / "app" / "services" / "governance" / "governance_runtime",
                GOVERNANCE_FILES,
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
