# Workspace v2.28.1 — Interaction Wiring & Functional UI Runtime Repair

## Purpose
Repair the live Workspace interaction layer after the v2.24.1 shell restoration exposed brittle event binding inherited from the older monolithic client runtime.

## Changes
- Align the primary Workspace runtime identity to 2.28.1.
- Replace brittle mandatory root-selector click bindings with null-safe marked bindings.
- Add a delegated fallback for primary navigation, project mode routing, new-project entry, import entry, and object-create entry.
- Add boot/runtime diagnostics through `window.SCWorkspaceInteractionRuntime`.
- Record unhandled client errors and promise rejections without silently hiding them.
- Mark successfully initialized primary action families with `data-scw-bound="1"`.
- Expose `SCWorkspaceInteractionRuntime.audit()` for a visible-control wiring inventory.
- Preserve the full repaired application shell and all v2.28 backend-authoritative visualization functionality.
- No new database migration and no arbitrary-code execution.
