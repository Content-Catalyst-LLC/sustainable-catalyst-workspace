# Deploy Workspace Backend v2.9.0

Deploy with `deploy_workspace_backend_v2_9_0_vps.sh`. The upgrader inherits the prior Workspace database/service credentials, creates a separate runtime-attestation token when absent, applies migration 009, starts API + worker, and verifies runtime-attestation authentication plus a compliant post-execution attestation smoke path.
