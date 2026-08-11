# Workspace v0.68.0 — Performance II: Long Sessions & Very Large Workspaces

v0.68.0 extends the v0.58 scale/performance foundation into long-running browser sessions and high-volume Workspace use without changing canonical storage.

## Runtime hardening

- Bounded in-memory samples: at most 120 recent observations per metric.
- Route-transition and full-render counters for repeated-session pressure.
- Derived Integrated Knowledge timing through the existing revision-aware cache.
- Optional Long Tasks API observation where the browser supports it.
- Optional JS heap pressure signal where the browser exposes `performance.memory`; absence is normal and not treated as failure.
- Cooperative chunk-yield and bounded-window utilities for large derived operations.
- Explicit reset of session counters and derived caches without canonical mutation.
- Exportable timing-only performance report using the existing browser-compatibility download adapter.

## Privacy boundary

The performance report does not contain project/object content, research queries, source URLs, or device identifiers. Samples are memory-only, are not stored in localStorage, and are never uploaded automatically.

## Governance boundary

Performance advice does not delete, archive, compact, migrate, or otherwise rewrite canonical research. Storage remains 35 and Project remains `sc-workspace-project/20.0`.

## Manual field validation

Automated fixtures validate bounded sampling, thresholds, retry-free reset, memoization, cooperative yields, and existing Chromium reflow matrices. Production field testing should still include multi-hour sessions and representative very-large projects on Safari, Chrome/Edge, and Firefox-class browsers.
