# 05 Admin Bootstrap and UI

## UI split

### A. Bootstrap Setup Suite
Accessible from:
- `docker-up.py` guided flow
- bootstrap web route
- protected recovery bootstrap route

Purpose:
- first initialization
- trust-anchor selection
- runtime preset selection
- first provider and credential onboarding
- first runtime mode selection

### B. Operational Settings Suite
Accessible in the administration-tool after bootstrap.

Purpose:
- ongoing administration and tuning

## Bootstrap UI pages

### 1. Welcome / system state
Shows:
- uninitialized vs initialized
- why bootstrap is required
- next steps

### 2. Preset selection
Preset cards:
- Local Mock Safe
- Local Hybrid
- Cloud Narrative
- Research / Evaluation
- Custom

### 3. Trust-anchor and storage
Fields:
- secret storage mode
- recovery mode policy
- bootstrap protection note
- optional separate secret DB settings
- trust-anchor confirmation

### 4. Initial runtime mode
Selections:
- mock only
- AI only
- hybrid
- retrieval mode
- validation mode
- runtime profile

### 5. First provider setup
Sections:
- provider type
- base URL
- enabled flag
- write-only credential input if required
- test connection button

### 6. Initial admin confirmation
- summary
- save and initialize
- launch stack

## Operational Settings pages

### 1. Overview
- active runtime profile
- generation mode
- retrieval mode
- validation mode
- provider health summary
- cost summary
- alerts
- direct links to major settings sections

### 2. Providers
- provider list
- create/edit provider
- credential configured status
- rotate credential
- test connection
- health state
- provider enable/disable

### 3. Models
- model inventory
- role tags: LLM / SLM / Mock
- timeout
- structured output capability
- cost method
- pricing info

### 4. Routes
- task routing table
- preferred/fallback/mock model
- scope and enablement
- effective strategy preview

### 5. Runtime Modes
- generation mode
- retrieval mode
- validation mode
- provider selection mode
- runtime profile
- preview of effective behavior

### 6. Backend Settings
- play-service URLs
- ticket TTL
- public URLs
- mail toggles
- rate and timeout controls appropriate for admin governance

### 7. World-engine Settings
- content sync behavior
- diagnostics verbosity
- preview isolation mode
- validator/retry/fallback settings where governed here

### 8. Retrieval
- retrieval enabled/disabled
- sparse/hybrid
- embedding model selection
- cache/index strategy
- degradation visibility

### 9. Costs & Usage
- budget policies
- usage charts
- provider and model cost rollups
- fallback and retry cost impact

### 10. Health & Alerts
- provider health
- degraded runtime events
- budget warnings
- notification configuration

### 11. Audit
- setting changes
- credential rotations
- mode changes
- bootstrap/recovery events

## UX principles

- The operator should never need to know a hidden env var name to make a normal operational choice.
- Secrets are write-only.
- Dangerous settings must show consequence hints.
- Mode switching must show prerequisites and blockers before save.
- The current active behavior must be inspectable in human language.

## Critical operator journeys

### Journey 1: first startup
`docker-up.py` -> bootstrap web UI -> preset selection -> provider credential -> initialize -> stack starts

### Journey 2: switch from mock to hybrid
Administration-tool -> Runtime Modes -> choose Hybrid -> verify route completeness -> save -> resolved runtime config reload -> health confirmation

### Journey 3: rotate provider secret
Providers -> select provider -> rotate credential -> test connection -> audit event visible

### Journey 4: investigate unexpected cost spike
Costs & Usage -> provider/model rollups -> identify route -> inspect runtime mode and fallback usage

### Journey 5: recover bootstrap
Protected bootstrap recovery route -> elevated auth -> repair trust-anchor/storage/provider basics
