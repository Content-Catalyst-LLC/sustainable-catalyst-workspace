# Workspace v2.17.0 — Reproduction & Cross-Runtime Verification

The v2.17 verification layer compares two completed Workspace execution runs without executing user-supplied code.

Comparison modes:
- `exact-digest`: byte-identical SHA-256 + size.
- `tolerance-aware-json`: recursive structure comparison with configurable absolute/relative numeric tolerances.
- `auto`: exact digest first, then bounded JSON comparison.

A durable receipt records original/reproduction run IDs, source/target runtime labels, input/environment/runtime equality, exact/equivalent output status, tolerances, classification, result artifact, SHA-256, and comparison details.

Classifications are `exact`, `equivalent`, `divergent`, or `incomplete`.

Binary Arrow/Parquet or other non-JSON outputs require exact content digests in v2.17; semantic cross-format table equivalence remains explicitly bounded for a later build.
