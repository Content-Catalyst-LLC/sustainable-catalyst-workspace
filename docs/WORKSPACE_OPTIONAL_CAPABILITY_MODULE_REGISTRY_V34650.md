# Workspace v3.46.5.0 — Optional Capability & Module Registry

## Purpose
Introduce the canonical host-neutral module system required to continue separating Workspace from the WordPress plugin shell.

## New canonical module
`app/core/workspace-module-registry-v34650.js`

The registry provides:
- module manifests
- required vs. optional modules
- enable/disable lifecycle
- dependency-aware loading
- capability advertisement and resolution
- preloaded/core-module registration
- isolated optional-module failures
- blocked/degraded/failed states
- required-module failure propagation
- registry diagnostics and issue history

## Failure policy
Required module failure may stop application boot.

Optional module failure is contained in the registry. It cannot take down the core Workspace application. A dependent optional module becomes blocked when its dependency is unavailable.

## Current core registrations
The frontend registers already-created host, transport, authentication, and API services as ready core modules. Once the compatibility runtime constructs canonical persistence, state-store, and project-runtime services, it registers those services as ready core modules as well.

## Incremental migration
v3.46.5.0 does not force all legacy Workspace feature scripts into the registry at once. WordPress currently supplies an empty `optionalModules` declaration. Later builds can migrate capabilities module-by-module while retaining a stable application kernel.

## Boundaries
- registry contains zero WordPress APIs or globals
- WordPress is not required for module registration or capability resolution
- optional module failure does not block boot
- no database migration
- no storage-schema migration

## Next
v3.46.6.0 — Standalone Web Application Shell.
