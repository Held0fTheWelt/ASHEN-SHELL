# Test Task — Infrastructure Validation

Minimal test case to validate Clockwork hybrid orchestration setup.

## Objective

Verify that Phase Dispatcher (Sonnet-equivalent) can route work to specialist agents and capture evidence/reports correctly.

## Phases (Simplified)

### Phase 1: Specification
- Read this test task
- Identify what needs validation
- Route to Phase 2

**Acceptance:** Clear routing decision recorded in brain/

### Phase 2: Implementation
- Create a simple test file: `backend/tests/test_infrastructure_validation.py`
- Write 2-3 basic tests (no real logic, just structural validation)
- Commit changes

**Acceptance:** Tests pass, commit recorded in audit/

### Phase 3: Verification
- Run tests and capture results
- Generate gate report
- Store in reports/

**Acceptance:** Gate report shows all tests passing

### Phase 4: Documentation
- Update INFRASTRUCTURE.md with test results
- Record learnings in knowledge/

**Acceptance:** Learnings captured for future reference

## Deliverables

- Evidence trail in `.clockwork_runtime/`
- Phase reports in `.clockwork_runtime/reports/`
- Test results in `.clockwork_runtime/evidence/`
- Refined setup documented in INFRASTRUCTURE.md
