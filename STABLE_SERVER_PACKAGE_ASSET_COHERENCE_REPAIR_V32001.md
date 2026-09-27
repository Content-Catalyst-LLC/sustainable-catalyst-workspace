# Workspace v3.20.0.1 — Stable Server Package & Asset Coherence Repair

## Defect

Workspace v3.20.0 identified itself as `SC_WORKSPACE_VERSION = 3.20.0`, while its WordPress package still carried and enqueued the v3.19.0 shell filenames. The deployment hardening gate derives the current shell paths from `SC_WORKSPACE_VERSION`, so it correctly reported two missing required release files.

## Corrective contract

For every Workspace WordPress release `X`, the package MUST contain readable:

- `assets/js/workspace-vX.js`
- `assets/css/workspace-vX.css`

and `SC_Workspace::enqueue_assets()` MUST enqueue those same version-matched paths.

## v3.20.0.1 behavior

v3.20.0.1 creates version-matched shell files from the known-good v3.19.0 shell because the v3.20 neural release did not introduce shell behavior changes. This preserves runtime behavior while restoring release/package coherence and cache-safe versioning.

## Backend

Backend service version remains 3.20.0. The patch is intentionally WordPress/package-only.
