# Sustainable Catalyst Workspace v0.50.0 — Workspace Experience Consolidation

Released: 2026-08-10

## Purpose

v0.50.0 consolidates the accumulated Workspace capabilities into a more coherent product experience without changing Storage 35, Project 20.0, Project Export 20.0, or Notebook Workspace 8.0.

## Added

- Browser-local **Comfortable / Compact** density preference.
- Workspace **command palette** opened with `Ctrl/Meta + K`.
- Primary-area keyboard navigation with `Alt + 1…5`.
- `/` shortcut to focus search in the currently visible Workspace view when a search field exists.
- A concise **Workspace Help / terminology** surface explaining Project, Research, Notebook, Knowledge, Review, and Exchange.
- Responsive horizontal primary navigation on small screens rather than a long five-row navigation stack.
- Minimum 44px primary navigation and Workspace button targets.
- Screen-reader status updates for route changes.
- Consistent compact empty-state/readability treatment.
- Internal Notebook top-rule normalization to the established 4px editorial grammar.

## Retained

- Five primary areas: Start, Projects, Research, Review, Exchange.
- v0.49 Research Templates & Reusable Workflows.
- v0.48 Cross-Project Knowledge.
- v0.47 Research Graph & Relationship Explorer.
- v0.46 Interchange and the v0.46.1 **4px editorial header rule** correction.
- All Notebook, provenance, review, sync, citation, composition, retrieval, collection, collaboration, and handoff behavior.

## Governance

Experience preferences are browser-local presentation settings. Commands only activate existing Workspace routes or focus an existing search control. v0.50.0 does not automatically create projects, mutate canonical records, invoke AI, upload data, or introduce background work.

## Schema boundary

- Storage: **35 → 35**
- Project: **20.0 → 20.0**
- Project Export: **20.0 → 20.0**
- Notebook Workspace: **8.0 → 8.0**
- Experience: **sc-workspace-experience/1.0**
- Experience Preferences: **sc-workspace-experience-preferences/1.0**
