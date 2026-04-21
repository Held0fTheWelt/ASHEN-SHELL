"""Core application service coordinating artifact birth, persistence, and runtime turns."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .artifacts import PublishedArtifactRegistry
from .incidents import IncidentRecord
from .payloads import make_operator_bundle, make_player_reveal
from .player_surface import make_clean_player_surface
from .runtime_demo import build_demo_engine
from .session_birth import build_story_session_birth_plan
from .storage import SessionStore, StoredSession


class WorldEngineService:
    """Coordinates the one-truth runtime flow for the runnable MVP."""

    def __init__(self, *, store: SessionStore | None = None, artifacts: PublishedArtifactRegistry | None = None):
        self.store = store or SessionStore()
        self.artifacts = artifacts or PublishedArtifactRegistry()

    def create_session(self, module_id: str) -> dict[str, Any]:
        artifact = self.artifacts.load_bundle(module_id)
        plan = build_story_session_birth_plan(
            session_id="pending",
            start_scene_id="turn_0_opening",
            artifact=artifact,
        )
        opening_text = (
            "Rain freckles the windows while the room holds its breath. "
            "A published case file lies open, and every look in the room feels like a test."
        )
        session = self.store.create_session(
            module_id=module_id,
            artifact_id=plan.artifact.artifact_id,
            artifact_revision=plan.artifact.artifact_revision,
            start_scene_id=plan.start_scene_id,
            opening_text=opening_text,
        )
        reveal = make_player_reveal(
            transcript=session.transcript,
            narration=opening_text,
            turn_number=0,
        ).as_dict()
        return {
            "session_id": session.session_id,
            "module_id": session.module_id,
            "artifact": artifact.as_dict(),
            "turn_zero_required": plan.turn_zero_required,
            "player_payload": reveal,
        }

    def get_session_player_view(self, session_id: str) -> dict[str, Any] | None:
        session = self.store.get_session(session_id)
        if session is None:
            return None
        gm_lines = [item["text"] for item in session.transcript if item.get("speaker") == "gm"]
        gm_narration = gm_lines[-1] if gm_lines else ""
        payload = make_clean_player_surface(
            transcript=session.transcript,
            gm_narration=gm_narration,
            turn_number=session.current_turn,
            status=session.status,
        )
        return {
            "session_id": session.session_id,
            "module_id": session.module_id,
            "artifact_id": session.artifact_id,
            "artifact_revision": session.artifact_revision,
            "player_view": payload,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
        }

    def execute_turn(self, session_id: str, player_input: str) -> dict[str, Any] | None:
        session = self.store.get_session(session_id)
        if session is None:
            return None
        engine = build_demo_engine(session_id=session_id, module_id=session.module_id)
        prior_player_lines = [
            item["text"]
            for item in session.transcript
            if item.get("speaker") == "player"
        ]
        for previous in prior_player_lines:
            engine.execute_turn(previous)
        result = engine.execute_turn(player_input)
        updated = self.store.append_turn(
            session_id=session_id,
            player_input=player_input,
            gm_output=result.text_output,
            turn_number=result.turn_number,
            strategy=result.strategy,
            support_action=result.support_action,
            retrieved_memory_ids=result.retrieved_memory_ids,
        )
        player_payload = make_player_reveal(
            transcript=updated.transcript,
            narration=result.text_output,
            turn_number=result.turn_number,
        ).as_dict()
        return {
            "session_id": session_id,
            "turn_result": asdict(result),
            "player_payload": player_payload,
        }

    def get_runtime_state(self, session_id: str) -> dict[str, Any] | None:
        session = self.store.get_session(session_id)
        if session is None:
            return None
        return {
            "session_id": session_id,
            "status": session.status,
            "current_turn": session.current_turn,
            "transcript_length": len(session.transcript),
            "start_scene_id": session.start_scene_id,
            "artifact_binding": {
                "artifact_id": session.artifact_id,
                "artifact_revision": session.artifact_revision,
            },
        }

    def get_diagnostics(self, session_id: str) -> dict[str, Any] | None:
        session = self.store.get_session(session_id)
        if session is None:
            return None
        operator_bundle = make_operator_bundle(
            trace_id=f"diag::{session_id}",
            diagnostics={
                "session_status": session.status,
                "current_turn": session.current_turn,
                "log_count": len(self.store.get_logs(session_id)),
            },
        ).as_dict()
        return {
            "session_id": session_id,
            "operator_bundle": operator_bundle,
            "incident_count": len(self.store.get_incidents(session_id)),
        }

    def get_logs(self, session_id: str, limit: int = 100) -> dict[str, Any] | None:
        session = self.store.get_session(session_id)
        if session is None:
            return None
        return {
            "session_id": session_id,
            "logs": self.store.get_logs(session_id, limit=limit),
        }

    def record_missing_session_incident(self, session_id: str) -> None:
        self.store.record_incident(
            IncidentRecord(
                incident_code="SESSION_NOT_FOUND",
                severity="warning",
                message="Requested session does not exist",
                session_id=session_id,
                details={"session_id": session_id},
            )
        )
