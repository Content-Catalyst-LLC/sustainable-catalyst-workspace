# Sustainable Catalyst Workspace v0.68.0

## Performance II: Long Sessions & Very Large Workspaces

v0.68.0 extends the earlier scale/performance foundation into long-running browser sessions and high-volume Workspace use. It is a performance-hardening release only: Storage remains 35, Project remains `sc-workspace-project/20.0`, Project Export remains `sc-workspace-project-export/20.0`, and no canonical migration is performed.

### Long-session runtime hardening

- Adds a bounded, memory-only session monitor for route transitions, full Workspace renders, Integrated Knowledge derivation timing, optional browser Long Tasks observations, cooperative-yield counts, and optional non-portable heap-pressure signals.
- Keeps at most 120 recent observations per metric so diagnostic history cannot grow without bound during a long session.
- Treats the browser Long Tasks API and `performance.memory` as optional capabilities; absence is not an error.
- Adds explicit advisory thresholds for render, derived-index, route-volume, session-duration, and heap pressure.
- Adds a reset action that clears transient timing counters and derived caches without changing canonical Workspace data.
- Adds a privacy-minimized timing/counter report export. Project/object content, source URLs, queries, and device identifiers are excluded.

### Very-large-workspace behavior

- Consolidates Integrated Knowledge callers around the existing revision-aware derived cache so Research Tasks, Grounded Research, composition attachment, and grounded-request preparation do not independently rebuild the same stable index.
- Adds bounded-window utilities for high-volume derived lists.
- Adds cooperative chunk-yield primitives that can yield to the browser between bounded chunks of large derived work.
- Keeps performance advice non-destructive: no automatic deletion, archival, compaction, migration, or canonical mutation is introduced.

### Review surface and contract

- Extends Review → Performance with a long-session profile showing session age, route changes, render count/p95, derived-index p95, observed long tasks, cooperative yields, and optional heap pressure.
- Adds `/wp-json/sc-workspace/v1/long-session-performance-contract`.
- Adds schemas for the long-session performance contract, performance session, and exported performance session report.

### Preserved hardening

v0.68.0 retains the v0.67 cross-device continuity safeguards, v0.66.1 WordPress header-window repair, v0.66 import/export compatibility hardening, v0.65 field-use behavior, v0.64.1 accessibility/layout recovery, v0.63 browser compatibility fallbacks, and v0.62 persistence/recovery integrity protections.

### Validation boundary

Automated tests exercise bounded 50,000-item windowing, a 5,000-item cooperatively chunked operation, simulated long-session thresholds, large-project fixtures, and the inherited Chromium layout matrices. They do not substitute for a real multi-hour production session on representative large projects and physical Safari/Chrome/Edge/Firefox-class environments.
