# Workspace v2.35.0 — Frontend Logic Reduction & Legacy JS Retirement

Replaces the monolithic primary browser runtime with a thin shell, isolates browser-local project behavior into a lazy compatibility bundle, and retires historical versioned Workspace JS/CSS assets from the active plugin package. Canonical scientific state, authorization, synchronization conflict decisions, handoff validity, provenance, and execution remain backend-owned.

The v2.34 package-check repair is incorporated structurally: active asset names are derived from `SC_WORKSPACE_VERSION`, preventing stale-release filename checks. No database migration is required; migration lineage remains at 031.
