# Workspace v2.30.0 — Thin Client State Architecture

Workspace v2.30.0 establishes a formal thin-client state boundary. PostgreSQL/Python remain authoritative for canonical Workspace objects and revisions. The browser may persist only an allowlisted transient state envelope for route, selection, panel, draft, filter, viewport, density, optimistic-request, and offline-queue metadata.

Canonical read models are hydrated into an in-memory, discardable cache through `/v1/thin-client-state/bootstrap`. That cache is never written by the v2.30 state runtime to localStorage. Canonical mutations continue through the v2.25 command API, and canonical reads continue through server-generated read models. Guest/local-first compatibility remains available while signed-in backend mode preserves backend authority.

The v2.28.1 interaction repair and v2.29 typed-client proxy boundary are preserved.
