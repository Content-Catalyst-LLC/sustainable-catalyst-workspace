# Sustainable Catalyst Workspace v0.9.0

## Evidence, Provenance & Reproducibility

This release makes traceability a first-class Workspace capability. Projects now include an Evidence / Provenance / Reproducibility mode for explicit evidence assessment, object lineage, SHA-256 content fingerprints, and analysis reproduction records.

### Added
- `sc-workspace-traceability/1.0` project sub-contract.
- Evidence assessment for Source and Evidence objects with relevance, source quality, independence, recency, notes, and SHA-256 fingerprints.
- Fingerprint verification to detect when an assessed object has changed.
- Object lineage relations: derived-from, supports, contradicts, uses, produced-by, informs, supersedes, cites.
- Reproducibility records linking analysis, datasets, evidence, method, parameters, environment, and reproduction steps.
- Portable reproduction package JSON export.
- Traceability package JSON export.
- `/wp-json/sc-workspace/v1/traceability-contract`.
- Canonical Knowledge Library route corrected to `/knowledge-libraries/`.

### Migration
- Storage schema 9 → 10.
- Project schema `sc-workspace-project/7.0` → `sc-workspace-project/8.0`.
- Existing objects and all prior project sub-contracts are preserved.

### Boundary
Workspace remains free, public, anonymous-capable, device-local, and without automatic cloud synchronization or server project storage.
