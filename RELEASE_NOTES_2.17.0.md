# Workspace v2.17.0 — Reproduction & Cross-Runtime Verification

Workspace v2.17.0 adds a server-side reproduction verification layer over the existing Python, R, Julia, ML, and native Arrow/Parquet runtime fabric.

## Added
- Durable cross-runtime verification receipts (migration 017).
- Exact content-digest verification for byte-identical outputs.
- Tolerance-aware recursive comparison for bounded JSON numeric results.
- Explicit input, environment, runtime-adapter, and output equivalence lineage.
- Exact / equivalent / divergent / incomplete classifications.
- Result artifacts with SHA-256 fingerprints for each verification.
- WordPress proxy routes for profiles, verification creation, receipt lists, and receipt retrieval.

## Governance
- No arbitrary code execution.
- No client-supplied runtime URLs or credentials.
- Verification never dispatches a new computation automatically.
- Non-JSON binary outputs require exact content digests in v2.17.
