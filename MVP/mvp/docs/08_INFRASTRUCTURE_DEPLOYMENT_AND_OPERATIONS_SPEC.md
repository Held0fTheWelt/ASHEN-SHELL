# 08 — Infrastructure, Deployment, and Operations Specification

Baseline services:
- frontend
- backend
- administration-tool
- world-engine
- relational store
- vector / search store
- cache / queue
- metrics stack

Reference baseline:
- PostgreSQL for authoritative relational state
- Redis for fast coordination and checkpoints
- Qdrant or equivalent for vector retrieval
- persistent lexical index storage
- Prometheus + Grafana for metrics
- object storage for assets and replay exports
