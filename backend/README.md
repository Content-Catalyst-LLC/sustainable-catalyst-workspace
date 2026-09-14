# Sustainable Catalyst Workspace Backend v2.6.0

Workspace v2.6.0 extends the reproducible execution registry with versioned runtime adapters and reproduction verification.

## Added in v2.6.0
- runtime adapter heads and immutable revisions
- Python/R/Julia/custom runtime descriptors
- environment compatibility/readiness checks
- runtime-adapter references frozen into execution runs
- reproduction plans from original run provenance
- verification receipts comparing frozen inputs and output SHA-256 digests
- exact / compatible / divergent / incomplete classifications

Workspace does not accept arbitrary command strings, automatically execute reproduction plans, or treat a metadata compatibility check as proof that a runtime is installed.
