# Validation Report — Workspace v3.20.0.1

Validation scope: stable server package / WordPress asset coherence repair.

Expected invariants:

- Plugin header and `SC_WORKSPACE_VERSION` are 3.20.0.1.
- Version-matched JS/CSS shell assets are packaged and non-empty.
- WordPress enqueues the v3.20.0.1 shell paths.
- No stale v3.19.0 shell enqueue remains.
- Deployment hardening still derives required shell files from `SC_WORKSPACE_VERSION`.
- Backend remains v3.20.0 and the PyTorch neural runtime remains present.
- No database migration is introduced.

Release tooling additionally provides:

- local Git apply/push/tag automation;
- a Bluehost WordPress installer with timestamped plugin backup and post-install preflight;
- a Contabo compatibility verifier confirming the unchanged v3.20.0 neural backend.
