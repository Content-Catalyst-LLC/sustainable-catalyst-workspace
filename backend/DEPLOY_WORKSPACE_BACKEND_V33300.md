# Deploy Workspace backend v3.33.0 on Contabo

v3.33.0 is an upgrade-in-place release and requires the verified v3.32.0 backend at:

`/opt/sustainable-catalyst/sustainable-catalyst-workspace-backend-v3.32.0`

The included deployer accepts either:

1. `sustainable-catalyst-workspace-backend-v3.33.0-upgrade.zip` (included in this release), or
2. a full `sustainable-catalyst-workspace-backend-v3.33.0.zip` generated after applying the release to the local repository.

The deployer copies the v3.32.0 `.env`, builds the neural/backend/worker images, runs pre-switch GNN certification inside the neural container, switches production containers, verifies `/health`, executes an end-to-end GNN forward job, confirms the dedicated GNN artifact and receipt lineage, checks runtime registry integrity, and verifies container hardening. On a post-switch error it restores v3.32.0.

No database migration is required.
