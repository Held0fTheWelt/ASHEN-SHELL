# What degraded mode means

Degraded mode means the system is still running, but with reduced capability.

Example:
- a stale vector index may force lexical-only retrieval
- a provider outage may force safer low-intensity continuation
- an audit request may block if lineage is incomplete

Degraded is not the same as safe for every task.
