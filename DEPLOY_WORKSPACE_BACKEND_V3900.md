# Deploy Workspace Backend v3.9.0

The deployment script copies the verified v3.8 backend tree to a new v3.9 directory, applies the v3.9 backend overlay, performs dependency-free static validation, builds Docker images while v3.8 remains live, runs an OpenAPI/contract preflight inside the freshly built backend image, applies migration 040 to `sc_workspace`, and then switches Workspace containers.

If a post-switch health or contract gate fails, the script attempts to restore the v3.8 runtime. Migration 040 is additive and is not removed during runtime rollback.

The deployment script deliberately does **not** require host-side `pytest` or host-side FastAPI. This avoids the dependency failure encountered during the v3.8 deployment attempt.
