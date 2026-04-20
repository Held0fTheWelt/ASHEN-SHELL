# Workstream D: AI Stack Integration — Planning Phase Complete

**Date:** 2026-04-20
**Status:** PLANNING PHASE COMPLETE - READY FOR IMPLEMENTATION
**Prepared By:** Claude Code (Haiku 4.5)

---

## Planning Summary

Workstream D planning is complete and the detailed task list has been created. The implementation is now ready to proceed using Test-Driven Development (TDD) with strict adherence to constitutional laws and fail-closed error handling.

---

## Deliverables from Planning Phase

### 1. Comprehensive Task List
- **Location:** `WORKSTREAM_D_TASK_LIST.md`
- **Content:** 24 tasks organized in 8 phases
- **Coverage:** From prompt catalogs to integration tests to documentation
- **Estimated Work:** 6-10 hours of focused execution

### 2. Detailed Implementation Plan
- **Location:** `.claude/plans/2026-04-20-mvp-workstream-d-ai-stack-integration.md`
- **Content:** Full task breakdown with:
  - Test-first approach for each task
  - File locations and structure
  - Expected artifacts and dependencies
  - Commit instructions with law references
  - Success criteria and validation gates

### 3. Bug Fixes (MCP Client)
- **Issue:** Missing MCP client classes needed by existing tests
- **Fixed:** 
  - Added `MCPToolError` exception class
  - Added `MCPEnrichmentClient` (alias for MCPClient)
  - Added `OperatorEndpointClient` (alias for MCPClient)
  - Updated exports in `__init__.py`
- **Commit:** `1190dd27` - "fix: implement MCPToolError, MCPEnrichmentClient, OperatorEndpointClient (Law 6)"
- **Test Result:** Previously failing `test_mcp_enrichment_attaches_to_adapter_request` now passes

### 4. Baseline Validation
- **MVP Reference Scaffold:** 37/37 tests passing (100%)
- **MCP Surface Tests:** 3/3 tests passing
- **Player Routes Tests:** 20/20 tests passing
- **Status:** Zero regressions, all baselines maintained

---

## Architecture Overview

Workstream D will implement a complete AI stack integration following this flow:

```
Player Action (via MCP)
    ↓
SessionService (Workstream A)
    ↓
with_ai_reasoning decorator
    ├→ Check if AI enabled (via operational_profile)
    ├→ Run LangGraph orchestrator if enabled
    │  ├→ Initialize state (query session via MCP)
    │  ├→ Run decision reasoning (LLM with canonical prompt)
    │  ├→ Select action (LLM chooses best action)
    │  ├→ Execute turn (via MCP execute_turn tool)
    │  └→ Interpret result (LLM generates narrative)
    └→ Collect diagnostics
    ↓
Turn Result + AI diagnostics
```

**Key Principle:** All AI access to game state flows through MCP read tools (mirrors). All AI writes flow through MCP execute_turn tool. No direct state mutation.

---

## Constitutional Laws Coverage (Workstream D)

### Law 1: One Truth Boundary
- AI reads game state via SessionMirror (backend mirror of world-engine state)
- AI executes turns via SessionService.execute_turn (delegates to world-engine)
- All truth remains in world-engine; backend is transparent mirror

### Law 6: Fail Closed on Authority Seams
- Unknown session_id → error, no partial execution
- MCP tool failure → stop reasoning, explicit error
- LLM model failure → fallback safe action, not hidden
- All errors include explicit error_message

### Law 9: AI Composition Bounds
- AI acts ONLY through MCP tools, never direct state access
- MCP tools validate all requests against operating_profile
- AI diagnostics never expose world-engine internals

### Law 10: Runtime Catastrophic Failure
- AI agent crash doesn't crash world-engine
- LangGraph orchestrator has comprehensive error handling
- Degraded states are explicit (never hidden behind success)
- All failures are loggable and auditable

---

## Task Organization (24 Tasks, 8 Phases)

| Phase | Name | Tasks | Focus |
|-------|------|-------|-------|
| 1 | Canonical Prompts | 5 | Game-specific prompt templates |
| 2 | MCP Agent Interface | 5 | Safe MCP tool wrapper |
| 3 | LangGraph State/Nodes | 6 | State schema and graph nodes |
| 4 | LangGraph Orchestrator | 4 | Graph builder and execution |
| 5 | Integration Tests | 5 | Comprehensive test coverage |
| 6 | Turn Decorator | 2 | Player route integration |
| 7 | AI Configuration | 2 | Settings and profiles |
| 8 | Documentation | 2 | Guides and checkpoint |

---

## Expected Artifacts (19 Files)

### Code Files (7)
1. `ai_stack/canonical_prompt_catalog.py`
2. `ai_stack/mcp_agent_interface.py`
3. `ai_stack/langgraph_agent_state.py`
4. `ai_stack/langgraph_agent_nodes.py`
5. `ai_stack/langgraph_orchestrator.py`
6. `ai_stack/turn_execution_decorator.py`
7. `ai_stack/ai_configuration.py`

### Test Files (8)
1. `ai_stack/tests/test_canonical_prompt_catalog.py`
2. `ai_stack/tests/test_mcp_agent_interface.py`
3. `ai_stack/tests/test_langgraph_state_schema.py`
4. `ai_stack/tests/test_langgraph_agent_nodes.py`
5. `ai_stack/tests/test_langgraph_orchestrator.py`
6. `ai_stack/tests/test_turn_execution_decorator.py`
7. `ai_stack/tests/test_ai_agent_integration.py`
8. `ai_stack/tests/test_ai_configuration.py`
9. `backend/tests/routes/test_player_routes_with_ai.py` (optional)

### Documentation Files (4)
1. `ai_stack/PROMPTS.md`
2. `ai_stack/MCP_AGENT_CONTRACT.md`
3. `ai_stack/ORCHESTRATOR.md`
4. `ai_stack/WORKSTREAM_D_INTEGRATION_GUIDE.md`

### Checkpoint & Status
1. `WORKSTREAM_D_CHECKPOINT.md`

---

## Success Criteria (Validation Gates)

### Test Coverage
- [ ] 15+ AI integration tests all passing
- [ ] All existing tests still passing (zero regressions)
- [ ] MVP baseline 37/37 still passing

### Architecture Validation
- [ ] All AI access flows through MCP (auditable)
- [ ] All AI writes flow through execute_turn (fail-closed)
- [ ] No direct state mutation from AI
- [ ] Fail-closed paths verified on all error scenarios

### Code Quality
- [ ] TDD: All tests written before implementation
- [ ] Constitutional laws: All commits reference a law
- [ ] Fail-closed: Every error path has explicit handling
- [ ] Documentation: Guides match actual code behavior

### Integration Points
- [ ] LangGraph nodes properly typed and documented
- [ ] MCP agent interface safe and auditable
- [ ] Canonical prompts game-appropriate and validated
- [ ] Decorator works with player routes

---

## Execution Approach

### Per-Task Workflow (TDD)
1. **Write Test:** Create failing test for feature
2. **Verify Fail:** Run test, confirm it fails with clear message
3. **Implement:** Write minimal code to make test pass
4. **Verify Pass:** Run test, confirm it passes
5. **Commit:** Commit with law reference
6. **Validate:** Run MVP baseline, verify 37/37 passing

### Commit Strategy
- **Frequency:** One commit per task (24 tasks = ~24 commits)
- **Messages:** Reference constitutional law (Law 1, 6, 9, 10)
- **Examples:**
  - "feat: implement canonical prompt catalog (Law 1)"
  - "feat: add MCP agent interface wrapper (Law 9)"
  - "test: verify fail-closed behavior (Law 10)"

### Testing Strategy
- **Unit tests:** Each component in isolation
- **Integration tests:** Components working together
- **End-to-end:** Full AI turn from decision to state mutation
- **Regression:** MVP baseline 37/37 after each phase

---

## Known Assumptions & Dependencies

### Assumed Ready (from Previous Workstreams)
- ✓ Workstream A: SessionService, SessionMirror
- ✓ Workstream B: MCP registry, tool specs, operating_profile
- ✓ Workstream C: Player routes, session binding
- ✓ LangGraph library (already in requirements)
- ✓ Operational profile system

### External Dependencies
- LangGraph 0.x (for graph building)
- LangChain (for LLM integration)
- Claude API (or compatible LLM)

### Not in Scope (Workstream D)
- Persistent session storage (Workstream E)
- Operator review surfaces (Workstream E)
- Advanced RAG/retrieval (Workstream E)
- Multi-player coordination (later)

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| LLM timeouts | Timeout parameter in MCP calls, fallback actions |
| MCP failures | Explicit MCPToolError, fail-closed paths |
| State corruption | All writes via execute_turn (world-engine owns) |
| AI bias | Prompt validation, operational profile gates |
| Performance | Diagnostic tracking, no-polling orchestrator |

---

## File Locations Quick Reference

**Planning:**
- Master plan: `.claude/plans/2026-04-20-mvp-v24-integration-master.md`
- Detailed tasks: `.claude/plans/2026-04-20-mvp-workstream-d-ai-stack-integration.md`
- Task list: `WORKSTREAM_D_TASK_LIST.md` (this directory)

**Previous Checkpoints:**
- Workstream A: `WORKSTREAM_A_CHECKPOINT.md`
- Workstream B: `WORKSTREAM_B_CHECKPOINT.md`
- Workstream C: `.claude/checkpoints/WORKSTREAM_C_CHECKPOINT.md`

**Code to Reference:**
- SessionService: `backend/app/services/session_service.py`
- MCP Canonical Surface: `ai_stack/mcp_canonical_surface.py`
- Operational Profile: `ai_stack/operational_profile.py`
- Player Routes: `backend/app/api/v1/player_routes.py`

---

## Next Steps

1. **Execute Phase 1:** Create canonical prompt catalog
   - Start with test: `ai_stack/tests/test_canonical_prompt_catalog.py`
   - Implement: `ai_stack/canonical_prompt_catalog.py`
   - Verify: Test passes, MVP baseline still 37/37
   - Commit: "feat: implement canonical prompt catalog (Law 1)"

2. **Execute Phase 2:** Create MCP agent interface
   - Start with test: `ai_stack/tests/test_mcp_agent_interface.py`
   - Implement: `ai_stack/mcp_agent_interface.py`
   - Verify: All MCP tool calls work correctly
   - Commit: "feat: implement MCP agent interface (Law 9)"

3. **Continue Through Phase 8:** Follow task list in order
   - Each phase builds on previous
   - Tests provide confidence gates
   - MVP baseline prevents regressions

---

## Contacts & References

**Task List Document:** `WORKSTREAM_D_TASK_LIST.md`
**Detailed Plan:** `.claude/plans/2026-04-20-mvp-workstream-d-ai-stack-integration.md`
**Master Plan:** `.claude/plans/2026-04-20-mvp-v24-integration-master.md`

**Key Contacts:**
- Test Failures: Check `backend/tests/runtime/` for existing test expectations
- MCP Issues: Check `tools/mcp_server/` and `backend/app/mcp_client/`
- LangGraph Issues: Check `ai_stack/langgraph_*` files and tests
- Constitutional Laws: Review `MVP/mvp/docs/48_CANONICAL_IMPLEMENTATION_PROTOCOL.md`

---

## Checklist: Planning Phase Complete

- [x] Task list created (24 tasks, 8 phases)
- [x] Detailed plan documented
- [x] MCP client classes fixed
- [x] MVP baseline validated (37/37 passing)
- [x] Architecture documented
- [x] Success criteria defined
- [x] Execution approach defined
- [x] Risk mitigation planned
- [x] File locations documented
- [x] Next steps clear

**Status: READY FOR IMPLEMENTATION**

Ready to proceed with Phase 1 (Canonical Prompt Catalog) using TDD approach.

---

**Prepared:** 2026-04-20 by Claude Code (Haiku 4.5)
**Duration:** Planning phase complete
**Commits:** 2 commits (task list + MCP fixes)
**Next Milestone:** Phase 1 completion with 5+ tests passing
