# Implementation Report: W2.1.3 Parse, Normalize, and Pre-Validate AI Output

**Version**: 0.3.3
**Date**: 2026-03-27
**Status**: ✅ COMPLETE — Parse/normalize/pre-validate pipeline established

---

## Executive Summary

W2.1.3 bridges raw adapter output into a clean, inspectable internal decision representation. Raw adapter responses are parsed into the typed `StructuredAIStoryOutput`, normalized into the canonical `ParsedAIDecision`, and pre-validated for obvious errors—all with diagnostic trace preservation.

**Problem**: `AdapterResponse.structured_payload` is a loose `dict[str, Any]`. Without a defined transformation pipeline, runtime validation would need to handle parsing failures, inconsistent field names, and type mismatches across many places.

**Solution**: A single focused module `ai_decision.py` containing:
- `ParsedAIDecision` — canonical internal decision representation
- `ParseResult` — inspectable pipeline outcome
- `parse_adapter_response()` — full parse/normalize/pre-validate pipeline
- `prevalidate_decision()` — catch obvious errors before runtime validation

**Result**: All adapter output is now transformed into a stable, inspectable form before entering the runtime validator. Diagnostics remain visible for debugging.

**Tests**: 26 new focused tests, all passing.
**Total Runtime Tests**: 226 (200 existing + 26 new).

---

## Problem Statement

After W2.1.2 established the `StructuredAIStoryOutput` contract, the next step is to parse raw adapter responses into this typed form and normalize them into an internal decision representation. Without this bridge:

1. **Parsing is implicit**: How to convert `dict[str, Any]` → `StructuredAIStoryOutput`? Error handling?
2. **No canonical form**: Is the internal representation the structured output, or something else?
3. **Errors are fragmented**: Parsing errors, type errors, and validation errors happen in different places
4. **Diagnostics are lost**: Raw output is not preserved for debugging
5. **Pre-validation is unclear**: What's caught early vs. deferred to runtime?

**Better approach**: Define explicit parse → normalize → pre-validate stages with clear responsibilities.

---

## Solution: Parse/Normalize/Pre-Validate Pipeline

### Three Core Models

#### 1. `ParsedAIDecision` — Canonical Internal Decision Representation

**Location**: `backend/app/runtime/ai_decision.py:29-63`

```python
class ParsedAIDecision(BaseModel):
    """Canonical internal decision after parsing + normalization.

    This is the authoritative form that the runtime consumes.
    Raw output and parse source are preserved for diagnostics.
    """

    # Required, normalized from StructuredAIStoryOutput
    scene_interpretation: str
    detected_triggers: list[str]
    proposed_deltas: list[ProposedDelta]
    proposed_scene_id: str | None
    rationale: str

    # Optional, normalized from StructuredAIStoryOutput
    dialogue_impulses: list[DialogueImpulse] = []
    conflict_vector: ConflictVector | None = None
    confidence: float | None = None

    # Diagnostic trace
    raw_output: str            # Always preserved from AdapterResponse
    parsed_source: str         # Always "structured_payload"
```

**Design**:
- Maps 1:1 from `StructuredAIStoryOutput` with field name normalizations (proposed_state_deltas → proposed_deltas)
- Includes diagnostic fields: raw_output and parsed_source for post-facto analysis
- All fields immutable (Pydantic BaseModel)
- Ready for downstream runtime validation

#### 2. `ParseResult` — Inspectable Pipeline Outcome

**Location**: `backend/app/runtime/ai_decision.py:65-79`

```python
class ParseResult(BaseModel):
    """Result of parse_adapter_response() — inspectable outcome.

    Attributes:
        success: True if parse+normalize+prevalidate all passed
        decision: ParsedAIDecision if successful, None otherwise
        errors: List of errors encountered (empty if successful)
        raw_output: Original adapter output (always preserved)
    """

    success: bool
    decision: ParsedAIDecision | None = None
    errors: list[str] = []
    raw_output: str
```

**Design**:
- Single result object for entire pipeline
- success flag = `len(errors) == 0`
- Collects all errors from all stages (parse + normalize + pre-validate)
- raw_output always preserved, even on failure

### Five Core Functions

#### 1. `parse_adapter_response(response: AdapterResponse) → ParseResult`

**Location**: `backend/app/runtime/ai_decision.py:81-152`

```python
def parse_adapter_response(response: AdapterResponse) -> ParseResult:
    """Parse raw or structured adapter output into ParseResult.

    Performs:
    1. Check adapter error status
    2. Check structured_payload is present and is dict
    3. Parse dict → StructuredAIStoryOutput (Pydantic validation)
    4. Normalize to ParsedAIDecision
    5. Pre-validate for obvious issues
    6. Return ParseResult with success flag, decision, errors, raw output
    """
```

**Pipeline steps**:
1. **Check adapter error**: If `response.is_error`, fail immediately with error message
2. **Check payload exists**: If `structured_payload is None`, fail with clear error
3. **Check payload is dict**: If not dict, fail with type error
4. **Parse to StructuredAIStoryOutput**: Pydantic validates all required/optional fields
   - Collects all Pydantic ValidationError field errors
   - Returns failure with error list if validation fails
5. **Normalize**: Call `normalize_structured_output(structured, raw_output)`
6. **Pre-validate**: Call `prevalidate_decision(decision)`
7. **Return**: ParseResult with success=(len(errors)==0), decision, errors, raw_output

**Error handling**: All errors aggregated into `errors` list; single success flag indicates validity.

#### 2. `normalize_structured_output(structured: StructuredAIStoryOutput, raw_output: str) → ParsedAIDecision`

**Location**: `backend/app/runtime/ai_decision.py:155-184`

```python
def normalize_structured_output(
    structured: StructuredAIStoryOutput,
    raw_output: str,
) -> ParsedAIDecision:
    """Normalize StructuredAIStoryOutput into ParsedAIDecision.

    Applies:
    - Whitespace stripping from text fields
    - None → [] for empty list fields
    - Field copying and repackaging
    """
```

**Normalization steps**:
1. Strip leading/trailing whitespace from `scene_interpretation`
2. Strip leading/trailing whitespace from `rationale`
3. Convert `proposed_state_deltas` to `proposed_deltas` (field rename)
4. Preserve `dialogue_impulses` (already [] if None in pydantic)
5. Preserve `conflict_vector` (None if not provided)
6. Preserve `confidence` (None if not provided)
7. Set `raw_output` to original adapter response
8. Set `parsed_source` = "structured_payload"

**Design**: Pure transformation; no validation. All inputs valid by construction (already validated by Pydantic).

#### 3. `prevalidate_decision(decision: ParsedAIDecision) → list[str]`

**Location**: `backend/app/runtime/ai_decision.py:187-228`

```python
def prevalidate_decision(decision: ParsedAIDecision) -> list[str]:
    """Pre-validate ParsedAIDecision for obvious errors.

    Catches:
    - Empty/blank required text fields
    - Malformed proposed deltas
    - Duplicate trigger IDs

    This is NOT the full runtime validation (module-aware). It's a first-pass
    filter for obviously broken output before hitting the main validator.
    """
```

**Validation checks**:
1. `scene_interpretation` not empty and not whitespace-only
2. `rationale` not empty and not whitespace-only
3. Each `proposed_delta` has non-empty `target_path`
4. Each `proposed_delta` has non-None `next_value`
5. No duplicate trigger IDs in `detected_triggers`

**Design**: Pre-validation only. Does NOT check:
- Whether trigger IDs exist in module.trigger_definitions
- Whether proposed_scene_id exists in module.scene_phases
- Whether target_paths are valid for this module
- Whether proposed delta values are valid for their fields
- Immutability rule violations

**Returns**: List of error strings (empty = valid).

#### 4. `process_adapter_response(response: AdapterResponse) → ParseResult`

**Location**: `backend/app/runtime/ai_decision.py:231-242`

```python
def process_adapter_response(response: AdapterResponse) -> ParseResult:
    """Convenience function: full pipeline parse → normalize → pre-validate.

    Equivalent to calling parse_adapter_response() directly.
    """
```

**Design**: Thin wrapper for API consistency. Direct call to `parse_adapter_response()`.

---

## Pipeline Flow

```
AdapterResponse (raw_output, structured_payload, error, is_error)
        ↓
[parse_adapter_response()]
        ↓
    ┌─────────────────────────────────────┐
    │ 1. Check adapter error              │
    └─────────────────────────────────────┘
        ↓
    ┌─────────────────────────────────────┐
    │ 2. Check structured_payload exists  │
    └─────────────────────────────────────┘
        ↓
    ┌─────────────────────────────────────┐
    │ 3. Check is dict                    │
    └─────────────────────────────────────┘
        ↓
    ┌─────────────────────────────────────┐
    │ 4. Parse → StructuredAIStoryOutput  │
    │    (Pydantic validation)            │
    └─────────────────────────────────────┘
        ↓
[normalize_structured_output()]
        ↓
    ┌─────────────────────────────────────┐
    │ 5. Normalize to ParsedAIDecision    │
    │    - Strip whitespace               │
    │    - Rename fields                  │
    │    - Preserve diagnostics           │
    └─────────────────────────────────────┘
        ↓
[prevalidate_decision()]
        ↓
    ┌─────────────────────────────────────┐
    │ 6. Pre-validate obvious errors      │
    │    - Blank fields                   │
    │    - Malformed deltas               │
    │    - Duplicate triggers             │
    └─────────────────────────────────────┘
        ↓
ParseResult (success, decision, errors, raw_output)
```

---

## Test Coverage

### Test Organization (26 tests total)

#### TestParseAdapterResponse (10 tests)

| Test | Purpose | Validates |
|------|---------|-----------|
| `test_parse_valid_structured_payload_succeeds` | Basic success path | Parsing and normalization work end-to-end |
| `test_parse_returns_parsed_decision_on_success` | Return type | ParseResult.decision is ParsedAIDecision with correct fields |
| `test_parse_adapter_error_fails_immediately` | Error handling | is_error flag triggers immediate failure |
| `test_parse_none_structured_payload_fails` | Payload validation | None payload rejected with clear error |
| `test_parse_non_dict_structured_payload_fails` | Type validation | Non-dict payload rejected at AdapterResponse construction |
| `test_parse_missing_required_field_scene_interpretation` | Field validation | Pydantic catches missing required field |
| `test_parse_missing_required_field_rationale` | Field validation | Pydantic catches missing required field |
| `test_parse_wrong_field_type_detected_triggers_not_list` | Type validation | Pydantic rejects wrong field type |
| `test_parse_raw_output_preserved_on_success` | Diagnostics | raw_output preserved in success case |
| `test_parse_raw_output_preserved_on_failure` | Diagnostics | raw_output preserved in failure case |

**Results**: 10/10 PASSED

#### TestNormalizeStructuredOutput (6 tests)

| Test | Purpose | Validates |
|------|---------|-----------|
| `test_normalize_strips_whitespace_from_scene_interpretation` | Normalization | Whitespace stripped from scene_interpretation |
| `test_normalize_strips_whitespace_from_rationale` | Normalization | Whitespace stripped from rationale |
| `test_normalize_dialogue_impulses_preserved_when_empty` | List handling | Empty dialogue_impulses preserved |
| `test_normalize_proposed_scene_id_none_passes_through` | Optional field | None values preserved |
| `test_normalize_conflict_vector_none_passes_through` | Optional field | None values preserved |
| `test_normalize_parsed_source_set_to_structured_payload` | Source tracking | parsed_source set correctly and raw_output preserved |

**Results**: 6/6 PASSED

#### TestPrevalidateDecision (6 tests)

| Test | Purpose | Validates |
|------|---------|-----------|
| `test_prevalidate_empty_scene_interpretation_returns_error` | Empty field detection | Empty scene_interpretation caught |
| `test_prevalidate_whitespace_only_scene_interpretation_returns_error` | Whitespace detection | Whitespace-only scene_interpretation caught |
| `test_prevalidate_empty_rationale_returns_error` | Empty field detection | Empty rationale caught |
| `test_prevalidate_empty_target_path_in_delta_returns_error` | Delta validation | Empty target_path in delta caught |
| `test_prevalidate_duplicate_trigger_ids_returns_error` | Duplicate detection | Duplicate trigger IDs caught |
| `test_prevalidate_valid_decision_returns_empty_errors` | Positive case | Valid decision returns empty error list |

**Results**: 6/6 PASSED

#### TestProcessAdapterResponse (4 tests)

| Test | Purpose | Validates |
|------|---------|-----------|
| `test_process_full_pipeline_success` | End-to-end success | Full pipeline completes successfully |
| `test_process_full_pipeline_failure_missing_fields` | End-to-end failure | Pipeline fails on missing fields |
| `test_process_full_pipeline_failure_adapter_error` | Error handling | Pipeline fails on adapter error |
| `test_process_raw_output_always_preserved` | Invariant | raw_output preserved in all cases |

**Results**: 4/4 PASSED

---

## Files Changed

| File | Change | Lines |
|------|--------|-------|
| `backend/app/runtime/ai_decision.py` | Created | 267 |
| `backend/tests/runtime/test_ai_decision.py` | Created | 453 |
| `CHANGELOG.md` | Updated | +72 |

**Total**: 3 files, 792 lines added

---

## What Pre-Validation Catches

✅ **Adapter error flags**
- response.is_error = True or response.error is not None

✅ **Missing structured_payload**
- response.structured_payload is None

✅ **Invalid payload type** (caught by AdapterResponse)
- structured_payload is not a dict

✅ **Missing required fields** (caught by Pydantic)
- scene_interpretation, detected_triggers, proposed_state_deltas, rationale all required

✅ **Wrong field types** (caught by Pydantic)
- detected_triggers must be list[str]
- proposed_state_deltas must be list[ProposedDelta]
- confidence (if provided) must be float

✅ **Empty required text fields**
- scene_interpretation empty or whitespace-only
- rationale empty or whitespace-only

✅ **Malformed proposed deltas**
- target_path empty or missing
- next_value is None

✅ **Duplicate trigger IDs**
- detected_triggers contains same ID twice

---

## What is Deferred to Runtime Validation (W2.1.4+)

🔄 **Module-aware validation**
- Whether trigger IDs exist in module.trigger_definitions
- Whether proposed_scene_id exists in module.scene_phases
- Whether target_paths are valid for this module

🔄 **Value validation**
- Whether proposed delta values are valid for their target fields
- Type coercion or range validation specific to field definitions

🔄 **Immutability rules**
- Whether field can be modified (e.g., is it marked immutable?)

🔄 **Complex guard logic**
- Domain-specific validation rules
- Cross-field dependencies
- Narrative constraints

**Rationale**: These require module context and field definitions that are available in the full runtime validator. Pre-validation is intentionally limited to catch obvious, universal errors.

---

## Design Decisions

| Decision | Rationale | Consequence |
|----------|-----------|--------------|
| Separate ParsedAIDecision from StructuredAIStoryOutput | Internal vs. external boundary | Two models, clear separation |
| Preserve raw_output always | Debugging and diagnostics | Extra field but valuable for transparency |
| PreValidation only, not full validation | Pre-validation runs before module context | Explicit boundary between stages |
| Whitespace stripping during normalization | Clean up common LLM formatting quirks | Simpler downstream processing |
| Errors as list in ParseResult | Single result object for entire pipeline | Easy to consume; all errors in one place |
| process_adapter_response() as wrapper | API consistency | Thin convenience function |

---

## Verification

```bash
PYTHONPATH=backend python -m pytest backend/tests/runtime/test_ai_decision.py -v
# Result: 26 PASSED

PYTHONPATH=backend python -m pytest backend/tests/runtime/ -v
# Result: 226 PASSED (200 existing + 26 new)
```

All tests passing. Coverage includes:
- Valid and invalid adapter responses
- Pydantic validation error handling
- Normalization correctness
- Pre-validation rules
- End-to-end pipeline

---

## Acceptance Criteria Met

✅ Raw adapter output can now be parsed into StructuredAIStoryOutput
✅ Parsed output can be normalized into ParsedAIDecision
✅ Pre-validation catches malformed, partial, or obviously invalid output
✅ Result is suitable for integration into turn execution flow
✅ Diagnostics remain inspectable (raw_output, parsed_source)
✅ No W2 scope jump occurred
✅ Implementation is generic and provider-agnostic
✅ 26 new focused tests (all passing)
✅ 226 total runtime tests passing
✅ CHANGELOG updated

---

## Next Steps: W2.1.4

W2.1.4 will integrate the parsing pipeline into the turn execution loop:

1. **Turn Executor Integration**: Connect parse_adapter_response() to execute_turn()
   - Call adapter.generate(request)
   - Call parse_adapter_response(response)
   - Feed ParsedAIDecision into runtime validator

2. **Full Runtime Validation**: Implement module-aware validation
   - Validate trigger IDs against module.trigger_definitions
   - Validate scene IDs against module.scene_phases
   - Validate target_paths against module state schema
   - Validate proposed delta values

3. **Guard System**: Integrate decision guard checks
   - Review decisions with low confidence
   - Apply domain-specific validation rules
   - Handle fallback cases

4. **Integration Tests**: End-to-end turn execution with real AI
   - Full turn loop with Claude adapter
   - Complex narrative paths with decisions
   - Error recovery and fallback

---

**Commit**: `feat(w2): parse and normalize structured AI output`
**Status**: ✅ COMPLETE

The parse/normalize/pre-validate pipeline is now in place. All adapter output flows through a defined, testable transformation before entering the runtime validator. Diagnostics remain visible throughout.

Ready for W2.1.4: Integration into turn execution!
