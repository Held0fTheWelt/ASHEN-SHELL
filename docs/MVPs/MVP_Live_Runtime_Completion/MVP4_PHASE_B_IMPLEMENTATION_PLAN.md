# MVP4 Phase B Implementation Plan

**Status**: Target State (Infrastructure exists, Costs still Scaffold)  
**Related**: adr-0032 (5 Core Runtime Contracts), MVP4_PHASE_A_IMPLEMENTATION_PLAN.md, MVP4_TEST_GATE_PLAN.md  
**Waves Covered**: Wave 2 (Real Cost Attribution), Wave 3 (Span Token Tracking), Wave 4 (Trace Quality Standards)

---

## Contract Requirements (adr-0032)

**Phase B extends Phase A** to satisfy Core Contracts with **real token cost data in Langfuse spans**. Phase A foundations (DiagnosticsEnvelope, degradation_timeline, to_response()) are prerequisites. **Langfuse SDK v4 span hierarchy already exists; Phase B fills in real token counts.**

1. **Contract 1 (Backend → World-Engine Handoff)** — Backend metadata preserved ✅ Phase A
   - Phase B: Trace correlation proves handoff (trace_id propagates Backend→WE via X-WoS-Trace-Id header)

2. **Contract 2 (Opening Truthfulness)** — Opening marked accurately ✅ Phase A, **correlated** Phase B
   - Phase B: Langfuse spans show opening execution timeline with real timing evidence
   - Test gate: `world-engine/tests/test_mvp4_contract_opening_truthfulness.py` (validate span timing)

3. **Contract 3 (Frontend Playability)** — `can_execute` matches state ✅ Phase A
   - Phase B: No change (satisfied by Phase A)

4. **Contract 4 (Diagnostics Truthfulness)** — All diagnostics **with real token costs** ✅ **Phase B Primary**
   - Phase B implementation: `cost_summary` filled with real `input_tokens`, `output_tokens`, `cost_usd` from span metadata
   - Hierarchical cost aggregation: per-span token counts sum to session cost
   - Test gate: `world-engine/tests/test_mvp4_contract_diagnostics.py` (validate real cost values, not zeros)

5. **Contract 5 (Narrative Streaming)** — SSE routed with trace correlation ✅ **Phase B Infrastructure Ready**
   - Phase B: Trace ID propagates to response envelope, ready for Phase C SSE implementation
   - Test gate: `backend/tests/test_mvp4_contract_streaming.py` (validate trace_id in response)

**Before implementing Phase B, Phase A tests must pass** (`python tests/run_tests.py --mvp4`).

---

## Current State vs Target State

**What already exists (Don't rebuild):**
- ✅ `backend/app/observability/langfuse_adapter.py` — LangfuseAdapter v4 SDK with `start_observation()`, `start_trace()`, `create_child_span()`, ContextVar span passing
- ✅ `world-engine/app/api/http.py` — Root span `world-engine.turn.execute` created, linked to Backend trace via `X-WoS-Trace-Id` header
- ✅ `world-engine/app/story_runtime/manager.py` — Child spans for `story.phase.ldss` and `story.phase.narrator` phases
- ✅ `ai_stack/narrative_runtime_agent.py` — Narrator block spans created for each block
- ✅ `ai_stack/diagnostics_envelope.py` — Phase A: DiagnosticsEnvelope with degradation_timeline, cost_summary, to_response()
- ✅ ContextVar infrastructure: `_active_span_context` for thread-safe span passing via `adapter.get_active_span()` / `set_active_span()`

**What still needs filling (Scaffold → Real):**
- ❌ **Narrator spans have `input_tokens: 0, output_tokens: 0, model: "mock"`** — Must populate with real LLM token counts
- ❌ **LDSS decision spans missing real token attribution** — Must extract from LLM call responses
- ❌ **cost_summary in diagnostics is zeros** — Must aggregate real token counts from all spans
- ❌ **Token cost calculation** — Need pricing models per provider/model

---

## Kritische Dateien — Was zu füllen ist

| Datei | Status | Aktion |
|---|---|---|
| `world-engine/app/api/http.py` | ✅ Hat root span | Verified: creates `world-engine.turn.execute` span (HTTP handler) |
| `world-engine/app/story_runtime/manager.py` | ✅ Hat phase spans | Verified: creates `story.phase.ldss`, `story.phase.narrator` spans |
| `ai_stack/narrative_runtime_agent.py` | ❌ Scaffold tokens | **FILL:** Replace `input_tokens: 0, output_tokens: 0, model: "mock"` with real LLM token counts |
| `ai_stack/live_dramatic_scene_simulator.py` | ⚠️ Needs spans | **ADD:** LDSS decision spans with real token attribution |
| `ai_stack/diagnostics_envelope.py` | ✅ Has structure | Verified: cost_summary field exists, to_response() implemented |
| `backend/app/observability/langfuse_adapter.py` | ✅ Has methods | Verified: `start_observation()`, `create_child_span()`, token tracking ready |
| `tests/gates/test_goc_mvp04_observability_diagnostics_gate.py` | ❌ Needs updates | **EXTEND:** Add tests that verify real token counts, not zeros |

---

## Implementierungsreihenfolge

### Schritt 1: Narrative Token Attribution
**Datei**: `ai_stack/narrative_runtime_agent.py` (~line 224)

**Current (Scaffold):**
```python
span.end(
    output={...},
    metadata={
        "input_tokens": 0,  # ← WRONG: scaffold
        "output_tokens": 0,
        "model": "mock",
    }
)
```

**Target (Real tokens from LLM response):**
```python
# Extract from LLM call response
llm_response = call_llm_for_narration(...)
input_tokens = llm_response.get("usage", {}).get("prompt_tokens", 0)
output_tokens = llm_response.get("usage", {}).get("completion_tokens", 0)
model = llm_response.get("model", "")  # e.g., "gpt-4-turbo"

# Calculate cost using pricing
cost_usd = _calculate_cost(model, input_tokens, output_tokens)

span.end(
    output={"narration": narration},
    metadata={
        "input_tokens": input_tokens,      # ← REAL tokens
        "output_tokens": output_tokens,
        "model": model,
        "cost_usd": cost_usd,
        "latency_ms": elapsed_ms,
    }
)
```

**Cost Calculation Helper** (add to langfuse_adapter.py):
```python
def calculate_token_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost based on model pricing."""
    pricing = {
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    }
    rates = pricing.get(model, pricing.get("gpt-3.5-turbo"))
    input_cost = (input_tokens / 1000.0) * rates["input"]
    output_cost = (output_tokens / 1000.0) * rates["output"]
    return round(input_cost + output_cost, 6)
```

---

### Schritt 2: LDSS Decision Span Token Attribution  
**Datei**: `ai_stack/live_dramatic_scene_simulator.py`

**Current state:** LDSS decisions may not track tokens.

**Target:** Create `ldss.decision` spans with real token counts.

```python
# In decision-making function
parent_span = adapter.get_active_span()
if parent_span:
    decision_span = adapter.create_child_span(
        name="ldss.decision",
        input={...decision context...},
        metadata={"decision_index": index}
    )
else:
    decision_span = None

try:
    # Call LLM for decision
    llm_response = call_llm_for_decision(...)
    
    input_tokens = llm_response.get("usage", {}).get("prompt_tokens", 0)
    output_tokens = llm_response.get("usage", {}).get("completion_tokens", 0)
    model = llm_response.get("model", "")
    cost = calculate_token_cost(model, input_tokens, output_tokens)
    
    decision = parse_decision(llm_response)
    
    if decision_span:
        decision_span.end(
            output={"decision": decision},
            metadata={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "model": model,
                "cost_usd": cost,
            }
        )
    
    return decision

finally:
    if decision_span:
        decision_span.update(output={"error": True}) if error else None
```

---

### Schritt 3: Cost Summary Aggregation
**Datei**: `world-engine/app/story_runtime/manager.py` (in turn finalization)

**Current state:** `cost_summary` is all zeros.

**Target:** Aggregate real token counts from all spans into cost_summary.

```python
# In _finalize_committed_turn() or after turn execution:
adapter = LangfuseAdapter.get_instance()

# Collect token counts from all active spans
total_input_tokens = 0
total_output_tokens = 0
total_cost = 0.0
cost_breakdown = {}

# Gather from LDSS phase
ldss_tokens = span_metadata.get("ldss", {})
total_input_tokens += ldss_tokens.get("input_tokens", 0)
total_output_tokens += ldss_tokens.get("output_tokens", 0)
cost_breakdown["ldss"] = ldss_tokens.get("cost_usd", 0.0)
total_cost += cost_breakdown["ldss"]

# Gather from Narrator phase
narrator_tokens = span_metadata.get("narrator", {})
total_input_tokens += narrator_tokens.get("input_tokens", 0)
total_output_tokens += narrator_tokens.get("output_tokens", 0)
cost_breakdown["narrator"] = narrator_tokens.get("cost_usd", 0.0)
total_cost += cost_breakdown["narrator"]

# Build envelope with real costs
diag_envelope = build_diagnostics_envelope(
    ...,
    cost_summary={
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "cost_usd": round(total_cost, 6),
        "cost_breakdown": cost_breakdown,
    }
)
```

---

### Schritt 4: Tests aktualisieren
**Datei**: `tests/gates/test_goc_mvp04_observability_diagnostics_gate.py`

**Add new tests (don't replace old ones):**

```python
@pytest.mark.mvp4
@pytest.mark.contract
def test_mvp4_narrative_spans_have_real_token_counts():
    """Narrator spans populate input_tokens, output_tokens (not zeros)."""
    response = execute_turn_with_langfuse_enabled()
    
    spans = _fetch_spans(response["trace_id"])
    narrator_spans = [s for s in spans if "narrator.narrate_block" in s["name"]]
    
    assert len(narrator_spans) > 0, "Expected narrator spans"
    for span in narrator_spans:
        meta = span["metadata"]
        assert meta.get("input_tokens", 0) > 0, f"Narrator span {span['name']} has zero input_tokens"
        assert meta.get("output_tokens", 0) > 0, f"Narrator span {span['name']} has zero output_tokens"
        assert meta.get("model") != "mock", "Model should be real (not 'mock')"
        assert meta.get("cost_usd", 0) > 0, "Cost should be calculated"

@pytest.mark.mvp4
@pytest.mark.contract
def test_mvp4_cost_summary_aggregates_real_values():
    """cost_summary in diagnostics is not all zeros."""
    response = execute_turn_with_langfuse_enabled()
    
    cost_summary = response["diagnostics_envelope"]["cost_summary"]
    assert cost_summary["input_tokens"] > 0, "cost_summary.input_tokens should be real, not 0"
    assert cost_summary["output_tokens"] > 0, "cost_summary.output_tokens should be real, not 0"
    assert cost_summary["cost_usd"] > 0.0, "cost_summary.cost_usd should be calculated, not 0.0"
    assert "cost_breakdown" in cost_summary, "cost_breakdown should show per-component costs"

@pytest.mark.mvp4
@pytest.mark.contract
def test_mvp4_langfuse_response_context_shows_costs():
    """to_response('langfuse') exposes real costs (not redacted)."""
    envelope = build_test_envelope_with_real_costs()
    langfuse_response = envelope.to_response(context="langfuse")
    
    assert langfuse_response["cost_summary"] != "[REDACTED]", "Langfuse should see costs"
    assert langfuse_response["cost_summary"]["cost_usd"] > 0.0
```

---

### Schritt 5: Manager Span Metadata Collection
**Datei**: `world-engine/app/story_runtime/manager.py`

**Collect span metadata during phase execution** so Step 3 aggregation can use it:

```python
# During LDSS phase
ldss_span = adapter.get_active_span()
...execute LDSS...
ldss_metadata = ldss_span.metadata if ldss_span else {}

# During Narrator phase
narrator_span = adapter.get_active_span()
...execute Narrator...
narrator_metadata = narrator_span.metadata if narrator_span else {}

# Later in finalization
span_metadata = {
    "ldss": ldss_metadata,
    "narrator": narrator_metadata,
}
# Pass to cost aggregation in Step 3
```

---

## Story Manager Child Spans + Cost Tracking
**Datei**: `world-engine/app/story_runtime/manager.py`

In `_execute_story_phases()` oder `_finalize_committed_turn()`:

```python
from backend.app.observability.langfuse_adapter import get_current_span, create_child_span

# Phase spans (profile → lanes → LDSS → narrator → affordance → state delta → commit)
class StoryPhaseSpans:
    def __init__(self, root_span):
        self.root_span = root_span
        self.spans = {}
    
    def start_phase(self, phase_name: str):
        if self.root_span:
            span = create_child_span(
                parent_span=self.root_span,
                name=f"story.phase.{phase_name}",
                metadata={"phase": phase_name},
            )
            self.spans[phase_name] = span
            return span
        return None
    
    def end_phase(self, phase_name: str, metadata: dict):
        span = self.spans.get(phase_name)
        if span:
            span.end(metadata=metadata)

# In _execute_story_phases():
phase_spans = StoryPhaseSpans(get_current_span())

# Profile phase
span = phase_spans.start_phase("profile")
profile_result = execute_profile_phase(graph_state)
phase_spans.end_phase("profile", {
    "profile_tokens": profile_result.get("tokens_used", 0),
    "profile_cost": profile_result.get("cost", 0.0),
})

# Lanes phase
span = phase_spans.start_phase("lanes")
lanes_result = execute_lanes_phase(graph_state)
phase_spans.end_phase("lanes", {
    "lanes_tokens": lanes_result.get("tokens_used", 0),
    "lanes_cost": lanes_result.get("cost", 0.0),
})

# LDSS phase (separate span)
span = phase_spans.start_phase("ldss")
ldss_result = execute_ldss_phase(graph_state)
phase_spans.end_phase("ldss", {
    "ldss_tokens": ldss_result.get("tokens_used", 0),
    "ldss_cost": ldss_result.get("cost", 0.0),
})

# ... continue for narrator, affordance, state_delta, commit phases

# Aggregiere Costs für cost_summary
total_tokens_input = sum(phase["tokens_input"] for phase in [profile_result, lanes_result, ldss_result, ...])
total_tokens_output = sum(phase["tokens_output"] for phase in [profile_result, lanes_result, ldss_result, ...])
total_cost = sum(phase["cost"] for phase in [profile_result, lanes_result, ldss_result, ...])

# Überweise an DiagnosticsEnvelope
degradation_events = collect_degradation_events(graph_state)
cost_summary = {
    "input_tokens": total_tokens_input,
    "output_tokens": total_tokens_output,
    "cost_usd": total_cost,
    "cost_breakdown": {
        "profile": profile_result.get("cost", 0.0),
        "lanes": lanes_result.get("cost", 0.0),
        "ldss": ldss_result.get("cost", 0.0),
        "narrator": narrator_result.get("cost", 0.0),
        "affordance": affordance_result.get("cost", 0.0),
        "state_delta": state_delta_result.get("cost", 0.0),
        "commit": commit_result.get("cost", 0.0),
    }
}

diag_envelope = build_diagnostics_envelope(
    ...existing args...,
    degradation_events=degradation_events,
    cost_summary=cost_summary,
)
```

---

### Schritt 3: LDSS Decision Spans + Token Tracking
**Datei**: `ai_stack/live_dramatic_scene_simulator.py`

In `simulate_scene()` oder `make_decision()`:

```python
from backend.app.observability.langfuse_adapter import get_current_span, create_child_span

def make_decision(decision_context: dict) -> dict:
    """Make LDSS decision with Langfuse span tracking."""
    
    parent_span = get_current_span()
    if parent_span:
        span = create_child_span(
            parent_span=parent_span,
            name="ldss.decision",
            input={
                "context": decision_context.get("context", ""),
                "available_actions": len(decision_context.get("actions", [])),
            },
            metadata={
                "decision_type": decision_context.get("type", "unknown"),
                "turn_number": decision_context.get("turn_number", 0),
            },
        )
    else:
        span = None
    
    try:
        # Call LLM for decision
        llm_response = call_llm_for_decision(decision_context)
        
        # Track tokens
        input_tokens = llm_response.get("usage", {}).get("prompt_tokens", 0)
        output_tokens = llm_response.get("usage", {}).get("completion_tokens", 0)
        model = llm_response.get("model", "unknown")
        
        # Calculate cost (using model's pricing)
        cost = calculate_token_cost(model, input_tokens, output_tokens)
        
        decision = parse_decision(llm_response)
        
        # Log to span
        if span:
            span.end(
                output={
                    "decision": decision,
                    "confidence": decision.get("confidence", 0.0),
                },
                metadata={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "model": model,
                    "cost_usd": cost,
                    "latency_ms": llm_response.get("latency_ms", 0),
                }
            )
        
        return {
            "decision": decision,
            "tokens_input": input_tokens,
            "tokens_output": output_tokens,
            "cost": cost,
            "model": model,
        }
        
    except Exception as e:
        if span:
            span.end(
                output={"error": str(e)},
                metadata={"error": True}
            )
        raise

def simulate_scene(scene_input: dict) -> dict:
    """Simulate scene with LDSS logic and cost tracking."""
    
    parent_span = get_current_span()
    if parent_span:
        span = create_child_span(
            parent_span=parent_span,
            name="ldss.simulate_scene",
            input={
                "scene_id": scene_input.get("scene_id"),
                "scene_type": scene_input.get("scene_type"),
            },
            metadata={
                "scene_id": scene_input.get("scene_id"),
            },
        )
    else:
        span = None
    
    try:
        total_tokens_input = 0
        total_tokens_output = 0
        total_cost = 0.0
        decisions = []
        
        # Make multiple decisions (each tracked)
        for i, decision_context in enumerate(extract_decision_contexts(scene_input)):
            decision_result = make_decision(decision_context)
            decisions.append(decision_result["decision"])
            total_tokens_input += decision_result["tokens_input"]
            total_tokens_output += decision_result["tokens_output"]
            total_cost += decision_result["cost"]
        
        # Build scene response
        scene_output = {
            "scene_text": compose_scene_text(decisions),
            "decisions": decisions,
        }
        
        if span:
            span.end(
                output={
                    "scene_text": scene_output["scene_text"][:200],  # truncate
                    "decision_count": len(decisions),
                },
                metadata={
                    "input_tokens": total_tokens_input,
                    "output_tokens": total_tokens_output,
                    "cost_usd": total_cost,
                    "decision_count": len(decisions),
                }
            )
        
        return {
            "scene_output": scene_output,
            "tokens_input": total_tokens_input,
            "tokens_output": total_tokens_output,
            "cost": total_cost,
        }
        
    except Exception as e:
        if span:
            span.end(output={"error": str(e)}, metadata={"error": True})
        raise
```

---

### Schritt 4: Narrator Block Spans + Token Tracking
**Datei**: `ai_stack/narrative_runtime_agent.py`

In `narrate_block()` oder `execute_narrative()`:

```python
from backend.app.observability.langfuse_adapter import get_current_span, create_child_span

def narrate_block(block_context: dict) -> dict:
    """Narrate a narrative block with Langfuse span tracking."""
    
    parent_span = get_current_span()
    if parent_span:
        span = create_child_span(
            parent_span=parent_span,
            name="narrator.narrate_block",
            input={
                "block_type": block_context.get("type"),
                "block_id": block_context.get("id"),
            },
            metadata={
                "block_type": block_context.get("type"),
                "block_id": block_context.get("id"),
            },
        )
    else:
        span = None
    
    try:
        # Call LLM for narration
        llm_response = call_llm_for_narration(block_context)
        
        # Track tokens
        input_tokens = llm_response.get("usage", {}).get("prompt_tokens", 0)
        output_tokens = llm_response.get("usage", {}).get("completion_tokens", 0)
        model = llm_response.get("model", "unknown")
        cost = calculate_token_cost(model, input_tokens, output_tokens)
        
        narration = llm_response.get("text", "")
        
        # Log to span
        if span:
            span.end(
                output={
                    "narration": narration[:200],  # truncate for logging
                    "narration_length": len(narration),
                },
                metadata={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "model": model,
                    "cost_usd": cost,
                    "latency_ms": llm_response.get("latency_ms", 0),
                    "narration_length": len(narration),
                }
            )
        
        return {
            "narration": narration,
            "tokens_input": input_tokens,
            "tokens_output": output_tokens,
            "cost": cost,
            "model": model,
        }
        
    except Exception as e:
        if span:
            span.end(output={"error": str(e)}, metadata={"error": True})
        raise
```

---

### Schritt 5: OTEL Filtering Configuration
**Datei**: `backend/app/observability/langfuse_adapter.py` (oder neue `otel_config.py`)

```python
# Multi-Select Configuration für Span Filtering
class OTELSpanFilter:
    """Control which spans are collected."""
    
    FILTER_TYPES = {
        "HTTP": "http_client, http_server",
        "DATABASE": "db_client, db_server",
        "FRAMEWORK": "asgi, fastapi",
        "LLM": "llm_calls",
        "CUSTOM": "custom_spans",
    }
    
    def __init__(self, enabled_filters: set[str] | None = None):
        # Default: All spans enabled
        self.enabled_filters = enabled_filters or set(self.FILTER_TYPES.keys())
    
    def should_collect_span(self, span_type: str) -> bool:
        """Check if span type should be collected."""
        # Map span type to filter category
        if span_type in ["http_client", "http_server"]:
            return "HTTP" in self.enabled_filters
        elif span_type in ["db_client", "db_server"]:
            return "DATABASE" in self.enabled_filters
        # ... etc
        return True  # Default: collect all

# API to enable/disable filters per-session
def set_session_span_filters(session_id: str, enabled_filters: set[str]):
    """Admin can configure span filters per-investigation."""
    # Store in session config
    session_config = get_session_config(session_id)
    session_config["span_filters"] = enabled_filters
    save_session_config(session_id, session_config)

def get_session_span_filters(session_id: str) -> set[str]:
    """Get active filters for session (default: all enabled)."""
    session_config = get_session_config(session_id)
    return session_config.get("span_filters", set(OTELSpanFilter.FILTER_TYPES.keys()))
```

---

### Schritt 6: Tests erweitern
**Datei**: `tests/gates/test_goc_mvp04_observability_diagnostics_gate.py`

```python
@pytest.mark.mvp4
def test_mvp04_root_span_created_with_environment_tags():
    """HTTP handler creates root span with LANGFUSE_ENVIRONMENT tags."""
    with enable_langfuse_for_test():
        response = execute_turn(session_id="test_session", turn_number=1)
        
        spans = fetch_spans_from_langfuse(trace_id=response["trace_id"])
        root_span = spans[0]
        
        assert root_span["name"] == "story.turn.execute"
        assert root_span["tags"] != None
        assert "story-execution" in root_span["tags"]

@pytest.mark.mvp4
def test_mvp04_child_spans_hierarchy():
    """Story manager creates child spans with proper hierarchy."""
    with enable_langfuse_for_test():
        response = execute_turn(session_id="test_session", turn_number=1)
        
        spans = fetch_spans_from_langfuse(trace_id=response["trace_id"])
        
        # Check for expected phases
        phase_names = [s["name"] for s in spans]
        assert "story.phase.profile" in phase_names
        assert "story.phase.ldss" in phase_names
        assert "story.phase.narrator" in phase_names

@pytest.mark.mvp4
def test_mvp04_ldss_decision_spans_with_token_tracking():
    """LDSS creates decision spans with input/output token counts."""
    with enable_langfuse_for_test():
        response = execute_turn(session_id="test_session", turn_number=1)
        
        spans = fetch_spans_from_langfuse(trace_id=response["trace_id"])
        decision_spans = [s for s in spans if "ldss.decision" in s["name"]]
        
        assert len(decision_spans) > 0
        for span in decision_spans:
            metadata = span.get("metadata", {})
            assert "input_tokens" in metadata
            assert "output_tokens" in metadata
            assert "cost_usd" in metadata

@pytest.mark.mvp4
def test_mvp04_cost_summary_in_diagnostics_envelope():
    """DiagnosticsEnvelope.cost_summary has real token/cost values in Phase B."""
    with enable_langfuse_for_test():
        response = execute_turn(session_id="test_session", turn_number=1)
        
        envelope = response["diagnostics_envelope"]
        cost_summary = envelope["cost_summary"]
        
        # Phase B should have real values (not zeros)
        assert cost_summary["input_tokens"] > 0
        assert cost_summary["output_tokens"] > 0
        assert cost_summary["cost_usd"] > 0.0
        assert "cost_breakdown" in cost_summary

@pytest.mark.mvp4
def test_mvp04_langfuse_context_shows_real_costs():
    """to_response('langfuse') shows real costs for RCA."""
    with enable_langfuse_for_test():
        envelope = build_test_envelope_with_real_costs()
        langfuse_response = envelope.to_response(context="langfuse")
        
        # Langfuse should see costs (not redacted)
        assert langfuse_response["cost_summary"] != "[REDACTED]"
        assert langfuse_response["cost_summary"]["cost_usd"] > 0.0

@pytest.mark.mvp4
def test_mvp04_operator_context_redacts_costs():
    """to_response('operator') redacts costs (security)."""
    envelope = build_test_envelope_with_real_costs()
    operator_response = envelope.to_response(context="operator")
    
    # Operator should not see costs
    assert operator_response["cost_summary"] == "[REDACTED]"

@pytest.mark.mvp4
def test_mvp04_span_filtering_all_by_default():
    """OTEL collector gathers all span types by default."""
    with enable_langfuse_for_test():
        response = execute_turn(session_id="test_session", turn_number=1)
        
        spans = fetch_spans_from_langfuse(trace_id=response["trace_id"])
        span_types = set(s.get("type", "custom") for s in spans)
        
        # Should include HTTP, DB, Framework, LLM, custom
        assert len(span_types) >= 3  # At least profile, ldss, narrator phases

@pytest.mark.mvp4
def test_mvp04_narrator_spans_with_narration_length():
    """Narrator spans include narration_length in metadata."""
    with enable_langfuse_for_test():
        response = execute_turn(session_id="test_session", turn_number=1)
        
        spans = fetch_spans_from_langfuse(trace_id=response["trace_id"])
        narrator_spans = [s for s in spans if "narrator" in s["name"]]
        
        assert len(narrator_spans) > 0
        for span in narrator_spans:
            metadata = span.get("metadata", {})
            assert "narration_length" in metadata
```

---

---

## Dependencies

```
Phase A: DiagnosticsEnvelope + Degradation Timeline ✅ DONE
    ↓
Phase B Step 1: Narrative Token Attribution (Replace Scaffold)
    ↓
Phase B Step 2: LDSS Decision Spans (Add Missing)
    ↓
Phase B Step 3: Cost Aggregation (Wire up)
    ↓
Phase B Step 4+5: Tests + Verification
```

**Phase B Prerequisites from Phase A:**
- ✅ DiagnosticsEnvelope.cost_summary field exists
- ✅ DiagnosticsEnvelope.degradation_timeline exists
- ✅ to_response(context=...) method implemented
- ✅ Langfuse SDK v4 adapter + ContextVar span passing

**Phase B Deliverables for Phase C:**
- Real token counts in all span metadata (not zeros)
- Hierarchical cost_summary from span aggregation
- Cost breakdown per component (LDSS, Narrator)
- Trace ID correlation proof (Backend → WE → Manager → Narrator)

---

## Stop Gate (Phase B Complete)

Phase B is done when ALL of these pass:

1. **Narrative block spans have real tokens:**
   - `test_mvp4_narrative_spans_have_real_token_counts` PASS
   - Spans show `input_tokens > 0`, `output_tokens > 0`
   - Model is real (not `"mock"`)

2. **LDSS decision spans exist and track costs:**
   - `test_mvp4_ldss_decision_spans_with_token_tracking` PASS
   - `ldss.decision` spans present with token metadata

3. **Cost summary has real values:**
   - `test_mvp4_cost_summary_aggregates_real_values` PASS
   - `cost_summary.input_tokens > 0`
   - `cost_summary.output_tokens > 0`
   - `cost_summary.cost_usd > 0.0`

4. **Diagnostics context routing works:**
   - `test_mvp4_langfuse_response_context_shows_costs` PASS
   - `to_response("langfuse")` shows costs
   - `to_response("operator")` redacts costs

5. **All MVP4 tests green:**
   - `python tests/run_tests.py --mvp4` — 0 failures
   - No regressions in Phase A tests

---

## Not in Phase B

- SSE narrative streaming (Phase C)
- Cost-aware LDSS degradation (Phase C)
- Token budget enforcement (Phase C)
- Admin governance UIs (Phase C)
- Offline trace export (Phase C fallback)
- Evaluation Pipeline (Phase C)
- Session Replay Debugging (Phase C)
- Audit Trail Multi-Select (Phase C)
