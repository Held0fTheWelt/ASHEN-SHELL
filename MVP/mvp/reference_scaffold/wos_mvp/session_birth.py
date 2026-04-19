from __future__ import annotations
from dataclasses import dataclass
from typing import Any

REQUIRED_BIRTH_FIELDS = (
    "artifact_id",
    "artifact_revision",
    "publish_state",
    "published_at",
    "module_id",
    "content_contract_version",
    "binding_source",
)

@dataclass(slots=True)
class PublishedArtifactBundle:
    artifact_id: str
    artifact_revision: str
    publish_state: str
    published_at: str
    module_id: str
    content_contract_version: str
    binding_source: str

    def as_dict(self) -> dict[str, str]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_revision": self.artifact_revision,
            "publish_state": self.publish_state,
            "published_at": self.published_at,
            "module_id": self.module_id,
            "content_contract_version": self.content_contract_version,
            "binding_source": self.binding_source,
        }

@dataclass(slots=True)
class StorySessionBirthPlan:
    session_id: str
    start_scene_id: str
    artifact: PublishedArtifactBundle
    turn_zero_required: bool = True


def validate_publish_bound_birth(bundle: dict[str, Any]) -> tuple[bool, list[str]]:
    missing = [field for field in REQUIRED_BIRTH_FIELDS if not bundle.get(field)]
    return (not missing, missing)


def build_story_session_birth_plan(*, session_id: str, start_scene_id: str, artifact: PublishedArtifactBundle) -> StorySessionBirthPlan:
    return StorySessionBirthPlan(session_id=session_id, start_scene_id=start_scene_id, artifact=artifact)
