# Workspace v3.46.9.0 — Standalone Runtime Production Certification

## Purpose
Turn the standalone Workspace from an independently bootable architecture into a release with explicit production-certification gates.

## Certification layers

### Static distribution certification
`build/certify_workspace_standalone_v34690.py`

A copy ships as:
`standalone/certify.py`

It certifies:
- standalone runtime-manifest identity;
- complete generated assets;
- SHA-256 integrity for every generated asset;
- absence of WordPress runtime coupling;
- manifest-driven boot;
- local static HTTP serving;
- direct-backend configuration.

### Runtime certification
`app/standalone/workspace-standalone-production-certification-v34690.js`

The runtime certification verifies:
- standalone kernel boot;
- WordPress not required;
- direct transport;
- module-registry failure isolation;
- verified persistence;
- canonical state ownership;
- project create/open/delete lifecycle;
- restoration of pre-certification project count.

### Optional live deployment certification
After the v3.46.9.0 backend is deployed:

```bash
cd standalone
python3 certify.py --backend-url https://workspace-api.sustainablecatalyst.com
```

This adds `WORKSPACE_STANDALONE_LIVE_BACKEND_HEALTH` and requires the public backend to report version 3.46.9.0.

## Production report
`standalone/production-certification-v34690.json`

This report captures deterministic package-level certification. Live backend reachability remains optional at build time so release creation is not coupled to external network availability.

## Safety
- database migration: none
- browser-storage schema migration: none
- previous/rollback release: 3.46.8.0

## Next
v3.46.10.0 — Decoupled Workspace Production Baseline.
