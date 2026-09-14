# Deploy Workspace Backend v2.7.0

Use `scripts/deploy_workspace_backend_v2_7_0_vps.sh` with the v2.7.0 backend ZIP.

The installer:

1. reuses the newest existing Workspace backend `.env` beginning with v2.6.0;
2. preserves the `sc-workspace-data` external volume;
3. reapplies additive migrations 002–006 and applies migration 007;
4. verifies PostgreSQL privileges for reproduction execution plans and runtime handoff receipts;
5. starts the v2.7 API and worker on the established Workspace runtime;
6. verifies health, readiness, capabilities, and worker heartbeat;
7. builds an original deterministic run and output;
8. creates a v2.6 reproduction plan and a second planned run;
9. creates a v2.7 frozen reproduction execution plan and proves it is not automatically dispatched;
10. performs an explicit human-authorized controlled runtime handoff;
11. waits for the worker and registers the reproduced output;
12. requires an `exact` reproduction verification receipt.

No service token is printed by the script.
