# Sustainable Catalyst Workspace v0.66.0

## Import, Export & Backward-Compatibility Hardening

v0.66.0 hardens Workspace interchange without changing Storage 35, Project 20.0, or Project Export 20.0. The release turns top-level Project Import into an explicit staging workflow, makes historical schema support inspectable, blocks unsafe future-schema downgrade, and adds a current-schema round-trip gate to Project Export.

### Project Import: stage, review, then commit

- Selecting a Project JSON file no longer mutates Workspace state.
- Workspace parses and classifies the file locally, then presents a staged compatibility assessment.
- The assessment identifies the source Project schema, Project Export envelope when present, legacy normalization needs, object count, and local source-ID collision.
- Import remains disabled until the staged assessment is supported and ready.
- Committing a staged project always creates a **new local copy** with a newly generated Workspace project ID.
- No existing project is silently overwritten, even when the imported source ID already exists.
- Supported legacy material is normalized only at explicit commit time.
- Project Import is capped at 8 MB in this release and uses the existing browser-safe text-read fallback.

### Backward-compatibility matrix

Workspace now exposes and can export a local compatibility matrix covering:

- `sc-workspace-project/1.0` through `20.0`, including `3.1`;
- `sc-workspace-project-export/1.0` through `20.0`, including `3.1`;
- existing browser-storage migration lineage from Storage 1 through Storage 35;
- portable project packages as a separate **Share & portable projects** workflow;
- interchange bundles as a separate **Import & interoperability** workflow.

Storage-version compatibility describes the existing browser-state migration pipeline. Storage envelopes are **not** accepted by the Project Import control.

### Future and malformed material

- Future Workspace Project/Project Export schemas are blocked rather than downgraded.
- Unknown JSON and malformed/partial project export envelopes are blocked.
- Portable Project and Interchange packages presented to Project Import are redirected conceptually to their purpose-built review surfaces rather than being guessed or coerced into a project import.
- No server import pipeline, remote schema lookup, or automatic trust elevation is introduced.

### Current Project Export round-trip gate

- Before a normal Project Export is written, Workspace projects the candidate through the current project normalizer and compares a stable canonical projection.
- If normalization would change the compared project projection, the normal export is blocked for review instead of silently emitting a potentially lossy file.
- The export envelope records the compatibility mode and a round-trip receipt when the check succeeds.
- FNV-1a fingerprints are used only for deterministic drift comparison. They are **not** cryptographic integrity, authentication, encryption, or security signatures.

### Review surface and REST contract

- Adds a backward-compatibility matrix to **Exchange → Import & interoperability**.
- Adds an exportable compatibility-matrix artifact.
- Adds `/wp-json/sc-workspace/v1/import-export-compatibility-contract` for the public capability boundary.
- Adds schemas for compatibility policy, staged import assessment, compatibility matrix, and round-trip receipt.

### Preserved product hardening

- v0.65 responsive/field-use behavior and contextual Lab handoffs remain intact.
- v0.64.1 desktop-layout recovery and WordPress enqueue-cycle protection remain intact.
- v0.64 keyboard/accessibility runtime remains intact.
- v0.63 browser/device compatibility fallbacks remain intact.
- v0.62 persistence, corruption detection, and recovery integrity remain intact.

### Boundaries

- Storage schema: **35**
- Project schema: **sc-workspace-project/20.0**
- Project Export schema: **sc-workspace-project-export/20.0**
- Schema migration: **none**
- Automatic import commit: **none**
- Silent import overwrite: **none**
- Future-schema downgrade: **none**
- Server import pipeline: **none**
- External schema/network lookup: **none**
- Automatic canonical mutation on file selection: **none**
