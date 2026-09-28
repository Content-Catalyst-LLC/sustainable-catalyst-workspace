# Deploy Workspace Backend v3.29.0

Base deployment is CPU-safe and rolls back to v3.28.0 on post-switch verification failure. Run `DEPLOY_WORKSPACE_BACKEND_V32900_CONTABO.sh` against the v3.29 backend ZIP. GPU exposure is optional and separate; only use `ENABLE_WORKSPACE_NEURAL_GPU_V32900_CONTABO.sh` on a host with NVIDIA container support and a visible GPU.
