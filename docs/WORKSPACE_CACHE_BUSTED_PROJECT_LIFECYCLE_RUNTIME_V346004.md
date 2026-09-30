# Workspace v3.46.0.4 — Cache-Busted Project Lifecycle Runtime Repair

## Cause
The v3.46.0.3 project-deletion repair lived in `sc-workspace-local-project-compat-v3000.js`, but the standalone shell dynamically requested that compatibility runtime from a stable, unversioned URL. Browser, shared-host, reverse-proxy, or CDN caching could therefore serve a pre-repair copy even while the v3.46.0.3 package was installed.

## Repair
- release-specific lifecycle runtime: `sc-workspace-local-project-compat-v346004.js`
- interaction runtime identity advances to `3.46.0.4`
- WordPress host config includes `?ver=3.46.0.4`
- standalone shell independently enforces the `ver` query
- shell rejects/replaces a stale compatibility script whose URL/release marker does not match
- deployment package guard requires the v3.46.0.4 lifecycle runtime and a minimum byte threshold
- v3.46.0.3 project-deletion semantics are preserved unchanged
- no database migration
- backend identity advances for release alignment only
