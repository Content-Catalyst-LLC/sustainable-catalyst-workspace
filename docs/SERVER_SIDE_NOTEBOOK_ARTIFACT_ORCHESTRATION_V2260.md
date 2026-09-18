# Workspace v2.26.0 — Server-Side Notebook & Artifact Orchestration

Workspace notebooks remain authored in the browser, but execution orchestration is server-authoritative. Executable cells opt in with an explicit `execution` object. The backend validates bounded operations, pins input artifact revision/SHA-256 identity, rejects dependency cycles, stores an immutable planning fingerprint, queues only dependency-ready steps, and advances downstream steps only after upstream success.

The browser does not infer operations, approve remote execution, schedule dependency graphs, or execute arbitrary code. External product routes remain server-configured only.
