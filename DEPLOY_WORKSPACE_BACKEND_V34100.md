# Deploy Workspace Backend v3.41.0

Requires production baseline `/opt/sustainable-catalyst/sustainable-catalyst-workspace-backend-v3.40.0`. The deployer builds the neural/backend/worker images, certifies distributed worker contracts, deterministic sharding/dispatch, lease/heartbeat state, retry/failover, and execution receipts before switching production. Post-switch it executes a real worker-pool job, verifies Workspace artifact persistence and the 117-operation registry, then checks container hardening.
