# Workspace v0.58.0 — Scale, Performance & Large-Project Hardening

v0.58.0 hardens Workspace for substantially larger local research corpora without changing Project 20.0, Project Export 20.0, Storage 35, or Notebook Workspace 8.0.

## Performance architecture

- The Integrated Knowledge corpus remains derived from canonical project and notebook records.
- A signature-based in-memory cache reuses the derived index when canonical project revision inputs have not changed.
- Integrated Knowledge renders an initial 120-result DOM window. Users may explicitly load additional 120-record windows, capped at 600 rendered result cards per view.
- Search and metrics continue to operate across the complete derived result set; the render window limits DOM materialization, not retrieval scope.
- Review → Performance exposes project/object/notebook-block/index counts, serialized Workspace size, browser storage estimates when available, index-build timing, cache hit/miss state, and advisory scale signals.

## Advisory budgets

Budgets are operational warning boundaries rather than storage quotas. Crossing one never deletes, archives, compacts, migrates, or rewrites research.

## Stress validation

The scale helper can construct deterministic synthetic projects with large object and notebook-block counts so index derivation, counting, bounded rendering, and pressure classification can be regression tested without relying on user data.

## Governance

Performance mechanisms may clear or rebuild derived caches. They do not mutate canonical Sources, Evidence, Datasets, Analysis, Decisions, Documents, Notebook content, citations, tasks, collaboration records, or institutional packages.
