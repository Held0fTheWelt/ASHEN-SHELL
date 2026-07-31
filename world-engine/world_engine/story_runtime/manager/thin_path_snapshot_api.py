"""Thin path snapshot API helpers.

Builds compact path snapshots for diagnostics and lightweight external inspection.
"""
from __future__ import annotations

from ._deps import *

class _ThinPathSnapshotApiMixin:
    @staticmethod
    def _selected_thin_path_row(
        rows: list[Any],
        turn_number: int | None,
    ) -> dict[str, Any] | None:
        if turn_number is not None:
            for row in rows:
                if isinstance(row, dict) and row.get("turn_number") == turn_number:
                    return row
            return None
        if rows:
            last = rows[-1]
            return last if isinstance(last, dict) else None
        return None

    @staticmethod
    def _diagnostic_contract_name(key: str) -> str:
        mapping = {
            "free_player_action_resolution": "free_player_action_resolution.v1",
            "director_gathering_state": "director_gathering_state.v1",
            "canonical_path_hold_effect": "canonical_path_hold_effect.v1",
            "narrator_consequence_realization": "narrator_consequence_realization.v1",
        }
        return mapping.get(key, f"{key}.v1")

    @classmethod
    def _diagnostic_contract_payload(
        cls,
        key: str,
        selected_row: dict[str, Any] | None,
    ) -> dict[str, Any]:
        if selected_row and selected_row.get(key) is not None:
            return {
                "contract_name": cls._diagnostic_contract_name(key),
                "payload": selected_row.get(key),
                "not_yet_wired": False,
            }
        return {
            "contract_name": cls._diagnostic_contract_name(key),
            "payload": None,
            "not_yet_wired": True,
        }

    @staticmethod
    def _empty_diagnostic_section(contract_name: str) -> dict[str, Any]:
        return {
            "contract_name": contract_name,
            "payload": None,
            "not_yet_wired": True,
        }

    @staticmethod
    def _diagnostics_envelope_from_event(event: dict[str, Any]) -> dict[str, Any]:
        diag = event.get("diagnostics") if isinstance(event.get("diagnostics"), dict) else {}
        if not diag and isinstance(event.get("diagnostics_envelope"), dict):
            diag = event["diagnostics_envelope"]
        return diag if isinstance(diag, dict) else {}

    @classmethod
    def _pulse_and_parity_sections(
        cls,
        *,
        diagnostics: list[Any],
        turn_number: int | None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        pulse_section = cls._empty_diagnostic_section("director_pulse_diagnostics.v1")
        bundle_parity = cls._empty_diagnostic_section("bundle_vs_event_stream_parity.v1")
        for event in reversed(diagnostics):
            if not isinstance(event, dict):
                continue
            if turn_number is not None and event.get("turn_number") != turn_number:
                continue
            diag = cls._diagnostics_envelope_from_event(event)
            director_pulse = diag.get("director_pulse")
            if not isinstance(director_pulse, dict):
                director_pulse = (
                    event.get("director_pulse")
                    if isinstance(event.get("director_pulse"), dict)
                    else None
                )
            if isinstance(director_pulse, dict):
                pulse_section = {
                    "contract_name": "director_pulse_diagnostics.v1",
                    "payload": director_pulse,
                    "not_yet_wired": False,
                }
            parity = diag.get("bundle_vs_event_stream_parity")
            if not isinstance(parity, dict):
                parity = director_pulse.get("parity") if isinstance(director_pulse, dict) else None
            if isinstance(parity, dict):
                bundle_parity = {
                    "contract_name": "bundle_vs_event_stream_parity.v1",
                    "payload": parity,
                    "not_yet_wired": False,
                }
            if pulse_section.get("payload") is not None or bundle_parity.get("payload") is not None:
                break
        return pulse_section, bundle_parity

    @staticmethod
    def _selected_capability_names(selected_row: dict[str, Any] | None) -> list[str]:
        if not selected_row:
            return []
        capabilities = selected_row.get("selected_capabilities") or []
        if not isinstance(capabilities, list):
            return []
        return [str(capability) for capability in capabilities if str(capability).strip()]

    def get_thin_path_summary(self, session_id: str, limit: int = 20) -> dict[str, Any]:
        """Slim per-turn Resolver -> Director -> Narrator evidence for the
        narrative_systems UI. Reads ``observability_path_summary`` off each
        recent diagnostics event so the operator can see, per turn:

        - the realization_plan (owner, capabilities, outcome)
        - the capability that was actually invoked
        - kanon_break decision
        - whether a visible block was produced

        Pulls only what the thin-path PR-A surfaces. LDSS-specific fields are
        deliberately excluded; they remain in the full diagnostics endpoint.
        """
        session = self.get_session(session_id)
        events = session.diagnostics[-max(1, int(limit)):]
        rows: list[dict[str, Any]] = []
        for event in events:
            if not isinstance(event, dict):
                continue
            ps = (
                event.get("observability_path_summary")
                if isinstance(event.get("observability_path_summary"), dict)
                else None
            ) or {}
            raw_input = str(event.get("raw_input") or "").strip()
            block_count = 0
            bundle = event.get("visible_output_bundle") if isinstance(event.get("visible_output_bundle"), dict) else None
            if isinstance(bundle, dict):
                blocks = bundle.get("scene_blocks") or []
                if isinstance(blocks, list):
                    block_count = sum(1 for b in blocks if isinstance(b, dict))
            rows.append(
                {
                    "turn_number": event.get("turn_number"),
                    "turn_kind": event.get("turn_kind"),
                    "turn_status": event.get("turn_status"),
                    "raw_player_input_preview": raw_input[:120],
                    "realization_plan": ps.get("realization_plan"),
                    "realize_via_capabilities_used_capability": ps.get(
                        "realize_via_capabilities_used_capability"
                    ),
                    "realize_via_capabilities_outcome": ps.get("realize_via_capabilities_outcome"),
                    "selected_capabilities": ps.get("selected_capabilities") or [],
                    "kanon_break": ps.get("kanon_break"),
                    "kanon_break_reason": ps.get("kanon_break_reason"),
                    # PR-B: live effect propagation projection per turn.
                    "free_player_action_resolution": ps.get("free_player_action_resolution"),
                    "canonical_path_hold_effect": ps.get("canonical_path_hold_effect"),
                    "narrator_consequence_realization": ps.get(
                        "narrator_consequence_realization"
                    ),
                    "director_gathering_state": ps.get("director_gathering_state"),
                    "gathering_paused_beat_suppression": ps.get(
                        "gathering_paused_beat_suppression"
                    ),
                    "director_pause_transition_reaction": ps.get(
                        "director_pause_transition_reaction"
                    ),
                    "visible_block_emitted": bool(ps.get("visible_block_emitted")),
                    "director_path_mode": ps.get("director_path_mode"),
                    "visible_scene_block_count": block_count,
                    "nodes_executed": ps.get("nodes_executed") or [],
                    "structured_output_keys": ps.get("structured_output_keys") or [],
                    "usage_details": ps.get("usage_details"),
                    "validation_status": ps.get("validation_status"),
                }
            )
        return {
            "schema_version": "thin_path_summary.v1",
            "session_id": session.session_id,
            "turn_counter": session.turn_counter,
            "rows": rows,
        }

    def get_runtime_diagnostic_snapshot(
        self,
        session_id: str,
        *,
        turn_number: int | None = None,
        thin_path_limit: int = 20,
    ) -> dict[str, Any]:
        """Read-only aggregator for ``runtime_diagnostic_snapshot.v1``.

        Composes existing operator surfaces (thin-path rows, diagnostics events,
        pulse diagnostics) without running the graph or importing the PR-0 stub
        module into production execution paths.
        """
        session = self.get_session(session_id)
        thin = self.get_thin_path_summary(session_id, limit=thin_path_limit)
        rows = thin.get("rows") if isinstance(thin.get("rows"), list) else []
        selected_row = self._selected_thin_path_row(rows, turn_number)
        pulse_section, bundle_parity = self._pulse_and_parity_sections(
            diagnostics=session.diagnostics,
            turn_number=turn_number,
        )

        return {
            "schema_version": "runtime_diagnostic_snapshot.v1",
            "session_id": session.session_id,
            "turn_number": (
                turn_number
                if turn_number is not None
                else (selected_row.get("turn_number") if selected_row else None)
            ),
            "canonical_step_id": getattr(session, "canonical_step_id", None),
            "visible_block_emitted": (
                selected_row.get("visible_block_emitted") if selected_row else None
            ),
            "resolver_output": self._diagnostic_contract_payload(
                "free_player_action_resolution",
                selected_row,
            ),
            "director_gathering_state": self._diagnostic_contract_payload(
                "director_gathering_state",
                selected_row,
            ),
            "canonical_path_hold_effect": self._diagnostic_contract_payload(
                "canonical_path_hold_effect",
                selected_row,
            ),
            "narrator_consequence_realization": self._diagnostic_contract_payload(
                "narrator_consequence_realization",
                selected_row,
            ),
            "pulse": pulse_section,
            "bundle_vs_event_stream_parity": bundle_parity,
            "semantic_capability_consultation_names": self._selected_capability_names(
                selected_row
            ),
            "thin_path_summary": {
                "schema_version": thin.get("schema_version"),
                "row_count": len(rows),
                "selected_turn": (
                    selected_row.get("turn_number") if selected_row else None
                ),
            },
            "aggregation_sources": [
                "thin_path_summary.v1",
                "session.diagnostics[].diagnostics.director_pulse",
                "session.diagnostics[].diagnostics.bundle_vs_event_stream_parity",
            ],
        }


__all__ = ["_ThinPathSnapshotApiMixin"]
