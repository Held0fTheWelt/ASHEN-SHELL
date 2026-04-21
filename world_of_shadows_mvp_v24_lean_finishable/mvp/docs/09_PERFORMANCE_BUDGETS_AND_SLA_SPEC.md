# 09 — Performance Budgets and SLA Specification

## Latency budgets
- p50: < 2 s
- p95: < 5 s
- p99: < 10 s

## Token budgets
- input context target: < 8k tokens
- output target: < 1k tokens

## Cost budgets
- per turn: < $0.10
- per session: < $2.00

## Degradation triggers
- high latency → reduce retrieval breadth
- high cost → compress context or use cheaper non-critical models
- stale indexes → switch to profile-appropriate degraded retrieval
