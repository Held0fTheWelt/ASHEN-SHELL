"""MVP2 Object Admission — source-kind-gated environment object validation.

Objects may only enter the runtime from three classified sources:
  canonical_content   — explicitly present in the canonical content module
  typical_minor_implied — minor plausible contextual object (staged temporarily, not committed)
  similar_allowed     — similar to a known canonical object (requires similarity_reason)

Any object without a valid source_kind is rejected. Major, dangerous, or plot-changing
objects without canonical backing are always rejected.

Error codes:
  object_source_kind_required         — object_id present but source_kind missing or invalid
  environment_object_not_admitted     — object not admitted (missing source, major/dangerous)
  similar_allowed_requires_similarity_reason — source_kind=similar_allowed but no similarity_reason
  runtime_module_contains_story_truth — object request would create new canonical story truth
"""

from __future__ import annotations

from typing import Any

from app.runtime.models import VALID_SOURCE_KINDS, ObjectAdmissionRecord


# Objects that are inherently major, dangerous, or plot-changing and cannot be
# admitted without explicit canonical content backing.
_BLOCKED_DANGEROUS_OBJECTS: frozenset[str] = frozenset({
    "gun", "pistol", "revolver", "loaded_revolver", "loaded_gun",
    "rifle", "shotgun", "firearm",
    "knife", "blade", "sword",
    "bomb", "explosive", "grenade",
    "poison", "drug", "narcotic",
    "contract", "will", "deed",      # plot-changing documents
    "weapon", "weapons",
})


def _is_dangerous_or_major(object_id: str) -> bool:
    """Return True if the object ID matches a known dangerous or major object."""
    normalized = object_id.lower().replace("-", "_").replace(" ", "_")
    return normalized in _BLOCKED_DANGEROUS_OBJECTS


def admit_object(request: dict[str, Any]) -> ObjectAdmissionRecord:
    """Evaluate an object admission request and return a fully resolved ObjectAdmissionRecord.

    The record status is "admitted" or "rejected". Rejected records carry an error_code.

    Args:
        request: dict with keys: object_id, source_kind, source_reference,
                 admission_reason, similarity_reason. All optional except object_id.

    Returns:
        ObjectAdmissionRecord with status, error_code, and admission settings populated.
    """
    object_id = str(request.get("object_id") or "").strip()
    if not object_id:
        return ObjectAdmissionRecord(
            object_id="(unknown)",
            status="rejected",
            error_code="object_source_kind_required",
            message="object_id is required.",
        )

    source_kind = str(request.get("source_kind") or "").strip() or None
    source_reference = str(request.get("source_reference") or "").strip() or None
    admission_reason = str(request.get("admission_reason") or "").strip() or None
    similarity_reason = str(request.get("similarity_reason") or "").strip() or None

    # 1. source_kind must be present
    if source_kind is None:
        return ObjectAdmissionRecord(
            object_id=object_id,
            source_kind=None,
            status="rejected",
            error_code="object_source_kind_required",
            message=(
                f"Object {object_id!r} has no source_kind. "
                f"Must be one of: {sorted(VALID_SOURCE_KINDS)!r}."
            ),
        )

    # 2. source_kind must be one of the valid kinds
    if source_kind not in VALID_SOURCE_KINDS:
        return ObjectAdmissionRecord(
            object_id=object_id,
            source_kind=source_kind,
            status="rejected",
            error_code="object_source_kind_required",
            message=(
                f"Object {object_id!r} has invalid source_kind={source_kind!r}. "
                f"Must be one of: {sorted(VALID_SOURCE_KINDS)!r}."
            ),
        )

    # 3. similar_allowed requires similarity_reason
    if source_kind == "similar_allowed" and not similarity_reason:
        return ObjectAdmissionRecord(
            object_id=object_id,
            source_kind=source_kind,
            source_reference=source_reference,
            status="rejected",
            error_code="similar_allowed_requires_similarity_reason",
            message=(
                f"Object {object_id!r} with source_kind=similar_allowed requires "
                f"a non-empty similarity_reason."
            ),
        )

    # 4. Dangerous/major objects without canonical backing are rejected
    if source_kind != "canonical_content" and _is_dangerous_or_major(object_id):
        return ObjectAdmissionRecord(
            object_id=object_id,
            source_kind=source_kind,
            status="rejected",
            error_code="environment_object_not_admitted",
            message=(
                f"Object {object_id!r} is major, dangerous, or plot-changing and "
                f"cannot be admitted without canonical content backing."
            ),
        )

    # 5. Build admitted record per source_kind rules
    if source_kind == "canonical_content":
        return ObjectAdmissionRecord(
            object_id=object_id,
            source_kind=source_kind,
            source_reference=source_reference,
            admission_reason=admission_reason,
            temporary_scene_staging=False,
            commit_allowed=True,
            status="admitted",
        )

    if source_kind == "typical_minor_implied":
        return ObjectAdmissionRecord(
            object_id=object_id,
            source_kind=source_kind,
            source_reference=source_reference,
            admission_reason=admission_reason,
            temporary_scene_staging=True,
            commit_allowed=False,
            status="admitted",
        )

    # similar_allowed (similarity_reason already validated above)
    return ObjectAdmissionRecord(
        object_id=object_id,
        source_kind=source_kind,
        source_reference=source_reference,
        admission_reason=admission_reason,
        similarity_reason=similarity_reason,
        temporary_scene_staging=False,
        commit_allowed=False,
        status="admitted",
    )


def validate_object_admission(record: ObjectAdmissionRecord) -> bool:
    """Return True if the record is admitted and internally consistent."""
    if record.status != "admitted":
        return False
    if record.source_kind not in VALID_SOURCE_KINDS:
        return False
    if record.source_kind == "similar_allowed" and not record.similarity_reason:
        return False
    return True
