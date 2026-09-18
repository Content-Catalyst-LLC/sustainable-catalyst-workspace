# Workspace v2.27.0 — Reproducible Scientific Study Packages

- Adds backend-authoritative scientific study package creation and verification.
- Captures project/notebook state, datasets, models, parameter sets, environments, runtime adapters, execution runs, notebook plans, jobs, scientific receipts, and provenance.
- Pins artifacts by revision, SHA-256, byte count, and optionally embeds immutable artifact snapshots in a deterministic ZIP bundle.
- Stores the study bundle itself in content-addressed Workspace object storage and emits durable create/verify receipts.
- Uses canonical deterministic manifests and SHA-256 closure verification; arbitrary-code execution remains disabled.
- Preserves the restored full-size Workspace interface asset lineage.
