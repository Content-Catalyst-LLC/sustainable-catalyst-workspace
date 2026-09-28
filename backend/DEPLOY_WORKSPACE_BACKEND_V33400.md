# Deploy Workspace backend v3.34.0

Deploy only after v3.33.0 is the verified production baseline. Upload the packaged `sustainable-catalyst-workspace-backend-v3.34.0.zip` and `DEPLOY_WORKSPACE_BACKEND_V33400_CONTABO.sh` to `/tmp`, then run the deployment script. The deployer builds backend/worker/neural images, performs pre-switch training certification, switches production, submits an end-to-end training job, verifies governed artifact lineage and the 62-operation registry, checks container hardening, and automatically rolls back to v3.33.0 if post-switch verification fails.
