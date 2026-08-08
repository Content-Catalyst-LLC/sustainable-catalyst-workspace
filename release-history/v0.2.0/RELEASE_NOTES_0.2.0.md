# Sustainable Catalyst Workspace v0.2.0

## Projects & Persistent Work

v0.2.0 turns Workspace from a launch surface into a persistent local working environment. A Workspace Project is now the durable container for a user's problem, notes, status, activity, and movement across Sustainable Catalyst.

### Delivered

- Create, open, rename, describe, pin, duplicate, archive, restore, and delete Workspace Projects.
- Device-local persistence with explicit **Saved on this device** disclosure.
- Autosave for project metadata and notes.
- Active, Paused, and Complete project states.
- Stable project identifiers independent of project titles.
- Project activity history for creation, status changes, tool handoffs, imports, exports, archive/restore, and duplication.
- JSON project export and controlled JSON import.
- Local-state migration from the v0.1.0 session key into the v0.2.0 project model.
- Corrupted-state quarantine and safe recovery instead of silently discarding unreadable browser data.
- Active-project handoff contract for Sustainable Catalyst tools using only the stable project ID in URL parameters; project titles, descriptions, and notes remain local.
- Public project-contract REST endpoint alongside the existing health endpoint.
- Product Registry update from 0.1.0 to 0.2.0 while preserving the canonical ID, Commercial Release family, free access model, and experimental lifecycle.

### Persistence boundary

v0.2.0 is local-first. Projects are stored only in the current browser unless the user explicitly exports a project JSON file. There is no Sustainable Catalyst account, cloud project database, cross-device synchronization, or collaboration service in this release.

### Compatibility

- `[sc_workspace]` remains the primary Workspace shortcode.
- `[sc_workspace_entry]` remains the compact Platform entry shortcode.
- `/platform/workspace/` remains the canonical public route.
- `/wp-json/sc-workspace/v1/health` remains public and read-only.
- v0.1.0 browser-local session state is migrated when possible.
- The canonical Product Registry record remains `sustainable-catalyst-workspace` at Commercial Release display order 400.
