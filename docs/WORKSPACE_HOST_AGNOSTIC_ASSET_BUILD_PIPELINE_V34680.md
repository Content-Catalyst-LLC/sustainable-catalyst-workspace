# Workspace v3.46.8.0 — Host-Agnostic Asset & Build Pipeline

## Purpose
Make Workspace host distributions generated products of one canonical application source tree instead of separately maintained runtime asset sets.

## Canonical build manifest
`build/workspace-runtime-assets-v34680.json`

Each runtime asset declares:
- logical asset ID
- canonical source path
- host targets
- load order
- whether it is shared across hosts
- whether it autoloads at runtime

## Deterministic generator
`build/build_workspace_assets_v34680.py`

The generator:
1. reads the canonical asset manifest;
2. copies canonical sources into WordPress and standalone distributions;
3. computes SHA-256 for every generated runtime asset;
4. emits a JSON runtime manifest for each host;
5. emits a JavaScript runtime-manifest bootstrap for each host;
6. verifies checksum parity for assets declared shared;
7. supports `--check` to fail on generated-asset drift.

## WordPress
WordPress still enqueues only the thin adapter.

The PHP bridge no longer enumerates:
- application kernel URL
- module registry URL
- persistence/state/project runtime URLs
- transport/auth/API runtime URLs
- WordPress transport/auth/host adapter URLs
- compatibility runtime URL
- application entry-point URL

It supplies:
- runtime asset-manifest URL
- asset base
- REST proxy/auth/identity metadata

The thin adapter loads the generated manifest, resolves `application.entry`, and hands boot to the host-neutral application entry.

## Standalone
`standalone/bootstrap.js` no longer contains a hard-coded runtime file list. It loads the generated standalone manifest and walks its declared `loadOrder`.

## Shared asset parity
Shared runtime modules must have identical SHA-256 hashes in WordPress and standalone generated outputs.

## Safety
- database migration: none
- browser-storage schema migration: none
- previous/rollback release: 3.46.7.0

## Next
v3.46.9.0 — Standalone Runtime Production Certification.
