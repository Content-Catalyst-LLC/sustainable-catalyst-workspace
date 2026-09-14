# Deploy Workspace Backend v2.4.0

v2.4.0 is an additive upgrade of the Workspace FastAPI/PostgreSQL backend. It preserves the existing database, service token, object-storage Docker volume, and server-configured cross-product route variables.

The deployment helper:

1. reuses the newest available v2.3.0/v2.2.0/v2.1.0 `.env`,
2. applies additive migrations 002, 003, and 004 idempotently,
3. rebuilds the API and worker,
4. validates health/readiness/capabilities,
5. waits for a v2.4.0 worker heartbeat,
6. creates a smoke dataset, model, parameter set, and revision-frozen execution run under an isolated numeric smoke identity,
7. links a durable `workspace.echo` job to the run,
8. verifies worker-driven run completion, and
9. registers an output and verifies the reproducibility fingerprint changes.

Run on the VPS after uploading the backend ZIP:

```bash
cd /tmp
rm -rf sc-workspace-v2.4.0-deploy
mkdir -p sc-workspace-v2.4.0-deploy
unzip -q sustainable-catalyst-workspace-backend-v2.4.0.zip -d sc-workspace-v2.4.0-deploy
cd sc-workspace-v2.4.0-deploy/sustainable-catalyst-workspace-backend-v2.4.0
chmod +x deploy_workspace_backend_v2_4_0_vps.sh
./deploy_workspace_backend_v2_4_0_vps.sh /tmp/sustainable-catalyst-workspace-backend-v2.4.0.zip
```

The backend remains loopback-bound at `127.0.0.1:8094`; continue using the existing protected reverse-proxy/WordPress bridge rather than exposing that port directly.
