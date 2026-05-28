"""Runtime voice consistency validation derived from character voice profiles."""

from __future__ import annotations

import re
from typing import Any

from ai_stack.contracts.character_voice_contract import (
    CharacterVoiceProfileRecord,
    VoiceConsistencyValidationResult,
    VoiceDriftFinding,
    VoiceValidationMode,
)
from ai_stack.story_runtime.npc_agency.character.character_voice_semantic_classifier import (
    SEMANTIC_CLASSIFICATION_POLICY_SOURCE,
    classify_voice_semantic_lines,
    semantic_policy_enabled,
)
from ai_stack.story_runtime.god_of_carnage.god_of_carnage_frozen_vocabulary import canonicalize_goc_actor_id, expand_goc_actor_id_aliases


def _norm(text: str) -> str:
    lowered = str(text or "").casefold()
    lowered = re.sub(r"[^\w\s]+", " ", lowered, flags=re.UNICODE)
    lowered = re.sub(r"\s+", " ", lowered).strip()
    return lowered


def _line_text(row: Any) -> str:
    if isinstance(row, dict):
        return str(row.get("text") or row.get("line") or row.get("content") or "").strip()
    return str(row or "").strip()


def _speaker_id(row: Any) -> str:
    if isinstance(row, dict):
        return str(row.get("speaker_id") or row.get("actor_id") or row.get("responder_id") or "").strip()
    return ""


def _profile_aliases(profile: CharacterVoiceProfileRecord) -> set[str]:
    aliases = set(expand_goc_actor_id_aliases(profile.runtime_actor_id))
    aliases.update(expand_goc_actor_id_aliases(profile.character_key))
    aliases.add(profile.runtime_actor_id)
    aliases.add(profile.character_key)
    canon = canonicalize_goc_actor_id(profile.runtime_actor_id)
    if canon:
        aliases.add(canon)
    return {str(alias).strip() for alias in aliases if str(alias).strip()}


def _profile_for_speaker(
    speaker_id: str,
    profiles: list[CharacterVoiceProfileRecord],
) -> CharacterVoiceProfileRecord | None:
    sid = str(speaker_id or "").strip()
    if not sid:
        return None
    canon = canonicalize_goc_actor_id(sid) or sid
    for profile in profiles:
        aliases = _profile_aliases(profile)
        if sid in aliases or canon in aliases:
            return profile
    return None


def _marker_hit(norm_text: str, marker: str) -> bool:
    norm_marker = _norm(marker)
    if not norm_marker:
        return False
    return bool(re.search(rf"(?<!\w){re.escape(norm_marker)}(?!\w)", norm_text))


def _detect_forbidden_language_markers(
    *,
    text: str,
    speaker_profile: CharacterVoiceProfileRecord,
    speaker_id: str,
) -> list[VoiceDriftFinding]:
    norm_text = _norm(text)
    marker_root = speaker_profile.forbidden_language_markers
    if not marker_root:
        return []
    matched_categories: list[str] = []
    matched_count = 0
    for category, markers in marker_root.items():
        if not isinstance(markers, list):
            continue
        category_hit = False
        for marker in markers:
            if _marker_hit(norm_text, str(marker)):
                matched_count += 1
                category_hit = True
        if category_hit:
            matched_categories.append(str(category))
    if not matched_categories:
        return []
    return [
        VoiceDriftFinding(
            drift_class="forbidden_language_marker",
            severity="failure",
            speaker_id=speaker_id,
            character_key=speaker_profile.character_key,
            policy_source="character_voice.voice_consistency.forbidden_language_markers",
            expected_profile_actor_id=speaker_profile.runtime_actor_id,
            evidence={
                "marker_count": matched_count,
                "marker_categories": matched_categories,
            },
        )
    ]


def _voice_validation_mode(validation_mode: str | None) -> VoiceValidationMode:
    """Normalize caller-supplied validation mode to the contract vocabulary."""
    mode = str(validation_mode or "schema_plus_semantic").strip().lower()
    if mode not in {"schema_only", "schema_plus_semantic", "strict_rule_engine"}:
        mode = "schema_plus_semantic"
    return mode  # type: ignore[return-value]


def _voice_profiles_from_raw(
    voice_profiles: list[dict[str, Any] | CharacterVoiceProfileRecord],
) -> list[CharacterVoiceProfileRecord]:
    """Parse usable voice profile records and ignore malformed rows."""
    profiles: list[CharacterVoiceProfileRecord] = []
    for raw_profile in voice_profiles:
        try:
            profiles.append(CharacterVoiceProfileRecord.model_validate(raw_profile))
        except Exception:
            continue
    return profiles


def _spoken_voice_rows(structured_output: dict[str, Any] | None) -> list[Any]:
    """Return spoken rows that contain text."""
    structured = structured_output if isinstance(structured_output, dict) else {}
    spoken = structured.get("spoken_lines") if isinstance(structured.get("spoken_lines"), list) else []
    return [row for row in spoken if _line_text(row)]


def _empty_voice_result(
    *,
    reason: str,
    mode: VoiceValidationMode,
    profiles_checked: int,
) -> VoiceConsistencyValidationResult:
    """Return an early voice validation result for no-op cases."""
    return VoiceConsistencyValidationResult(
        status="not_applicable" if reason == "no_spoken_lines" else "approved",
        reason=reason,
        validation_mode=mode,
        profiles_checked=profiles_checked,
        spoken_line_count=0,
        policy_sources=["character_voice_contract"] if reason != "no_spoken_lines" else [],
    )


def _schema_only_voice_result(
    *,
    mode: VoiceValidationMode,
    profiles_checked: int,
    spoken_line_count: int,
) -> VoiceConsistencyValidationResult:
    """Return the approved schema-only validation result."""
    return VoiceConsistencyValidationResult(
        status="approved",
        reason="schema_only_voice_validation_skipped",
        validation_mode=mode,
        profiles_checked=profiles_checked,
        spoken_line_count=spoken_line_count,
        policy_sources=["character_voice_contract"],
    )


def _profile_marker_findings(
    *,
    rows: list[Any],
    profiles: list[CharacterVoiceProfileRecord],
    strict: bool,
) -> list[VoiceDriftFinding]:
    """Validate direct profile availability and forbidden-language markers."""
    findings: list[VoiceDriftFinding] = []
    for row in rows:
        speaker = _speaker_id(row)
        text = _line_text(row)
        profile = _profile_for_speaker(speaker, profiles)
        if profile is None:
            findings.append(
                VoiceDriftFinding(
                    drift_class="missing_voice_profile",
                    severity="failure" if strict else "warning",
                    speaker_id=speaker,
                    policy_source="character_voice.characters",
                    evidence={"line_present": bool(text)},
                )
            )
            continue
        findings.extend(
            _detect_forbidden_language_markers(
                text=text,
                speaker_profile=profile,
                speaker_id=speaker,
            )
        )
    return findings


def _semantic_voice_findings(
    *,
    rows: list[Any],
    profiles: list[CharacterVoiceProfileRecord],
    typed_mode: VoiceValidationMode,
    strict: bool,
) -> tuple[list[VoiceDriftFinding], list[Any]]:
    """Run semantic voice classification and translate drifts to findings."""
    findings: list[VoiceDriftFinding] = []
    classifications = classify_voice_semantic_lines(
        spoken_rows=rows,
        profiles=profiles,
        validation_mode=typed_mode,
    )
    for classification in classifications:
        for finding_code in classification.finding_codes:
            severity = (
                "failure"
                if strict and finding_code in {"cross_actor_voice_confusion", "mixed_voice_signature"}
                else "warning"
            )
            evidence = dict(classification.evidence)
            evidence.update(
                {
                    "classifier_version": classification.classifier_version,
                    "expected_profile_alignment": classification.expected_profile_alignment,
                    "best_profile_alignment": classification.best_profile_alignment,
                    "cross_actor_confusion_margin": classification.cross_actor_confusion_margin,
                    "confidence": classification.confidence,
                    "dimension_scores": classification.dimension_scores,
                    "best_dimension_scores": classification.best_dimension_scores,
                }
            )
            findings.append(
                VoiceDriftFinding(
                    drift_class=finding_code,
                    severity=severity,
                    speaker_id=classification.speaker_id,
                    policy_source=SEMANTIC_CLASSIFICATION_POLICY_SOURCE,
                    expected_profile_actor_id=classification.expected_profile_actor_id,
                    actual_source_actor_id=classification.best_matching_actor_id
                    if finding_code == "cross_actor_voice_confusion"
                    else None,
                    evidence=evidence,
                )
            )
    return findings, classifications


def _voice_policy_sources(profiles: list[CharacterVoiceProfileRecord]) -> list[str]:
    """List policy sources that participated in the validation."""
    policy_sources = [
        "character_voice.characters",
        "character_voice.voice_consistency",
    ]
    if any(profile.forbidden_language_markers for profile in profiles):
        policy_sources.append("character_voice.voice_consistency.forbidden_language_markers")
    if semantic_policy_enabled(profiles):
        policy_sources.append(SEMANTIC_CLASSIFICATION_POLICY_SOURCE)
    return policy_sources


def validate_voice_consistency(
    *,
    structured_output: dict[str, Any] | None,
    voice_profiles: list[dict[str, Any] | CharacterVoiceProfileRecord],
    validation_mode: str | None = None,
) -> VoiceConsistencyValidationResult:
    """Validate structured actor speech against content-derived voice records."""

    typed_mode = _voice_validation_mode(validation_mode)
    mode = str(typed_mode)
    profiles = _voice_profiles_from_raw(voice_profiles)
    rows = _spoken_voice_rows(structured_output)

    if not rows:
        return _empty_voice_result(
            reason="no_spoken_lines",
            profiles_checked=len(profiles),
            mode=typed_mode,
        )

    if mode == "schema_only":
        return _schema_only_voice_result(
            mode=typed_mode,
            profiles_checked=len(profiles),
            spoken_line_count=len(rows),
        )

    strict = mode == "strict_rule_engine"
    findings = _profile_marker_findings(
        rows=rows,
        profiles=profiles,
        strict=strict,
    )
    semantic_findings, semantic_classifications = _semantic_voice_findings(
        rows=rows,
        profiles=profiles,
        typed_mode=typed_mode,
        strict=strict,
    )
    findings.extend(semantic_findings)
    policy_sources = _voice_policy_sources(profiles)

    blocking = [finding for finding in findings if finding.severity == "failure"]
    return VoiceConsistencyValidationResult(
        status="rejected" if blocking else "approved",
        reason="voice_consistency_drift" if blocking else "voice_consistency_pass",
        validation_mode=typed_mode,
        profiles_checked=len(profiles),
        spoken_line_count=len(rows),
        findings=findings,
        blocking_findings=blocking,
        semantic_classifications=semantic_classifications,
        policy_sources=policy_sources,
    )
