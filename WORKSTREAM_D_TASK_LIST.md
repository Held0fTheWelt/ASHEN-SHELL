# Workstream D: AI Stack Integration - Task List

**Date:** 2026-04-20
**Status:** READY TO START
**Scope:** LangGraph integration with MCP surface and canonical prompts
**Test Target:** 15+ AI integration tests, all passing
**MVP Baseline:** 37/37 still passing (zero regressions)
**Expected Commits:** 8-12 commits with constitutional law references

---

## Executive Summary

Workstream D integrates LangGraph with the MCP surface and canonical prompts to enable AI-driven gameplay decisions. The implementation follows a strict TDD approach with fail-closed error handling and comprehensive testing. All AI access flows through the MCP interface (no direct state mutation), ensuring architectural purity.

---

## Task Phases (24 Tasks Total)

### Phase 1: Canonical Prompt Catalog (5 tasks)
- D1.1: Create prompt catalog structure
- D1.2: Define game-specific prompt templates
- D1.3: Add prompt validation and safety checks
- D1.4: Integrate prompts with operational profile
- D1.5: Document prompt catalog API

### Phase 2: MCP Agent Interface (5 tasks)
- D2.1: Create MCP agent interface wrapper
- D2.2: Add MCP client integration
- D2.3: Add tool call logging and diagnostics
- D2.4: Add fail-closed validation
- D2.5: Document MCP agent interface contract

### Phase 3: LangGraph State and Nodes (6 tasks)
- D3.1: Define LangGraph state schema
- D3.2: Implement state initialization node
- D3.3: Implement decision reasoning node
- D3.4: Implement action selection node
- D3.5: Implement turn execution node
- D3.6: Implement result interpretation node

### Phase 4: LangGraph Orchestrator (4 tasks)
- D4.1: Create LangGraph orchestrator
- D4.2: Add error handling and degradation
- D4.3: Add diagnostic tracking
- D4.4: Document orchestrator API

### Phase 5: Integration Tests (5 tasks)
- D5.1: Test MCP agent interface with mocks
- D5.2: Test orchestrator with mock world state
- D5.3: Test AI agent against SessionService
- D5.4: Test fail-closed behavior
- D5.5: Verify MVP baseline regression

### Phase 6: Turn Execution Decorator (2 tasks)
- D6.1: Create turn execution decorator
- D6.2: Test decorator integration with player routes

### Phase 7: AI Configuration (2 tasks)
- D7.1: Create AI configuration contract
- D7.2: Integrate with operational profile

### Phase 8: Documentation and Finalization (2 tasks)
- D8.1: Create AI Stack Integration guide
- D8.2: Create Workstream D checkpoint

---

## Implementation Approach

**TDD Pattern for Each Task:**
1. Write failing test (verify it fails)
2. Implement minimal code to pass test
3. Run test (verify it passes)
4. Commit with law reference
5. Run MVP baseline (verify 37/37 still passing)

**Constitutional Laws (Workstream D Focus):**
- Law 1: One truth boundary
- Law 6: Fail closed on authority seams
- Law 9: AI composition bounds
- Law 10: Runtime catastrophic failure

---

## Expected Artifacts

**Code Files (7-10):**
- `ai_stack/canonical_prompt_catalog.py`
- `ai_stack/mcp_agent_interface.py`
- `ai_stack/langgraph_agent_state.py`
- `ai_stack/langgraph_agent_nodes.py`
- `ai_stack/langgraph_orchestrator.py`
- `ai_stack/turn_execution_decorator.py`
- `ai_stack/ai_configuration.py`

**Test Files (8):**
- `ai_stack/tests/test_canonical_prompt_catalog.py`
- `ai_stack/tests/test_mcp_agent_interface.py`
- `ai_stack/tests/test_langgraph_state_schema.py`
- `ai_stack/tests/test_langgraph_agent_nodes.py`
- `ai_stack/tests/test_langgraph_orchestrator.py`
- `ai_stack/tests/test_turn_execution_decorator.py`
- `ai_stack/tests/test_ai_agent_integration.py`
- `ai_stack/tests/test_ai_configuration.py`
- `backend/tests/routes/test_player_routes_with_ai.py` (optional)

**Documentation Files (3-4):**
- `ai_stack/PROMPTS.md`
- `ai_stack/MCP_AGENT_CONTRACT.md`
- `ai_stack/ORCHESTRATOR.md`
- `ai_stack/WORKSTREAM_D_INTEGRATION_GUIDE.md`

**Checkpoint:**
- `WORKSTREAM_D_CHECKPOINT.md`

---

## Key Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Tests passing | 15+ | TBD |
| MVP baseline | 37/37 | TBD |
| Code coverage | AI stack | TBD |
| Commits | 8-12 | TBD |
| Fail-closed paths | 100% | TBD |
| MCP usage | 100% of AI access | TBD |

---

## Success Criteria (Final Checkpoint)

- [ ] 15+ AI integration tests all passing
- [ ] All AI access flows through MCP (no direct state mutation)
- [ ] Fail-closed behavior verified on all error paths
- [ ] LangGraph orchestrator working with multi-step reasoning
- [ ] Canonical prompts integrated and validated
- [ ] MCP agent interface safe and auditable
- [ ] MVP baseline 37/37 still passing (zero regressions)
- [ ] 8-12 commits with law references
- [ ] Documentation complete and accurate
- [ ] Ready for Workstream E (Governance Surfaces)

---

## Related Documents

- **Master Plan:** `.claude/plans/2026-04-20-mvp-v24-integration-master.md`
- **Detailed Tasks:** `.claude/plans/2026-04-20-mvp-workstream-d-ai-stack-integration.md`
- **Workstream A:** `WORKSTREAM_A_CHECKPOINT.md`
- **Workstream B:** `WORKSTREAM_B_CHECKPOINT.md`
- **Workstream C:** `.claude/checkpoints/WORKSTREAM_C_CHECKPOINT.md`

---

## Quick Reference: File Locations

**Configuration:**
- Prompts: `ai_stack/canonical_prompt_catalog.py`
- MCP Interface: `ai_stack/mcp_agent_interface.py`
- LangGraph: `ai_stack/langgraph_*` (4 files)
- AI Config: `ai_stack/ai_configuration.py`

**Tests:**
- Test directory: `ai_stack/tests/test_*` (5+ files)
- Integration: `ai_stack/tests/test_ai_agent_integration.py`
- Routes: `backend/tests/routes/test_player_routes_with_ai.py` (optional)

**Documentation:**
- Catalog: `ai_stack/PROMPTS.md`
- Contract: `ai_stack/MCP_AGENT_CONTRACT.md`
- API: `ai_stack/ORCHESTRATOR.md`
- Guide: `ai_stack/WORKSTREAM_D_INTEGRATION_GUIDE.md`

---

**Next Step:** Execute Phase 1, Task D1.1 with TDD approach
