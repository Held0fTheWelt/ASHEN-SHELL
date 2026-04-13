# 07 Settings Inventory for Backend, World-engine, and AI

This document identifies settings that should be moved from hidden env/code-default patterns into operational governance.

## A. Must become administrable

### AI runtime and providers
- generation execution mode
- provider selection mode
- provider enable/disable
- provider base URLs
- provider credentials
- model inventory
- model role (LLM/SLM/Mock)
- route preferred/fallback/mock model mapping
- route enable/disable
- timeout per model
- structured output support flags
- runtime profile

### Retrieval
- retrieval execution mode
- embeddings enable/disable
- embedding model choice
- embedding cache policy
- retrieval degradation behavior
- retrieval route/profile

### World-engine runtime behavior
- validation execution mode
- semantic validation enabled
- corrective feedback enabled
- retry count
- fallback threshold alerts
- preview isolation mode
- runtime diagnostics verbosity
- content sync enabled
- content sync interval
- content timeout
- content source precedence

### Backend integration behavior
- play-service internal URL
- play-service public URL
- play-service request timeout
- game ticket TTL
- public application URLs
- mail enabled
- email verification enabled
- verification TTL
- notification thresholds appropriate to operations

## B. Should become administrable with caution
- CORS origins
- ratelimit defaults where operationally needed
- N8N integration toggles if operational
- docs/admin/public URL values
- budget warning thresholds
- fallback and degradation thresholds
- MCP operating profile
- MCP suite exposure

## C. Should remain deployment/trust-root managed
- Flask/Django/FastAPI secret keys
- JWT master secret roots
- database root credentials
- KEK / master encryption key
- raw repo root paths
- container bootstrap-only process secrets

## Current hidden/default sources to replace

### Code defaults
- model registry default provider/model mapping
- adapter env reads for real providers
- world-engine startup validator defaults

### Env/config examples
- OpenAI API key
- Ollama base URL
- retrieval embedding toggles/cache path
- MCP profile and suite selection
- backend/world-engine sync URLs and timeouts

## Governance rule

If a setting changes normal operation and an operator may reasonably need to adjust it after first install, it belongs in the operational governance plane unless it is a trust-root secret.
