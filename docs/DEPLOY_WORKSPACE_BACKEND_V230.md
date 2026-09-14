# Deploy Workspace Backend v2.3.0

v2.3.0 upgrades a running v2.2.0 backend. It preserves the PostgreSQL credentials, service token, and `sc-workspace-data` volume, then adds a separate worker container.

Use `scripts/deploy_workspace_backend_v2_3_0_vps.sh` with the v2.3.0 backend ZIP.

After deployment verify:

- `GET /health` returns version `2.3.0`, `backgroundJobs: true`, and `computeOrchestration: true`.
- `GET /ready` returns HTTP 200.
- authenticated `GET /v1/worker/status` shows a v2.3.0 worker heartbeat.
- authenticated `GET /v1/orchestration/routes` exposes named routes without exposing service credentials or URLs.
- the deployment smoke job `workspace.echo` reaches `succeeded`.

Cross-product route environment variables are optional and may be added later. Unconfigured targets are reported as blocked rather than guessed.
