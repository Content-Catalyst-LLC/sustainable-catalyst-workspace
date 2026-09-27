# Workspace v3.21.0 — Neural Dataset, Tensor & Transformation Interchange

Workspace v3.21.0 extends the bounded PyTorch neural runtime with governed data interchange primitives.

## Runtime operations

The neural runtime now exposes eight operations. Four v3.20 operations remain unchanged and four are added:

- `workspace.neural.tensor-contract` — validates inline tensor values and emits a canonical tensor contract plus fingerprint.
- `workspace.neural.dataset-manifest` — validates a provenance-oriented dataset reference/manifest without reading external data.
- `workspace.neural.batch-plan` — creates deterministic bounded batch plans, including drop-last and seeded-shuffle intent metadata.
- `workspace.neural.transformation-apply` — applies a bounded declarative transform pipeline and returns per-step lineage/fingerprints.

Supported transformation operators are identity, cast, standardize, minmax, clip, and select-columns. Client code, packages, serialized neural modules, arbitrary filesystem paths, and runtime URLs remain prohibited.

## Ownership boundary

Workspace performs bounded tensor compute and records interchange lineage. Existing dataset/import/interchange services remain responsible for ingesting external sources. Platform Core remains authoritative for governed research/model provenance contracts. Training remains disabled until the later neural-training milestone.
