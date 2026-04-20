from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any

class PathClass(str, Enum):
    AUTHORITATIVE_PLAYER = "authoritative_player"
    AUTHORITATIVE_OPERATOR = "authoritative_operator"
    AUTHORITATIVE_ADMIN = "authoritative_admin"
    TRANSITIONAL = "transitional"
    PREVIEW = "preview"
    OPERATOR_ONLY = "operator_only"
    AUDIT_ONLY = "audit_only"
    RESEARCH_ONLY = "research_only"
    FALLBACK_NON_PROD = "fallback_non_prod"

class Audience(str, Enum):
    PLAYER = "player"
    OPERATOR = "operator"
    ADMIN = "admin"
    AUDITOR = "auditor"
    RESEARCH = "research"

class TruthStatus(str, Enum):
    COMMITTED = "committed"
    ADVISORY = "advisory"
    PREVIEW = "preview"
    TRANSITIONAL = "transitional"

class PayloadClass(str, Enum):
    PLAYER_REVEAL = "player_reveal"
    OPERATOR_BUNDLE = "operator_bundle"
    INCIDENT_BUNDLE = "incident_bundle"
    EXPORT = "export"
    SESSION_BIRTH = "session_birth"

@dataclass(slots=True)
class ClassifiedPayload:
    schema_version: str
    path_class: PathClass
    audience: Audience
    truth_status: TruthStatus
    payload_class: PayloadClass | None = None
    generated_at: str | None = None
    data: dict[str, Any] | None = None

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["path_class"] = self.path_class.value
        result["audience"] = self.audience.value
        result["truth_status"] = self.truth_status.value
        if self.payload_class is not None:
            result["payload_class"] = self.payload_class.value
        return result


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_player_reveal(*, transcript: list[dict[str, Any]], narration: str, turn_number: int) -> ClassifiedPayload:
    return ClassifiedPayload(
        schema_version="v21",
        path_class=PathClass.AUTHORITATIVE_PLAYER,
        audience=Audience.PLAYER,
        truth_status=TruthStatus.COMMITTED,
        payload_class=PayloadClass.PLAYER_REVEAL,
        generated_at=utc_now_iso(),
        data={"transcript": transcript, "narration": narration, "turn_number": turn_number},
    )


def make_operator_bundle(*, trace_id: str, diagnostics: dict[str, Any]) -> ClassifiedPayload:
    return ClassifiedPayload(
        schema_version="v21",
        path_class=PathClass.OPERATOR_ONLY,
        audience=Audience.OPERATOR,
        truth_status=TruthStatus.ADVISORY,
        payload_class=PayloadClass.OPERATOR_BUNDLE,
        generated_at=utc_now_iso(),
        data={"trace_id": trace_id, "diagnostics": diagnostics},
    )


def ordinary_player_payload_is_clean(payload: dict[str, Any]) -> bool:
    forbidden = {
        "operator_bundle",
        "backend_interpretation_preview",
        "raw_diagnostics",
        "live_room",
        "copy_operator_json",
    }
    return forbidden.isdisjoint(payload)
