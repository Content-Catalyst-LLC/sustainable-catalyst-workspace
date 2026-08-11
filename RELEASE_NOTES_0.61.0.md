# Sustainable Catalyst Workspace v0.61.0 — Product Hardening I: Browser, Recovery & Field-Use Resilience

## Purpose
Harden the v0.60 Public Product Beta II experience for real browser sessions, reloads, navigation history, stale UI state, and recoverable field-use failures.

## Added
- Review → Reliability surface.
- Safe session-local route restoration.
- Browser back/forward route handling through the History API when available.
- Stale/invalid saved UI-state sanitization with safe fallback to Start.
- Recovery-state classification across current state, last-known-good state, quarantine envelope, and restore points.
- Actionable capability findings for local/session storage, history, file APIs, integrity support, and route isolation.
- Navigation-only reset that cannot delete canonical research.
- Privacy-minimized resilience snapshot export.
- Duplicate Workspace hero deck removed.

## Governance
No schema migration. No automatic repair, upload, deletion, telemetry, or canonical mutation. Route state stores only view/surface names and release/timestamp metadata in sessionStorage.

## Retained
- v0.59.1 focused application shell and one-surface Research experience.
- v0.60 Public Product Beta II readiness gate.
- 4px editorial header rule.
