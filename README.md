# Sustainable Catalyst Workspace v0.1.0

Workspace is the free public working layer of the Sustainable Catalyst Platform. v0.1.0 establishes the product identity, WordPress shell, browser-local session foundation, cross-product launch surface, health endpoint, and canonical Product Registry integration.

## Public surface

Place `[sc_workspace]` on the WordPress page at `/platform/workspace/`. Use `[sc_workspace_entry]` for a compact Workspace entry card on the Platform page or other product directories.

## Persistence boundary

This release intentionally does **not** create user accounts, server-side projects, cloud persistence, collaboration, uploads, or shared artifacts. The only persisted state is a small browser-local record containing the current session and recently opened tools.

## Product Registry

On activation, the plugin non-destructively adds or updates `sustainable-catalyst-workspace` in `scfs_canonical_product_registry` under `family=commercial` and `console_screen=commercial`, with display order 400. It creates a one-time backup of the pre-change registry. If the registry is not present, registration is marked pending and retried from WordPress administration.

## Shortcodes

- `[sc_workspace]` — full Workspace application shell
- `[sc_workspace_entry]` — compact entry card

## Health

`GET /wp-json/sc-workspace/v1/health`
