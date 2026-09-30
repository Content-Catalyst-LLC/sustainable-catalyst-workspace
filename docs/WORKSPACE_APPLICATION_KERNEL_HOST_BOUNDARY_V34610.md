# Workspace v3.46.1.0 — Workspace Application Kernel & Host Boundary

## Purpose
Begin the structural separation of Workspace from WordPress without disturbing the verified v3.46.0.4 local project lifecycle.

## Architecture
- `app/core/workspace-host-adapter-contract-v1.js` defines the host-neutral adapter contract.
- `app/core/workspace-application-kernel-v34610.js` owns boot, capability registration, lifecycle routing, and kernel diagnostics.
- `adapters/wordpress/workspace-wordpress-host-adapter-v34610.js` implements the host contract for the current WordPress host.
- WordPress ships mirrored browser assets, but the canonical core sources live outside `wordpress/`.
- The existing verified project runtime registers itself as a temporary project-lifecycle provider. Its project create/open/delete implementation remains authoritative for this transition build.

## Boundary
The application kernel has no WordPress imports, constants, functions, handles, or assumptions. WordPress may host assets and provide authentication/transport configuration, but it is not required for kernel boot or project-lifecycle routing.

## Certification
- standalone kernel boot
- standalone create/open/delete routing using an in-memory lifecycle provider
- zero WordPress imports in core
- zero WordPress script-handle dependencies for the main Workspace shell
- host adapter contract validation
- WordPress adapter isolated under `adapters/wordpress`
- backend version alignment with no database migration

## Next
v3.46.2.0 will decouple transport/authentication/API adapters. v3.46.3.0 will extract the project runtime itself from the compatibility bundle.
