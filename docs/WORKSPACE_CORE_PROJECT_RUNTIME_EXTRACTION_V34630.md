# Workspace v3.46.3.0 — Core Project Runtime Extraction

## Purpose
Move project lifecycle authority out of the compatibility bundle and into canonical host-neutral Workspace application code.

## New canonical runtime
`app/projects/workspace-project-runtime-v34630.js`

The runtime owns:
- project listing
- project creation orchestration
- active-project selection
- project opening and archived-project restoration
- delete-from-device orchestration
- persistence verification
- delete rollback if persistence cannot be verified
- best-effort secondary-reference cleanup
- lifecycle diagnostics

## Project state port
The extracted runtime uses `sc-workspace-project-state-port/1.0`. This separates lifecycle logic from the current browser-local storage implementation.

For v3.46.3.0, the compatibility bundle provides the temporary state/UI port:
- the existing rich project-record factory
- access to current in-memory state
- verified local persistence
- rendering hooks
- Personal Knowledge/reference cleanup
- confirmation and failure notices

The compatibility bundle no longer registers itself as the project lifecycle provider. It creates the canonical project runtime and registers that runtime with the application kernel.

## UI routing
The primary New Project, Open project/Restore, and Delete from this device actions now route through the application kernel.

## Boundaries
- core project runtime has zero WordPress imports
- WordPress is not required for project lifecycle orchestration
- current project schema and browser-local storage format are preserved
- backend authority rules are unchanged
- no database migration

## Next
v3.46.4.0 — Canonical State & Persistence Boundary Decoupling will move the state/persistence boundary itself out of the compatibility runtime.
