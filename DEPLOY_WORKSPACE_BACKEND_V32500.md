# Deploy Workspace backend v3.25.0

Run `DEPLOY_WORKSPACE_BACKEND_V32500_CONTABO.sh` on Contabo with the v3.25 backend ZIP. The script requires the v3.24.0 production directory as its rollback baseline, builds the backend/worker/neural images, performs hardened pre-switch explainability certification, promotes v3.25.0, runs an end-to-end integrated-gradients job, verifies the separately persisted explainability artifact and receipt lineage, validates OpenAPI/runtime registration, and rechecks container hardening. No database migration is required.
