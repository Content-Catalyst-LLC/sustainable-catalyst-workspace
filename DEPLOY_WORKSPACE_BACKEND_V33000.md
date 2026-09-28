# Deploy Workspace Backend v3.30.0

Prerequisite: production Workspace v3.29.0 at `/opt/sustainable-catalyst/sustainable-catalyst-workspace-backend-v3.29.0` with its `.env` file.

Run `DEPLOY_WORKSPACE_BACKEND_V33000_CONTABO.sh /tmp/sustainable-catalyst-workspace-backend-v3.30.0.zip` on Contabo. The deployer builds backend/worker/neural images, runs pre-switch bounded grid-search certification, promotes v3.30.0, submits a real Workspace hyperparameter-grid job, verifies the separately persisted search artifact and execution receipt, checks the 44-operation runtime registry, and re-checks numeric-UID/read-only container hardening. Genuine post-switch failure restores v3.29.0.
