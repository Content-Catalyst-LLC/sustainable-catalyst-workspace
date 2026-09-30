# Workspace v3.46.0.1 — Standalone Frontend Runtime & Project Creation Repair

## Purpose
This repair begins the v3.46.x WordPress-decoupling series.

Workspace application boot and project interaction may not be blocked by WordPress script-handle dependencies.
WordPress is treated as a host adapter that supplies configuration, authentication context, embedding, and an optional server-side proxy.

## Repair
- Main Workspace application script has zero hard WordPress script-handle dependencies.
- Frontend runtime identity is v3.46.0.1 rather than the stale v3.43.0 marker.
- A host-neutral `SCWorkspaceConfig` contract is supported.
- WordPress supplies `SCWorkspaceConfig` as an adapter.
- The interaction compatibility runtime is loaded by the application runtime from a host-provided or asset-relative URL.
- This restores New Project and the existing interaction surface for authenticated clean-state users.
- Backend identity advances to v3.46.0.1 with no schema migration and no multilingual/neural behavior change.

## Boundary
The v3.46.0.1 release intentionally keeps the legacy interaction runtime as a temporary continuity layer.
The remaining v3.46.x builds extract projects, notebooks, research, state, transport, and capabilities into standalone application modules.

## Permanent rule introduced
The core Workspace application script must not declare WordPress feature-module handles as required runtime dependencies.
