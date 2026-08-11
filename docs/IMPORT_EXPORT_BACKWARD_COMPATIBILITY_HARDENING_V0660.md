# v0.66.0 — Import, Export & Backward-Compatibility Hardening

## Purpose

v0.66.0 treats interchange as a preservation boundary. A file chosen by the user is not assumed to be current, complete, safe to downgrade, or safe to write over an existing project. The release therefore separates **inspection** from **commit** and makes the supported historical schema line explicit.

This release does not introduce a new canonical data model. Storage remains 35; Project remains `sc-workspace-project/20.0`; Project Export remains `sc-workspace-project-export/20.0`.

## Top-level Project Import contract

The Project Import workflow is:

1. **Choose** a local JSON file.
2. **Parse** it locally through the existing browser-compatible file reader.
3. **Classify** the envelope and project schema.
4. **Stage** a compatibility assessment. No Workspace project is created at this point.
5. **Review** source schema, normalization requirement, project title/object count, source ID, and collision information.
6. **Commit** only after explicit user action.
7. **Normalize** supported legacy material to the current Project model at commit time.
8. **Assign a new local project ID** regardless of whether the source ID collides.
9. Preserve the imported project as an independent local copy and record the import activity.

A file-selection event therefore cannot silently overwrite, merge into, or replace a canonical local project.

## Supported historical project line

The v0.66 Project Import classifier recognizes these documented Workspace Project and Project Export versions:

`1.0, 2.0, 3.0, 3.1, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0, 20.0`.

Both raw Project records (`sc-workspace-project/<version>`) and Project Export envelopes (`sc-workspace-project-export/<version>`) use that compatibility line. An export envelope must also contain a supported Workspace Project payload.

This is a Workspace historical compatibility guarantee. It is **not** a claim that arbitrary third-party JSON can be interpreted as a Workspace project.

## Existing browser-storage lineage

Workspace retains its pre-existing Storage migration chain from Storage 1 through Storage 35 for local browser state. That migration path is distinct from Project Import:

- Storage envelopes are consumed by the Workspace state loader/migration pipeline.
- Storage envelopes are not accepted as Project Import files.
- v0.66 does not rewrite already-current Storage 35 state merely because the release was installed.

## Future schema policy

A Project or Project Export created by a future Workspace project generation is blocked by the v0.66 Project Import boundary. Workspace does not attempt to infer a downgrade from fields it does not understand.

The user is told that the file cannot be safely downgraded. No project is created, no existing project is changed, and no network lookup is made to guess a conversion.

Unknown JSON and malformed/partial project export envelopes are likewise rejected rather than coerced into a project.

## Purpose-built package surfaces remain separate

v0.66 does not collapse every import format into Project Import.

- `sc-workspace-portable-project/1.0` stays under **Share & portable projects**, including its package integrity verification and import-as-copy workflow.
- `sc-workspace-interchange/2.0` stays under **Import & interoperability**, including staged review and profile handling.

If one of these package families is selected in Project Import, the classifier blocks the top-level import and identifies the appropriate Workspace surface.

## Current Project Export round-trip validation

Normal Project Export now checks whether the candidate survives current project normalization without changing a stable comparison projection.

The comparison intentionally ignores volatile/local persistence fields that are not meaningful to interchange, including the local persistence envelope, `updatedAt`, active-object UI state, and activity timestamps. The remaining projection is stable-key ordered, normalized, and compared before the file is written.

If the normalized projection differs, Workspace blocks the normal Project Export and asks the user to review/recover rather than emitting a file that has already demonstrated drift inside the current normalizer.

A successful export includes a `sc-workspace-round-trip-receipt/1.0` receipt.

### Fingerprint boundary

The round-trip receipt uses an FNV-1a 32-bit fingerprint to make deterministic before/after drift easy to inspect in the browser. FNV-1a here is **not**:

- a cryptographic checksum;
- an authentication mechanism;
- a signature;
- encryption;
- protection against an adversarially modified file.

Cryptographic package-integrity workflows elsewhere in Workspace continue to use SHA-256 where their package contracts require it.

## Compatibility matrix artifact

The v0.66 matrix (`sc-workspace-backward-compatibility-matrix/1.0`) exposes:

- current Storage/Project/Project Export versions;
- supported historical Project and Project Export schema strings;
- supported existing Storage migration generations;
- the staged/new-copy Project Import policy;
- the future-schema block policy;
- the separate Portable Project and Interchange surfaces;
- automatic-action boundaries.

The matrix can be exported locally from the Import & interoperability surface for field diagnostics, support, and release auditing.

## Non-goals

v0.66 does not add:

- automatic migration on file selection;
- silent overwrite or last-write-wins import;
- live/server-side import jobs;
- schema downloads or remote conversion services;
- automatic AI interpretation of unknown files;
- future-schema downgrade;
- arbitrary third-party JSON ingestion through Project Import;
- a new Project or Storage schema.

## Field-validation cases

Beyond automated contract/runtime fixtures, production validation should include:

- current Project 20.0 raw import;
- current Project Export 20.0 import;
- representative early legacy exports (1.0, 3.1, 10.0);
- an imported source ID that already exists locally;
- malformed JSON;
- a recognized export envelope with missing project payload;
- future Project/Export schema rejection;
- Project Export round-trip success on a real populated project;
- normal Project Export blocking if current normalization is deliberately made lossy in a test environment;
- Portable Project and Interchange packages continuing through their dedicated surfaces.
