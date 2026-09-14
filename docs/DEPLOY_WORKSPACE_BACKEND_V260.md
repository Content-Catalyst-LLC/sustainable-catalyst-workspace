# Deploy Workspace Backend v2.6.0

Use `scripts/deploy_workspace_backend_v2_6_0_vps.sh` against the packaged backend ZIP. The script preserves prior credentials, applies migrations 002–006, verifies `sc_workspace` table privileges, restarts the API/worker on the existing loopback port, and performs an exact reproduction smoke test.

The smoke test is bounded: it uses the built-in `workspace.echo` operation and metadata/content-digest comparison. It does not execute arbitrary runtime commands.
