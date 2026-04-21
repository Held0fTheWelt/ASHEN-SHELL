# Persistence, Incidents, and Non-Graph Testability

Story persistence must be durable enough to restore authoritative sessions and must turn corruption into incident-visible state.

Storage, provenance, birth, restore, and auth seams must remain testable without heavy graph imports when those tests do not logically need the graph runtime.
