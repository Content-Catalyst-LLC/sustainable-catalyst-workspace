# Workspace v3.46.7.0 — WordPress Thin Adapter

## Purpose
Reduce WordPress from an application orchestrator to a host adapter.

## Before v3.46.7.0
`SC_Workspace::enqueue_assets()` directly enumerated a large historical Workspace JavaScript graph. WordPress therefore remained responsible for module ordering even after the application kernel, transport, state store, persistence runtime, project runtime, and module registry had been extracted.

## v3.46.7.0 boundary
WordPress now performs only four frontend-host responsibilities:

1. enqueue the current Workspace stylesheet;
2. enqueue one thin adapter JavaScript file;
3. localize one bridge object containing host configuration and identity/auth metadata;
4. continue exposing the WordPress REST proxy and existing server-side routes.

The thin adapter constructs `SCWorkspaceConfig` and `SCWorkspaceIdentity`, then loads the host-neutral Workspace entry point.

## New canonical adapter
`adapters/wordpress/workspace-wordpress-thin-adapter-v34670.js`

Mirrored deployment asset:
`wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-wordpress-thin-adapter-v34670.js`

## WordPress no longer owns
- application module enumeration
- application module ordering
- canonical project lifecycle
- canonical state ownership
- persistence transactions
- module-registry behavior
- application-kernel boot logic

## Compatibility
The existing shortcode markup remains in v3.46.7.0 to preserve the current WordPress interface while UI rendering continues to migrate toward host-neutral application surfaces.

Historical JavaScript files are retained in the plugin package for rollback and future registry migration. They are no longer directly enqueued by the PHP boot path.

## Safety
- database migration: none
- browser-storage schema migration: none
- previous/rollback release: 3.46.6.0
- standalone web shell remains intact

## Next
v3.46.8.0 — Host-Agnostic Asset & Build Pipeline.
