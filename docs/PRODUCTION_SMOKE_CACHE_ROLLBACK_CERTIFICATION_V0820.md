# Production Smoke, Cache & Rollback Certification — v0.82.0

v0.82.0 stays inside the Workspace Release Candidate feature freeze. It certifies the release package and provides explicit live-production procedures; it does not claim that an undeployed artifact has already passed production.

## Automated package gate

- current WordPress/plugin/runtime version coherence
- single current cumulative JavaScript and CSS asset
- current version-query/cache identity when WordPress query strings are present
- deployment server state and inherited v0.81 deployment hardening
- Release Candidate stage and schema freeze
- bundled v0.81.0 rollback artifact requirement

## Live field certification

The following remain manual until performed against the deployed site: public-page smoke, REST identity, anonymous/authenticated smoke, representative local-project preservation, CDN/browser cache coherence, and a v0.81.0 → v0.82.0 rollback/reinstall rehearsal.

Workspace project storage is application data, not cache. Cache repair must never clear browser-local projects.
