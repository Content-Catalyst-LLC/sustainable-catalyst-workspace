# Workspace v1.10.0 — Workspace Automation & Research Operations

This release productionizes the existing browser-local Research Automation Framework into an explicit Research Operations layer. Operations can describe saved-search refresh, source-update review, watchlist review, research-queue review, citation verification, provenance review, evidence refresh, and project maintenance.

Schedules are declarations, not a daemon. Workspace calculates due state deterministically, exposes blocked targets, and executes an operation only when the user explicitly chooses Run now or Run due operations. External freshness checks remain user initiated; no background network request is made.

Each run is a reviewable draft and can emit a metadata-only SHA-256 receipt. Receipts contain identifiers, timestamps, operation type, outcome, and counts—not project content, query text, or source URLs.

The legacy Research Automation library is retained for backward compatibility and can be imported explicitly. There is no automatic migration.
