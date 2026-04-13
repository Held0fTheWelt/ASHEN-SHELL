# 02 Architecture and Trust Model

## Architectural overview

This MVP introduces three configuration planes:

1. **Bootstrap / Trust-Anchor Plane**
2. **Operational Governance Plane**
3. **Resolved Runtime Execution Plane**

## 1. Bootstrap / Trust-Anchor Plane

This plane exists to make the system safely initializable and easy to find.

It governs:
- initial admin bootstrap
- trust-anchor initialization
- secret storage mode selection
- initial preset selection
- initial runtime mode selection
- first provider and credential setup
- readiness marker indicating that the system is initialized

This plane is exposed through:
- `docker-up.py`
- protected bootstrap web UI
- optional bootstrap CLI fallback

This plane is intentionally narrow.

## 2. Operational Governance Plane

This is the normal post-bootstrap administration layer.

It governs:
- providers
- models
- routes
- runtime execution mode
- retrieval execution mode
- validation execution mode
- backend settings
- world-engine settings
- notifications
- health
- usage and costs
- budgets and alerts

This plane lives in:
- backend persistence and services
- administration-tool pages
- internal runtime config APIs
- health/usage event ingestion

## 3. Resolved Runtime Execution Plane

This is what backend, world-engine, ai_stack, and writers-room consume at execution time.

It is a resolved, server-side configuration view derived from:
- active settings profiles
- enabled providers/models/routes
- effective runtime policies
- secret resolution
- safe fallbacks

The runtime must not depend on:
- raw UI values
- direct browser-held secrets
- hidden hardcoded defaults as primary source of truth

## Trust boundary model

### Administration-tool
- UI only
- no direct secret persistence logic
- no raw secret reads
- authenticated admin access only

### Backend
- authoritative control plane
- encrypted secret storage
- provider/model/route/settings governance
- usage/cost metering
- runtime config resolution
- audit trail
- health and notification policy

### World-engine
- runtime consumer of resolved config
- may call internal backend config endpoints
- must not become the primary source of provider/credential truth

### ai_stack / writers-room
- consumers of resolved config and allowed routing rules
- no direct raw secret admin behavior

## Storage recommendation

### Preferred
- governance metadata in primary backend DB
- secrets in separate secret DB
- envelope encryption
- KEK outside both DBs

### Acceptable MVP fallback
- governance and secret tables in same backend DB
- strict table/service separation
- same encryption model
- same KEK separation principle

## Why Resolved Runtime Config is the chosen execution model

This suite chooses **Resolved Runtime Config** rather than a mandatory backend proxy gateway for all LLM requests.

Why:
- simpler MVP integration
- less runtime coupling
- still centralizes settings and secret authority
- allows later evolution to backend gateway if desired

Under this model:
- backend resolves effective provider/model/runtime settings
- internal services fetch resolved config
- runtime components instantiate adapters from resolved config
- raw credentials remain backend-controlled

## Bootstrap simplification rule

The system must never leave the operator uncertain about where first configuration lives.

If bootstrap is incomplete:
- `docker-up.py` must say so
- the web setup suite must be reachable
- the path to complete initialization must be obvious
