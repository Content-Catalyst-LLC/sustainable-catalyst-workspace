# Deploy Workspace Backend v2.22.0

Deploy the backend ZIP on the VPS with `deploy_workspace_backend_v2_22_0_vps.sh`. The script preserves the prior environment, applies migrations through 022, rebuilds the internal runtime fabric, validates health, runs inherited runtime smoke tests, executes a durable minimax-regret decision job, verifies its receipt, and checks the decision runtime sandbox.
