# Workspace v0.4.1 — Identity, Accounts & Persistence Boundary

## Purpose

Introduce a trustworthy identity boundary before hosted persistence is added. Workspace remains fully usable as a guest. WordPress authentication can recognize a signed-in site account, but v0.4.1 does **not** upload, claim, or synchronize Workspace Projects.

## Persistence model

- Storage schema: `5`
- Project schema: `sc-workspace-project/3.1`
- Identity schema: `sc-workspace-identity/1.0`
- Persistence scope: `device`
- Sync state: `local-only`
- Server project storage: disabled
- Cloud sync: disabled
- Manual portability: existing project JSON export/import

Each browser receives a pseudonymous local device ID (`scwd-*`). It contains no user name, email address, WordPress user ID, or project content. Projects carry device-scoped persistence metadata so a future hosted-sync release can migrate ownership explicitly rather than silently changing storage semantics.

## Account behavior

Guest access remains first-class. If the WordPress site already supports accounts, Workspace exposes sign-in and sign-out links that return to Workspace. Registration is shown only when the site-level WordPress registration setting is enabled. The plugin does not enable public registration or create accounts automatically.

Signing in changes the session identity indicator only. It does not change project persistence from device-local to server storage.

## Future boundary

A later release may add an explicit user-mediated flow such as `Claim local projects → upload encrypted/sanitized project payload → server confirmation → synced state`. v0.4.1 intentionally stops before that write boundary.
