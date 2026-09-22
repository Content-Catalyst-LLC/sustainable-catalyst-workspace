# Workspace v3.9.0 — Timeline, Event Reconstruction & Investigative Sequence Workspace

Workspace v3.9.0 extends the v3.8 investigation graph with a backend-authoritative temporal reconstruction layer.

## Added
- versioned investigation events with explicit time precision/status
- immutable event-to-statement links
- immutable human-asserted event-to-event temporal relations
- deterministic timeline ordering of recorded events
- reconstruction graph overlay on the v3.8 investigation graph
- temporal consistency diagnostics for direct conflicts between recorded timestamps and asserted temporal relations
- immutable timeline/reconstruction snapshots
- unified research context projection
- WordPress timeline adapter and v3.9 typed-client contract

## Epistemic boundary
The runtime does not fill gaps, infer hidden events, infer causality, infer motive or culpability, choose a preferred narrative, determine truth, or rank evidence. Temporal diagnostics only compare explicitly recorded timestamps with explicitly asserted temporal relationships.

Migration: `040_timeline_event_reconstruction_investigative_sequence_workspace.sql`

Rollback runtime baseline: v3.8.0. Migration 040 is additive and may remain in the database during runtime rollback.
