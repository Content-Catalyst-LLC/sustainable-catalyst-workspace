# Sustainable Catalyst Workspace v3.20.0.1

## Stable Server Package & Asset Coherence Repair

Workspace v3.20.0.1 is a surgical WordPress/package repair for v3.20.0. It does not change the neural backend, database schema, job model, runtime contracts, or browser-local project data.

### Repair

- Adds the version-matched shell assets required by `SC_Workspace_Deployment_Hardening::required_files()`:
  - `assets/js/workspace-v3.20.0.1.js`
  - `assets/css/workspace-v3.20.0.1.css`
- Updates the Workspace WordPress plugin identity to `3.20.0.1`.
- Updates the shell enqueue paths to the v3.20.0.1 asset names.
- Preserves the known-good v3.19 shell bytes because v3.20.0 introduced backend/runtime capability rather than a shell implementation change.
- Adds release validation that fails packaging if the plugin version, required assets, or enqueue paths diverge again.

### Backend compatibility

The correct backend remains Workspace backend **v3.20.0** with the PyTorch neural runtime introduced in v3.20.0. No backend redeploy, migration, or database mutation is required for this patch.

### Safety boundaries

- No browser-local Workspace project data is inspected or modified by the release repair.
- No automatic migration is added.
- No neural training capability is enabled.
- No runtime credentials are changed.
