# Workspace v3.9.0 Architecture
## Timeline, Event Reconstruction & Investigative Sequence Workspace

### Purpose
Represent the temporal structure of a complex investigation without converting chronology into causality or association into proof.

### Durable objects
1. **Investigation event heads** — current backend-authoritative event state.
2. **Investigation event revisions** — immutable revision history for titles, descriptions, recorded times, time precision/status, location references, review state, and metadata.
3. **Event–statement links** — immutable, human-asserted links between recorded events and v3.7 claims/findings/hypotheses/questions.
4. **Event relations** — immutable human-asserted temporal relationships such as `precedes`, `follows`, `overlaps`, `contains`, `same-event-as`, and `sequence-related`.
5. **Timeline snapshots** — immutable fingerprints of the timeline, reconstruction graph, and temporal diagnostics.

### Timeline semantics
Timeline ordering is deterministic and based only on recorded `startAt`, then `endAt`, then event ID. Undated events remain visible and are never silently positioned between dated events.

### Temporal diagnostics
Diagnostics identify direct inconsistencies such as an event asserted to precede another event while its recorded start time is later. A diagnostic is a review signal only. It does not resolve the conflict or identify which record is correct.

### Reconstruction graph
The v3.9 graph can overlay v3.8 investigation graph nodes/edges with event nodes, event–statement links, and event-to-event temporal relations. All new relation edges are marked human-asserted.

### Interpretation boundary
Workspace v3.9 does not infer missing events, hidden connections, causal chains, motive, culpability, wrongdoing, preferred hypotheses, preferred narratives, or truth. Those remain matters for human research and documented evidence.
