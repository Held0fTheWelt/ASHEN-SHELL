# 01 Scope and Goals

## Objective

Implement a complete MVP suite that makes backend, world-engine, AI runtime, retrieval, and provider settings administrable through a secure and discoverable governance model.

The suite must eliminate the current pattern where critical operating behavior is hidden in:
- environment variables
- deployment-only defaults
- hardcoded runtime choices
- scattered code-level registries
- partially implicit startup behavior

## Primary outcome

A user must be able to:

1. start the system with `docker-up.py`
2. be guided into bootstrap setup if the system is not initialized
3. choose a usable preset
4. choose mock, AI, or hybrid runtime mode
5. configure providers and credentials safely
6. launch the stack
7. later manage the full operational configuration in the administration-tool

## MVP scope

### In scope

- Bootstrap/trust-anchor setup experience
- Web-first setup suite plus `docker-up.py` orchestration
- Admin-only configuration flows
- Encrypted credential storage in backend-controlled persistence
- Runtime mode governance for:
  - mock
  - AI
  - hybrid
- Provider/model/routing governance
- Retrieval governance
- Backend settings governance
- World-engine settings governance
- Cost and usage governance
- Health, alert, and budget visibility
- Settings inventory migration out of hidden `.env` and code defaults where operationally appropriate

### Out of scope

- Full infrastructure-secret rotation for all deployment roots through the same normal admin UX
- Full secret-manager integration as mandatory requirement
- Complex self-service multi-tenant support
- Full feature parity for every future provider on day one
- Replacing deployment orchestration or Docker itself

## Design goals

### 1. Discoverability
A new operator must not be forced to hunt through `.env` files, code defaults, or docs to find core configuration.

### 2. Security
Secrets must be write-only from the UI, encrypted at rest, and never re-rendered in raw form.

### 3. Flexibility
Operators must be able to move between mock, AI, and hybrid modes without code edits.

### 4. Operational clarity
The system must make it obvious which provider, model, route, and runtime profile are active.

### 5. Cost awareness
Usage and cost must be measurable and attributable by provider, model, and workflow.

### 6. Runtime correctness
Backend and world-engine must consume resolved configuration rather than scattered ad hoc defaults.

## Key simplifications introduced by this suite

- A guided bootstrap entry point instead of hidden initialization work
- A split between trust-anchor setup and normal operations
- A single settings governance domain instead of multiple unrelated config paths
- Explicit runtime mode selection instead of inferred mode behavior
- Provider/model/routing as persisted domain data instead of code constants
