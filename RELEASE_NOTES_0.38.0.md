# Sustainable Catalyst Workspace v0.38.0 — Portable & Synced Notebooks

## Purpose
Make Research Notebooks portable across devices without weakening Workspace's local-first, explicit-action, and conflict-safe boundaries.

## Added
- SHA-256 integrity-checked portable notebook packages.
- Import as a new notebook copy; never overwrite an existing notebook.
- Notebook-specific restore points with restore-as-copy recovery.
- Signed-in, explicit notebook account backup.
- Per-notebook sync enrollment and manual Sync now.
- Server revision preconditions that reject stale writers with HTTP 409.
- Conflict-safe Open cloud as copy and Keep local as sync head actions.
- Notebook portability state inside the project so restore/import/sync lineage travels with normal project persistence.

## Governance
No background notebook synchronization, automatic cloud upload, silent last-write-wins, destructive import, or destructive restore. v0.37 Grounded Notebook Assistance remains reviewable and citation-bound.
